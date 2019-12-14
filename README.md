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

**You need to have installed PostgreSQL as far as currently there is 
only support for this database.**

    selenium==3.141.0
    pandas==0.25.3
    psycopg2-binary==2.8.4
    PyYAML==5.2

## Usage
### Configuration

Configure a PostgreSQL origin and configure the scheduling within the 
two available scrappers. Please, refer to: <https://hub.docker.com/_/postgres>

Example:
```
$ docker run --name some-postgres -p 3306:3306 -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```

Execute the following DDL statement to create the tweets insertion table.
```
create table twitter.tweets(
	id serial,
	tweet_id bigint not null,
	username varchar(15) not null,
	tweet text not null,
	primary key(id)
);

CREATE UNIQUE INDEX tw_id ON twitter.tweets (tweet_id);
```

Historical is for retrieving historical data and
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