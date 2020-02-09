from typing import List, Union, Optional, Dict
from BTrees.OOBTree import OOBTree
from nltk.stem.snowball import SnowballStemmer
import io
import os
import re
import my_modules.file_handler as fh

regexps = {  # Regular expression for text parsing
    'url': r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
    'email': r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
    'mostly_letters': r"[a-zA-Z]+['-]?[a-zA-Z]+|[a-zA-Z]+"
}

stemmer = SnowballStemmer('english')


# Takes a single word and tries to match it with regular expressions
# defined in the regexps. This method also performs normalization,
# i.e. stems the word.
def normalize(word: str) -> Optional[str]:
    for regexp in regexps:
        res: Union['regexp match', None] = None

        if regexp == 'url' or regexp == 'email':
            res = re.match(regexps[regexp], word)
        if regexp == 'mostly_letters':
            res = re.match(regexps[regexp], re.sub(fr"[\"“”]", '', word.lower()))

            if res is not None:
                res = res.group()
                return stemmer.stem(res)
        if res is not None:
            return res.group()

    return None


# Builds phrase index
# Returns index in BTree form and file to id mapping
def phrase_index(files_list: List[str],
                 write_to_file: bool = False,
                 output_file: str = 'phrase_index') -> (OOBTree, Dict[int, str]):
    phrase: List[str] = []
    index: OOBTree = OOBTree()
    file_map: Dict[int, str] = {}
    file_count: int = 0

    for file in files_list:
        file_count += 1
        # Open file to read data from it
        with io.open(fr'{file}', encoding='utf_8') as file_reader:
            # Create a mapping of the file index to the file name
            file_map[file_count] = os.path.basename(file_reader.name)

            # Read lines from the file
            for line in file_reader:
                # Read words from the line
                for word in line.split():
                    # Normalize each word
                    norm_word = normalize(word)

                    if norm_word is not None:
                        # Append word to the phrase
                        phrase.append(norm_word)
                    else:
                        continue

                    # If the phrase consists of two words
                    if len(phrase) >= 2:
                        term = fr'{phrase[0]} {phrase[1]}'
                        item = index.get(term, False)

                        # If there is no such phrase in the index
                        if not item:
                            # Add new phrase to the index
                            index.insert(term, {file_count})
                        else:
                            # Otherwise, append file id to the
                            # list of ids of the existing phrase
                            item.add(file_count)

                        phrase[0] = phrase.pop()
                    else:
                        continue

    # Write date to the .json file
    if write_to_file:
        index_for_json = dict(index.items())

        for key in index.keys():
            index_for_json[key] = list(sorted(index.get(key)))
        fh.write_json(output_file, index_for_json)
        fh.write_json('phrase_index_file_map', file_map)

    return index, file_map


# Builds coordinate index
# Returns index in BTree form and file to id mapping
def coordinate_index(files_list: List[str],
                     write_to_file: bool = False,
                     output_file: str = 'coordinate_index') -> (OOBTree, Dict[int, str]):
    index: OOBTree = OOBTree()
    file_map: Dict[int, str] = {}
    file_count: int = 0
    word_count: int = 0

    for file in files_list:
        file_count += 1
        # Open file to read data from it
        with io.open(fr'{file}', encoding='utf_8') as file_reader:
            # Create a mapping of the file index to the file name
            file_map[file_count] = os.path.basename(file_reader.name)

            # Read lines from the file
            for line in file_reader:
                # Read words from the line
                for word in line.split():
                    word_count += 1
                    # Normalise the word
                    term = normalize(word)

                    if term is not None:
                        item = index.get(term, False)

                        # If there is no such word in the index
                        if not item:
                            # Add the new word to the index
                            index.insert(term, {file_count: [word_count]})
                        else:
                            # If a word exists but doesn't have such file id
                            if not item.get(file_count, False):
                                # Add the file id
                                item[file_count] = [word_count]
                            else:
                                # Add word position to the file's coordinate list
                                item[file_count].append(word_count)
                    else:
                        continue

    # Write date to the .json file
    if write_to_file:
        fh.write_json(output_file, dict(index.items()))
        fh.write_json('coordinate_index_file_map', file_map)

    return index, file_map
