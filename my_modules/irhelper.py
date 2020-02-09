import os
import re
import regex
import io
import json
import my_modules.file_handler as fh
from typing import List, Dict, Set, Optional, Union
from nltk.stem.snowball import SnowballStemmer
from pandas import DataFrame


class IRHelper(object):
    def __init__(self, dir_path: str):
        self.__files_list = fh.files_in_dir(dir_path)  # List of absolute paths of files to index
        self.__dir_path = dir_path  # Directory where files for indexing are placed
        self.__stemmer = SnowballStemmer('english')  # Stemmer object
        self.__regexps = {  # Regular expression for text parsing
            'url': r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            'email': r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
            'mostly_letters': r"[a-zA-Z]+['-]?[a-zA-Z]+|[a-zA-Z]+"
        }

    # Takes a single word and tries to match it with regular expressions
    # defined in the __init__. This method also performs normalization,
    # i.e. stems the word.
    def normalize(self, word: str) -> Optional[str]:
        for regexp in self.__regexps:
            res: Union['regexp match', None] = None

            if regexp == 'url' or regexp == 'email':
                res = re.match(self.__regexps[regexp], word)
            if regexp == 'mostly_letters':
                res = re.match(self.__regexps[regexp], word.lower())

                if res is not None:
                    res = res.group()
                    return self.__stemmer.stem(res)
            if res is not None:
                return res.group()

        return None

    # Splits string into words.
    # Returns number of words in the string and a list of words.
    def tokenize(self, line: str) -> (int, List[str]):
        words: List[str] = line.split()

        return len(words), words

    # Builds lexicon, i.e. a list of unique words received after parsing
    # documents.
    # Returns the total number of words that documents contained, total
    # number of words in the lexicon and the lexicon itself.
    def build_lexicon(self,
                      write_to_file: bool = False,
                      file_name: str = 'lexicon') -> (int, int, List[str]):
        words_in_collection: int = 0
        lexicon: List[str] = []

        for file in self.__files_list:
            with io.open(fr'{file}', encoding='utf_8') as file_handler:
                for line in file_handler:
                    words_in_line, words = self.tokenize(line)
                    lexicon.extend([word for word in map(self.normalize, words) if word is not None])
                    words_in_collection += words_in_line
            lexicon = list(set(lexicon))

        lexicon = sorted(lexicon)
        if write_to_file:
            fh.write_txt(file_name, '\n'.join(lexicon))

        return words_in_collection, len(lexicon), lexicon

    # Builds incidence matrix.
    # Returns DataFrame (a table, basically) with columns labeled
    # by words and rows labeled by document names.
    def build_incidence_matrix(
            self,
            write_to_file: bool = False,
            file_name: str = 'incidence_matrix') -> (List[str], DataFrame):
        # I decided to use dictionary (hash map) because its average
        # complexity for element insertion, deletion and access is O(1)
        # Even if we will need to change the size of the dictionary it
        # still will be working with O(1) complexity.
        # I decided to use lists (arrays) as keys since its very easy to
        # set values in the arbitrary cells of the array.
        matrix: Dict[str, List[int]] = {}

        for file in self.__files_list:
            with io.open(fr'{file}', encoding='utf_8') as file_handler:
                for line in file_handler:
                    _, words = self.tokenize(line)
                    norm_words = [word for word in map(self.normalize, words) if word is not None]

                    for word in norm_words:
                        row: List[int] = matrix.get(word, [])

                        if not row:
                            inc_row = [0] * len(self.__files_list)
                            inc_row[self.__files_list.index(file)] = 1
                            matrix[word] = inc_row
                        else:
                            row[self.__files_list.index(file)] = 1
        if write_to_file:
            fh.write_json(file_name, matrix)

        # List of absolute paths of files is returned with the incidence matrix
        # because indexes in the rows correspond to the indexes in this list.
        return self.__files_list, DataFrame(matrix, index=[os.listdir(self.__dir_path)])

    # Builds inverted index.
    # Returns a map where keys are file ids and
    # values are file names and inverted index.
    def build_inverted_index(self,
                             write_to_file: bool = False,
                             file_name: str = 'inverted_index') -> (Dict[int, str], Dict[str, Set[int]]):
        # I decided to use dictionary (hash map) because its average
        # complexity for element insertion, deletion and access is O(1)
        # Even if we will need to change the size of the dictionary it
        # still will be working with O(1) complexity.
        # I decided to use sets as keys because they can contain only unique
        # values.
        index: Dict[str, Set[int]] = {}
        file_map: Dict[int, str] = {}
        file_count: int = 0

        for file in self.__files_list:
            file_count += 1

            with io.open(fr'{file}', encoding='utf_8') as file_handler:
                file_map[file_count] = os.path.basename(file_handler.name)

                for line in file_handler:
                    _, words = self.tokenize(line)
                    norm_words = [word for word in map(self.normalize, words) if word is not None]

                    for word in norm_words:
                        row: Set[int] = index.get(word, {})

                        if not row:
                            index[word] = {file_count}
                        else:
                            index[word].add(file_count)
        if write_to_file:
            index_for_json: Dict[str, List[int]] = {}

            for word in index.keys():
                index_for_json[word] = list(sorted(index[word]))
            fh.write_json(file_name, index_for_json)
            fh.write_json('file_map', file_map)

        return file_map, index

    # This function is used to perform boolean search.
    # It reads all necessary data from files and calls
    # the function which makes boolean expression evaluation.
    def bool_search(self,
                    expr: str,
                    inverted_index_path: str,
                    file_map_path: str,
                    inverted_index: Optional = None) -> List[List[str]]:
        ques: Dict[str, Union[List[str], List[List[str]]]] = {
            'op_que': [],  # Que for operators we will find in boolean expression
            # Que for arguments (list of documents where a word occurred derived
            # from the word in the expression) we will find in boolean expression
            'arg_que': [],
            'exp_que': [expr]  # Que for expressions which are surrounded by parenthesis
        }

        with open(file_map_path, 'r') as handler:
            file_map = json.load(handler)

        if inverted_index is None:
            with open(inverted_index_path, 'r') as handler:
                index: Dict[str, List[str]] = json.load(handler)
        else:
            index: Dict[str, List[str]] = inverted_index

        self.eval_bool_expr(index, ques, file_map)  # Performs boolean expression evaluation

        return [file_map[str(file_id)] for file_id in ques['arg_que'].pop()]

    # This function evaluates boolean expression
    def eval_bool_expr(self,
                       index: Dict[str, list],
                       ques: Dict[str, list],
                       file_map: Dict[str, str]):
        curr_exp: str = ques['exp_que'].pop()  # Take expression from the que of expressions
        # Find expressions surrounded by parenthesis and save them into the following variable
        more_exp: List[str] = regex.findall("\(([^()]*+(?:(?R)[^()]*)*+)\)", curr_exp)

        if more_exp:  # If there any expressions surrounded by parenthesis
            # Remove them from the current expression
            ques['exp_que'].append(regex.sub("\(([^()]*+(?:(?R)[^()]*)*+)\)", '', curr_exp))
            ques['exp_que'].extend(more_exp)  # Add expressions surrounded by parenthesis to the que
            self.eval_bool_expr(index, ques, file_map)  # Repeat
        else:  # If there are no expressions surrounded by parenthesis
            for tok in curr_exp.split():  # Split current expression into words (tokens) by spaces
                # NOT! is the same as NOT but used before expressions in parenthesis so that the expression
                # could be evaluated correctly
                if tok in ['AND', 'OR', 'NOT', 'NOT!']:  # If this token is an operator
                    ques['op_que'].append(tok)  # Put it into the que of operators
                else:  # If this token is not an operator
                    # Get the list of documents where this word occurred
                    inc_row = index.get(self.normalize(tok), {})
                    ques['arg_que'].append(inc_row)  # Add it to the list of arguments
                    # If we have at least two arguments and one operator, perform
                    # operator evaluation.
                    if len(ques['arg_que']) >= 2 and len(ques['op_que']) >= 1:
                        self.__eval_helper(index, ques, file_map)
            # If we have any operators left after parsing the expression
            # perform their evaluation.
            if not ques['exp_que'] or ques['op_que']:
                while ques['op_que']:
                    self.__eval_helper(index, ques, file_map)
        # Repeat if we have any expressions left
        if ques['exp_que']:
            self.eval_bool_expr(index, ques, file_map)
        else:
            return None

    # Helper method which evaluates boolean operators
    def __eval_helper(self,
                      index,
                      ques: dict,
                      file_map: Dict[str, str]):
        op = ques['op_que'].pop()

        if op == 'AND':
            arg1 = set(ques['arg_que'].pop())
            arg2 = set(ques['arg_que'].pop())
            ques['arg_que'].append(arg1.intersection(arg2))
        if op == 'OR':
            arg1 = set(ques['arg_que'].pop())
            arg2 = set(ques['arg_que'].pop())
            ques['arg_que'].append(arg1.union(arg2))
        if op == 'NOT':
            arg = set(ques['arg_que'].pop())
            ques['arg_que'].append(set([int(key) for key in file_map.keys()]).difference(arg))
            self.__eval_helper(index, ques, file_map)
        # NOT! is the same as NOT but used before expressions in parenthesis so that the expression
        # could be evaluated correctly
        if op == 'NOT!':
            arg = set(ques['arg_que'].pop(0))
            ques['arg_que'].append(set([int(key) for key in file_map.keys()]).difference(arg))
            self.__eval_helper(index, ques, file_map)
