import sqlite3
from os.path import getsize
import csv

class Database():

    def __init__(self, db_name):
        self.db_name = db_name
        self.db = sqlite3.connect(db_name)
        self.cursor = self.db.cursor()
        self.create_database()

    def create_database(self) -> None:
        """create sqlite database if no database is already created"""
        print(f'Checking database {self.db_name}')

        if getsize(self.db_name) <= 0:
            print('Database seems to be empty. Configuring database...')
            self.set_db_schema()
            # self.insert_game_data()

    def set_db_schema(self) ->None:
        """Sets schema, table structure etc. to the database.
        """
        print('Setting db schema')
        with open('db/create_database.sql', 'r') as f:
            queries = f.read()
        for query in queries.split(';'):
            self.cursor.execute(query)

    def insert_game_data(self) -> None:
        """Inserts gamedate that is loaded from CSV file. At the moment it is
        only dealing with prompt data, but should handle all CSV data files
        that should be loaded into the database.
        """
        prompts = self.read_from_csv('story/prompts.csv')
        prompts = self.csv_to_sql_values(prompts)
        self.write_data_to_db(prompts, 'db/insert_prompts.sql')

    def get_columns(self) -> dict:
        """Defines columns per table in database"""
        columns = {
            'prompt': ['island', 'area', 'story_type', 'story', 'id', 'person', 'prompt', 'has_answers', 'following'],
            'answer': ['prompt_id', 'num', 'answer', 'following']
        }
        return columns

    def get_query(self, file: str) -> str:
        """Reads query from text (sql) file and return it as a string. The file
        a template file with placeholders to add data to. Placeholders can be
        replaced using f-strings.
        """
        with open(file, 'r') as f:
            query = f.read()
        return query

    def get_prompt(self, cols: list, prompt_id) -> tuple | None:
        """"""
        query = self.get_query('db/get_prompt.sql')
        query = query.format(cols=', '.join(cols), id=prompt_id)
        result = self.cursor.execute(query)
        return result.fetchone()

    def get_answers(self, cols, prompt_id) -> list:
        """"""
        query = self.get_query('db/get_answers.sql')
        query = query.format(cols=', '.join(cols), prompt_id=prompt_id)
        result = self.cursor.execute(query)
        return result.fetchall()

    def read_from_csv(self, filename: str) -> list:
        """Reads propmt from CSV file and get it prepared to write to SQLite
        database."""
        csv_data = []
        with open(filename, 'r') as csvfile:
            lines = csv.reader(csvfile, delimiter=',', quotechar='|')
            for line in lines:
                csv_data.append(line)
        return csv_data

    def csv_to_sql_values(self, lines: list) -> list:
        sql_values = []
        for i, line in enumerate(lines):
            if i > 0:
                value = '(' + ', '.join(line) + ')'
                sql_values.append(value)
        return sql_values


    def write_data_to_db(self, data, queryfile):
        """Writes the prompts read from the CSV file to the database."""
        query_template = self.get_query(queryfile)
        for item in data:
            query = query_template.format(values=item)
            print(query)
            # result = self.cursor.execute(query)
            self.cursor.execute(query)
        # return result
