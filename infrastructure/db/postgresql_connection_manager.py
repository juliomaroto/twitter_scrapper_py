import psycopg2
import sqlalchemy
import pandas as pd


class PostgreSqlConnectionManager:
    PROTOCOL_NAME = 'postgresql'

    def __init__(self, connection_info: {}):
        self.__connection = self.__get_connection(connection_info)
        self.__connection.set_session(autocommit=True)
        self.__engine = self.__get_alchemy_engine(connection_info)

    def __get_connection(self, connection_info: {}):
        return psycopg2.connect(
            host=connection_info['host'],
            dbname=connection_info['dbname'],
            user=connection_info['user'],
            password=connection_info['password']
        )
    
    def __get_alchemy_engine(self, connection_info: {}):
        connection_endpoint = '{protocol}://{user}:{password}@{host}/{dbname}'
        connection_endpoint = connection_endpoint.format(
            protocol=self.PROTOCOL_NAME,
            host=connection_info['host'],
            dbname=connection_info['dbname'],
            user=connection_info['user'],
            password=connection_info['password']
        )

        engine = sqlalchemy.create_engine(connection_endpoint)
        connection = engine.connect()
        
        return connection

    def read_dataframe(self, query: str):
        return pd.read_sql(query, self.__engine)

    def write_dataframe_to_schema_table(self, df, schema, table):
        df.to_sql(
            schema=schema,
            name=table,
            con=self.__engine,
            index=False,
            if_exists='replace'
        )

    def execute_statement(self, stmt):
        cursor = self.__connection.cursor()
        cursor.execute(stmt)
        cursor.close()
