"""module for handling prompts and answer"""

from art import tprint


class Prompt():

    def __init__(self, db):
        self.db = db
        self.columns = self.db.get_columns()
        self.island = ''
        self.area = ''
        self.story_type = ''
        self.story = ''
        self.current_prompt = 1
        self.prev_prompt = None
        self.next_prompt = 1
        self.prompt = None
        self.answers = None
        self.debug = True

    def get_prompt(self) -> None:
        """Get the next prompt based on the `next_prompt` variable.
        `next_prompt` is set based on the previous get_prompt() call."""

        prompt = self.db.get_prompt(self.columns['prompt'], self.next_prompt)
        prompt = self.set_dict(prompt, self.columns['prompt'])
        self.current_prompt = prompt['id']
        self.prompt = prompt
        self.set_next_prompt(prompt['following'])

    def get_answers(self) -> None:
        """Get the answer corresponding to current prompt. This function
        should only be called when a prompt contains answers."""

        answers = self.db.get_answers(self.columns['answer'], self.current_prompt)
        answers = self.set_dict(answers, self.columns['answer'])
        answers = self.numbering_answers(answers)
        self.answers = answers

    def numbering_answers(self, answers: dict) -> dict:
        """Formats all answers so that the index number from every answer
        becomes the key value of a dictionary. This way the numbers can be
        used as answer numbers for user input and can be found in the
        dictionary using the user input. The value of the dictionary is the
        dictionary created with Prompt.set_dict()."""

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
        # if prompt item required is not 0
        if self.prompt['required_item'] != 0 and self.has_required_item(
            self.prompt['required_item']):
            print('Item required here AND in inventory')
            self.next_prompt = self.prompt['following_alt']
        else: 
            self.next_prompt = following
        self.answers = None

    def set_dict(self, query, cols) -> dict | list:
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

    def print_prompt(self, gamename, heigth, width) -> None:
        tprint(gamename)
        blank_line = self.format_blank_line(width)
        print('#' * width)
        print(blank_line)
        heigth -= 9

        menu = self.format_text('Menu: Inventory (i) - Quit game (quit)', width)
        prompt = self.format_text(self.prompt['prompt'], width)
        answers = self.format_answers(width)

        menu_lines = self.count_lines_simplified(menu)
        heigth -= menu_lines
        prompt_lines = self.count_lines_simplified(prompt)
        prompt_answer_lines = self.count_lines_simplified(answers)

        prompt_total = self.prompt_count_total(prompt_lines, prompt_answer_lines)
        print(menu)
        print(blank_line * (heigth - (prompt_total)))
        print(self.format_text(self.prompt['prompt'], width))
        print(blank_line)
        if len(answers) > 0:
            print(answers)

    def format_text(self, text, width) -> str:
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

    def format_answers(self, width) -> str:
        """"""
        answer_text = ''
        for i, answer in enumerate(self.answers.values(), start=1):
            answer_line = self.format_text(f"{answer['num']} {answer['answer']}" ,width)
            answer_text = answer_text + answer_line
            if i < len(self.answers):
                answer_text = answer_text + '\n'

        return answer_text

    def count_lines_simplified(self, text) -> int:
        """Simplified function to count the number of lines in text based on a
        split on `\n`. Returns the length of the list, which a representation
        of the number of lines.
        """
        if text == '':
            return 0
        return len(text.split('\n'))

    def count_lines(self, text, width) -> int:
        """Counts the number of lines are needed to print the text within the
        predefined width. It only uses full words.
        count_lines() might be superfluous for at least prompts. It is easier
        to simply split the formatted_text from format_text() on '\n' and check
        the list length.
        Not sure if this is working for answer this easy.
        """

        # width should be width minus "# " en " #" on both ends of the line
        width -= 4
        # number_of lines has a minimum of 1
        number_of_lines = 1
        # character count starts at 0 for first line
        character_count = 0
        for word in text.split(' '):
            if len(word) + character_count <= width:
                # if word still fits on the same line, add length to
                # character_count.
                character_count += len(word) + 1
            else:
                # if word doesn't fit on the same line, add 1 to
                # number_of_lines and set character_count to length of word
                number_of_lines += 1
                character_count = len(word) + 1
        return number_of_lines

    def count_answer_lines(self, width) -> int:
        """Gets sum of all lines that are needed to print all possible answer
        from a prompt. At the moment it will only work correctly with less than
        10 answers, because the code will not look at the length of the nubmer
        that is used as prefix for the answer. At will assume a length of 1.
        """
        if self.prompt['has_answers'] == 0:
            return 0
        else:
            number_of_lines = 0
            for num, answer in self.answers.items():
                formatted_answer = f'{num} {answer}'
                number_of_lines += self.count_lines(formatted_answer, width)
            return number_of_lines

    def prompt_count_total(self, prompt_lines, answer_lines) -> int:
        """Counts the number of lines that the prompt, and if applicable the
        answers, needs to be printed on.
        """
        # total of prompt lines + 1 empty line after
        total = prompt_lines + 1
        # total prompt + answer lines + 1 if there are answers.
        if answer_lines > 0:
            total = total + answer_lines
        return total + 1

    def format_blank_line(self, width) -> str:
        """Formats a line that should only contain the borders, and in between
        only spaces. This line will be used to fill the screen where no content
        is printed.
        """
        return '# ' + ' ' * (width - 4) + ' #'

    def has_required_item(self, item_id):
        """Looks if item_id from the prompts query is None. In that case
        returns False. If item is required, an integer should be used in the
        database to poin the the specific item (id).
        """
        required_item = self.db.item_by_id(item_id)
        if required_item is None:
            return False
        return True
