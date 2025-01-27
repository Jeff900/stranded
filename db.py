import sqlite3
from os.path import getsize
import csv

class Database():
    db_name: str
    db: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self, db_name):
        self.db_name = db_name
        self.db = sqlite3.connect(db_name)
        self.cursor = self.db.cursor()
        self.create_database()

    def create_database(self) -> None:
        """create sqlite database if no database is already created"""
        print(f'Checking database {self.db_name}')
        self.set_db_schema()

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
        answers = self.read_from_csv('story/answers.csv')
        answers = self.csv_to_sql_values(answers)
        self.write_data_to_db(answers, 'db/insert_answers.sql')
        items = self.read_from_csv('story/items.csv')
        items = self.csv_to_sql_values(items)
        self.write_data_to_db(items, 'db/insert_items.sql')

    def get_columns(self) -> dict:
        """Defines columns per table in database"""
        columns = {
            'prompt': ['island', 'area', 'story_type', 'story', 'id', 'person', 'prompt', 'has_answers', 'following', 'following_alt', 'required_item', 'item'],
            'answer': ['id', 'prompt_id', 'num', 'answer', 'following', 'item_id']
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
        """Executes query to get prompt by prompt ID based on get_prompt SQL
        template. Returns a tuple with one result.
        """
        query = self.get_query('db/get_prompt.sql')
        query = query.format(cols=', '.join(cols))
        result = self.cursor.execute(query, (prompt_id, ))
        return result.fetchone()

    def get_answers(self, cols, prompt_id) -> list:
        """Executes query to get answers by prompt ID based on get_answers SQL
        template. Returns a list with tuples for each answer corresponding to
        the prompt ID.
        """
        query = self.get_query('db/get_answers.sql')
        query = query.format(cols=', '.join(cols))
        result = self.cursor.execute(query, (prompt_id, ))
        return result.fetchall()

    def collect_item(self, item_id: int, answer_id: int) -> None:
        """Insert item from answer into the inventory.
        """
        query = self.get_query('db/collect_item.sql')
        self.cursor.execute(query, (item_id, ))
        query = self.get_query('db/update_answer.sql')
        item_id = -abs(item_id)
        self.cursor.execute(query, (item_id, answer_id))
        self.db.commit()

    def item_by_id(self, item_id: int) -> tuple | None:
        """Get item by ID and return tuple or None
        """
        query = self.get_query('db/item_by_id.sql')
        return self.cursor.execute(query, (item_id, )).fetchone()

    def read_from_csv(self, filename: str) -> list:
        """Reads propmt from CSV file and get it prepared to write to SQLite
        database."""
        csv_data = []
        with open(filename, 'r') as csvfile:
            lines = csv.reader(csvfile, delimiter=';', quotechar='|')
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
            # print(query)
            self.cursor.execute(query)
        self.db.commit()

    def count_prompts(self):
        query = 'SELECT count(id) FROM prompt'
        results = self.cursor.execute(query).fetchone()
        return results[0]

    def empty_tables(self, tables):
        """Will remove all data from specified table. This is used when an
        error occurs during the database setup, to make sure no invalid or
        incomplete data will remain.
        """
        for table in tables:
            query = f'DELETE FROM {table}'
            self.cursor.execute(query)
        self.db.commit()
