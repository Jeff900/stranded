"""This is the main module for the Stranded game."""

import shutil
from db import Database
from prompts import Prompt


class Game:
    """General class to handle all general data, such as game name, db
    connection, installation funtions etc.
    """
    settings: dict
    db_name: str
    db: Database
    gamename: str
    username: str
    width: int
    height: int

    def __init__(self, db_name='stranded.db'):
        self.settings = self.load_settings()
        self.db_name = db_name
        self.db = Database(self.db_name)
        self.db.set_db_schema()
        self.gamename = self.settings['gamename']
        self.screen_size()
        self.username = 'username'
        if not self.check_database():
            self.setup_database()

    def screen_size(self) -> None:
        "Get current screen height and width of terminal"
        self.width, self.height = shutil.get_terminal_size()

    def load_settings(self) -> dict:
        """Loads settings from settings file and returns it as a dictionary"""
        with open('settings', 'r') as f:
            settings = dict()
            for line in f:
                key, value = line.split('=')
                if len(value.split(',')) > 1:
                    value = value.split(',')
                settings[key.strip()] = value
        return settings

    def check_database(self):
        """Checks if there is data in the prompts table in the database. If so,
        assume that the database is correctly setup. Currently it will not
        check every single table. 
        """
        if self.db.count_prompts() == 0:
            return False
        return True

    def setup_database(self):
        """Data will be inserted to tables in database. If an error occurs, the
        tables will be emptied again to prevent invalid and incomplete data in
        the database.
        """

        try:
            # try inserting the gamedata
            self.db.insert_game_data()
        except Exception:
            # on error, empty all tables
            self.db.empty_tables(['prompt', 'answer', 'item'])
            print('Not able to setup the database. Deleting data and quiting...')
            quit()


def main():
    game = Game()
    prompt = Prompt(game.db)

    while True:
        game.screen_size()
        prompt.get_prompt()
        prompt.get_answers()
        prompt.print_prompt(game.gamename, game.height, game.width)

        if prompt.prompt['has_answers'] == 0:
            user_input = input('Hit enter to continue... ')
        else:
            user_input = input('Select answer (enter number): ')
            if prompt.valid_answer(user_input):
                # get item_id from answer and checks if it is an actual item_id
                # e.g. not 0.
                item_id = prompt.answers[int(user_input)]['item_id']
                answer_id = prompt.answers[int(user_input)]['id']
                if item_id != 0:
                    # if actual item_id, put it in inventory and change answer
                    # table. Make id negative integer.
                    game.db.collect_item(item_id, answer_id)

                prompt.set_next_prompt(
                    prompt.answers[int(user_input)]['following'])

        if user_input in ['quit', 'exit']:
            break

        print()


if __name__ == '__main__':
    main()
