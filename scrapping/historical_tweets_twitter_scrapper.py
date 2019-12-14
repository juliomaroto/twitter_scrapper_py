from selenium.common.exceptions import TimeoutException
from infrastructure import PostgreSqlConnectionManager
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import pandas as pd
import time

from scrapping.scrapper import Scrapper


class HistoricalTweetsTwitterScrapper(Scrapper):
    __GECKO_DRIVER_PATH = '/usr/local/bin/webdriver/gecko/geckodriver'
    __SCROLL_PAUSE_TIME = 2

    def __init__(self, config: {}):
        db_config: {} = config.get('database_config')
        self.__pscm: PostgreSqlConnectionManager = PostgreSqlConnectionManager(
            {
                'host': db_config.get('host'),
                'dbname': db_config.get('dbname'),
                'user': db_config.get('user'),
                'password': db_config.get('password')
            })
        self.__endpoint = config.get('feed_endpoint')

    def run(self):
        # create a new Firefox session
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(
            options=options,
            executable_path=self.__GECKO_DRIVER_PATH
        )

        # Go into the website
        driver.get(self.__endpoint)

        # Calculate initial height
        last_height = driver.execute_script(
            "return document.body.scrollHeight")

        last_tws: int = 0
        # Waiting for new tweets and extracting them when are available
        while True:
            try:
                tweets = self.process(driver, last_tws)
                df = pd.DataFrame(tweets)

                group_length: int = len(tweets)
                print("[HST] GROUP CONSUMED OF LENGTH: {}".format(group_length))

                if not df.empty:
                    last_tws = last_tws + len(tweets)

                    self.__pscm.write_dataframe_to_schema_table(
                        df,
                        'twitter',
                        'tweet_staging_hst'
                    )

                    sql = """
                        INSERT INTO twitter.tweet (tweet_id, username, tweet)
                            SELECT tweet_id, username, tweet
                            FROM twitter.tweet_staging_hst
                        ON CONFLICT (tweet_id) DO UPDATE 
                        SET
                            tweet = excluded.tweet,
                            username = excluded.username;
                    """

                    self.__pscm.execute_statement(sql)

                    group_length: int = len(tweets)
                    print("[HST] GROUP PERSISTED OF LENGTH: {}".format(group_length))

                    # Scroll down to bottom
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight)")

                    # Wait to load page
                    time.sleep(self.__SCROLL_PAUSE_TIME)

                    # Calculate new scroll height and compare with last scroll
                    # height
                    new_height = driver.execute_script(
                        "return document.body.scrollHeight")

                    # break condition
                    if new_height == last_height:
                        # Wait to load page
                        time.sleep(self.__SCROLL_PAUSE_TIME)
                    last_height = new_height
            except TimeoutException as ex:
                pass

    @staticmethod
    def process(driver: webdriver.Firefox, last_tweet_number: int):
        # Fetching new tweets
        tweet_boxes = driver.find_elements_by_class_name('tweet')

        tws = []
        for tb in tweet_boxes[last_tweet_number:]:
            tweet_id = tb.get_attribute('data-tweet-id')
            tweet_content = tb.find_element_by_class_name('content')

            tweet_header = tweet_content \
                .find_element_by_class_name('stream-item-header') \
                .find_element_by_class_name('account-group') \
                .find_element_by_class_name('username') \
                .find_element_by_tag_name('b').text

            tweet_body = tweet_content \
                .find_element_by_class_name('js-tweet-text-container') \
                .find_element_by_tag_name('p').text

            tweet_text = tweet_body.replace('\n', '')

            tw: {} = {
                'tweet_id': int(tweet_id),
                'username': tweet_header,
                'tweet': tweet_text
            }

            tws.append(tw)

        return tws
