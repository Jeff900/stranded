"""module for handling prompts and answer"""


class Prompt():
    def __init__(self, db):
        self.db = db
        self.columns = self.db.get_columns()
        self.island = ''
        self.area = ''
        self.story_type = ''
        self.story = ''
        self.current_prompt = '1'
        self.prev_prompt = ''
        self.next_prompt = '1'
        self.prompt = None
        self.answers = None
        self.debug = True

    def get_prompt(self):
        """Get the next prompt based on the `next_prompt` variable.
        `next_prompt` is set based on the previous get_prompt() call."""

        prompt = self.db.get_prompt(self.columns['prompt'], self.next_prompt)
        prompt = self.set_dict(prompt, self.columns['prompt'])
        self.current_prompt = prompt['id']
        self.next_prompt = prompt['following']
        self.prompt = prompt

    def get_answers(self):
        """Get the answer corresponding to current prompt. This function
        should only be called when a prompt contains answers."""

        answers = self.db.get_answers(self.columns['answer'], self.current_prompt)
        answers = self.set_dict(answers, self.columns['answer'])
        answers = self.format_answers(answers)
        self.answers = answers

    def format_answers(self, answers):
        """Formats all answers so that the index number from every answer
        becomes the key value of a dictionary. This way the numbers can be
        used as answer numbers for user input and can be found in the
        dictionary using the user input. The value of the dictionary is the
        dictionary created with set_dict()."""

        answers_dict = {}
        for answer in answers:
            answers_dict[answer['num']] = answer
        return answers_dict

    def valid_answer(self, user_input):
        """Checks if the user input """
        for answer in self.answers:
            if user_input == str(answer):
                return True
        return False

    def set_next_prompt(self, following):
        self.next_prompt = following
        self.answers = None

    def set_dict(self, query, cols):
        """Sets dictionary with query results per column. Returns a single dict
        when query contains one record. Returns list of dicts when query
        contains multiple records."""

        if type(query) == tuple:
            query_dict = {}
            for i, value in enumerate(query):
                query_dict[cols[i]] = value
            return query_dict

        if type(query) == list:
            query_list = []
            for results in query:
                query_dict = {}
                for i, value in enumerate(results):
                    query_dict[cols[i]] = value
                query_list.append(query_dict)
            return query_list

    def print_preprompt(self):
        print(50 * '#')
        print('#', 'Stranded', 37 * ' ','#')
        print('#', 'Insert `quit` to exit the game.', 14 * ' ', '#')
        print(50 * '#')

    def print_state(self):
        """Prints the various states of prompt id's variables for debugging
        purposes. self.debug should be set to False in production."""
        if self.debug:
            print('\n### Current state of variables ###')
            print('current:', type(self.current_prompt), self.current_prompt)
            print('previous:', type(self.prev_prompt), self.prev_prompt)
            print('next:', type(self.next_prompt), self.next_prompt)
            print('##################################\n')
