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
        answers = self.numbering_answers(answers)
        self.answers = answers

    def numbering_answers(self, answers):
        """Formats all answers so that the index number from every answer
        becomes the key value of a dictionary. This way the numbers can be
        used as answer numbers for user input and can be found in the
        dictionary using the user input. The value of the dictionary is the
        dictionary created with set_dict()."""

        answers_dict = {}
        for answer in answers:
            answers_dict[answer['num']] = answer
        return answers_dict

    def valid_answer(self, user_input: str) -> bool:
        """Checks if the user input is valid. To be defined in more detail.
        """
        for answer in self.answers:
            if user_input == str(answer):
                return True
        return False

    def set_next_prompt(self, following) -> None:
        """Sets the next_pompt attribute to the following prompt id from prompt
        or answer. It resets the answers to None.
        """
        self.next_prompt = following
        self.answers = None

    def set_dict(self, query, cols):
        """Sets dictionary with query results per column. Returns a single dict
        when query contains one record. Returns list of dicts when query
        contains multiple records.
        """
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

    def print_prompt(self, heigth, width):
        blank_line = self.format_blank_line(width)
        prompt = self.format_text(self.prompt['prompt'], width)
        answers = self.format_answers(width)
        prompt_lines_s = self.count_lines_simplified(prompt)
        prompt_answer_lines_s = self.count_lines_simplified(answers)
        prompt_lines = self.count_lines(self.prompt['prompt'], width)
        answer_lines = self.count_answer_lines(width)
        print(prompt_lines, answer_lines)
        print(prompt_lines_s, prompt_answer_lines_s)
        print('#' * width)
        print(blank_line * 5)
        print(self.format_text(self.prompt['prompt'], width))
        print(blank_line * 5)
        if len(answers) > 0:
            print(answers)
        # print(self.format_answers(width))

    def format_text(self, text, width):
        width -= 4
        formatted_text = '# '
        text = text.split(' ')
        char_count = 0
        for word in text:
            if len(formatted_text) == 2:
                formatted_text = formatted_text + word
                char_count += len(word)
            elif len(word) + char_count < width:
                formatted_text = formatted_text + ' ' + word
                char_count += len(word) + 1
            else:
                spaces = width - char_count
                formatted_text = formatted_text + ' ' * spaces + ' #\n# ' + word
                char_count = len(word)
        spaces = width - char_count
        formatted_text = formatted_text + ' ' * spaces + ' #'
        return formatted_text

    def format_answers(self, width):
        answer_text = ''
        for i, answer in enumerate(self.answers.values(), start=1):
            answer_line = self.format_text(f'{answer['num']} {answer['answer']}' ,width)
            answer_text = answer_text + answer_line
            if i < len(self.answers):
                answer_text = answer_text + '\n'

        return answer_text

    def count_lines_simplified(self, text):
        """Simplified function to count the number of lines in text based on a
        split on `\n`. Returns the length of the list.
        """
        return len(text.split('\n'))

    def count_lines(self, text, width):
        """Counts the number of lines are needed to print the text within the
        predefined width. It only uses full words.
        count_lines() might be superfluous for at least prompts. It is easier
        to simply split the formatted_text from format_text() on '\n' and check
        the list length.
        Not sure if this is working for answer this easy.
        """
        width -= 4
        number_of_lines = 1
        character_count = 0
        for word in text.split(' '):
            if len(word) + character_count <= width:
                character_count += len(word) + 1
            else:
                number_of_lines += 1
                character_count = len(word) + 1
        return number_of_lines

    def count_answer_lines(self, width):
        """Gets sum of all lines that are needed to print all possible answer
        with a prompt. At the moment it will only work correctly with less than
        10 answers.
        """
        if self.prompt['has_answers'] == 0:
            return 0
        else:
            number_of_lines = 0
            for num, answer in self.answers.items():
                formatted_answer = f'{num} {answer}'
                number_of_lines += self.count_lines(formatted_answer, width)
            return number_of_lines

    def format_blank_line(self, width):
        """Formats a line that should only contain the borders, and in between
        only spaces.
        """
        return '# ' + ' ' * (width - 4) + ' #'

    def print_state(self) -> None:
        """Prints the various states of prompt id's variables for debugging
        purposes. self.debug should be set to False in production."""
        if self.debug:
            print('\n### Current state of variables ###')
            print('current:', type(self.current_prompt), self.current_prompt)
            print('previous:', type(self.prev_prompt), self.prev_prompt)
            print('next:', type(self.next_prompt), self.next_prompt)
            print('##################################\n')
