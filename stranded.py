"""This is the main module for the Stranded game."""

from db import Database
from prompts import Prompt
import os


class Game:
    """General class to handle all general data, such as game name, db
    connection, installation funtions etc.
    """

    def __init__(self, db_name='stranded.db'):
        self.settings = self.load_settings()
        print(self.settings)
        self.db_name = db_name
        self.db = Database(self.db_name)
        self.gamename = self.settings['gamename']
        self.screen_size()
        self.username = 'username'

    def screen_size(self):
        "Get current screen heigth and width of terminal"
        self.width, self.heigth = os.get_terminal_size()

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


def main():
    game = Game()
    prompt = Prompt(game.db)

    while True:
        game.screen_size()
        prompt.get_prompt()
        prompt.get_answers()
        prompt.print_prompt(game.gamename, game.heigth, game.width)

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
