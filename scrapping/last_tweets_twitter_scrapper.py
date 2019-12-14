from selenium.webdriver.support import expected_conditions as EC
from infrastructure import PostgreSqlConnectionManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from scrapping.scrapper import Scrapper
from selenium import webdriver
import pandas as pd


class LastTweetsTwitterScrapper(Scrapper):
    GECKO_DRIVER_PATH = '/usr/local/bin/webdriver/gecko/geckodriver'
    SECONDS_OF_WAITING_FOR_NEW_TWEETS: int = 10

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
            executable_path=self.GECKO_DRIVER_PATH
        )

        # Go into the website
        driver.get(self.__endpoint)

        # Waiting for new tweets and extracting them when are available
        while True:
            try:
                wait = WebDriverWait(
                    driver,
                    self.SECONDS_OF_WAITING_FOR_NEW_TWEETS
                )

                wait.until(lambda driver: EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'new-tweets-bar')
                    )
                )

                if EC.element_to_be_clickable((By.CLASS_NAME, 'new-tweets-bar')):
                    tweets = self.process(driver)
                    df = pd.DataFrame(tweets)

                    group_length: int = len(tweets)
                    msg: str = "[LH] GROUP CONSUMED OF LENGTH: {}".format(
                        group_length
                    )
                    print(msg)

                    self.__pscm.write_dataframe_to_schema_table(
                        df,
                        'twitter',
                        'tweet_staging'
                    )

                    sql = """
                        INSERT INTO twitter.tweet (tweet_id, username, tweet)
                            SELECT tweet_id, username, tweet
                            FROM twitter.tweet_staging
                        ON CONFLICT (tweet_id) DO UPDATE 
                        SET
                            tweet = excluded.tweet,
                            username = excluded.username;
                    """

                    self.__pscm.execute_statement(sql)

                    group_length: int = len(tweets)
                    msg: str = "[LH] GROUP PERSISTED OF LENGTH: {}".format(
                        group_length
                    )

                    print(msg)
            except Exception as ex:
                pass

    @staticmethod
    def process(driver: webdriver.Firefox):
        btn = driver\
            .find_element_by_class_name('new-tweets-bar')

        if btn:
            new_results: str = btn.text
            no_new_results: int = int(new_results.split(' ')[0])

            # Generating new tweets
            btn.click()

            # Fetching new tweets
            tweet_boxes = driver.find_elements_by_class_name('tweet')

            tws = []
            for tb in tweet_boxes[:no_new_results]:
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

                tw: {} = {
                    'tweet_id': int(tweet_id),
                    'username': tweet_header,
                    'tweet': tweet_body
                }

                tws.append(tw)

            return tws
