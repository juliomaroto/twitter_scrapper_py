# Twitter Scrapper

## Disclaimer

This project has been created for educational purposes and it is distributed under
a public GNU License. This a non-lucrative project that aims to share the power
of having access to the data and democratizing it.

Please, use it honestly.

## About

This project files and implementation of twitter scrapper anonymous service
using selenium as browser engine. This project works by default on MacOS
using GECKO driver (Firefox).


## Installation

```
$ cd [PROJECT_DIR]
$ pip3 install -r requirements.txt
```
### Dependencies

    selenium==3.141.0
    pandas==0.25.3
    psycopg2-binary==2.8.4
    PyYAML==5.2

## Usage
### Configuration

Configure a PostgreSQL origin and configure the scheduling within the 
two available scrappers. Historical is for retrieving historical data and
recent is for waiting for last available news.
```
database:
    host: localhost
    dbname: postgres
    user: postgres
    password: passwd

robots:
    pararellized: true
    scheduling:
        historical:
            enabled: true
            scrapper_name: "historical_tweets_twitter_scrapper"
            feed_endpoint: "https://twitter.com/search?vertical=news&q=%40realdonaldtrump&l=en&src=rela"

        recent:
            enabled: true
            scrapper_name: "last_tweets_twitter_scrapper"
            feed_endpoint: "https://twitter.com/search?f=tweets&vertical=news&q=%40realdonaldtrump&l=en&src=rela"
```

## PR friendly
Despite of the project is licensed under GNU Public license Version 3, you can
fork it whenever you want following the GNU license requirements, in order to contribute to the project
you can send a pull request and it is likely your propossed changes will be included
on it.