from typing import List, Union, Optional
from BTrees.OOBTree import OOBTree
from nltk.stem.snowball import SnowballStemmer
import io
import re
import pickle
from my_modules import file_handler as fh

# Regular expression for text parsing
regexps = {
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
                return res
        if res is not None:
            return res.group()

    return None


def build_term_tree(file_list: List[str],
                    is_inverse: bool = False,
                    serialize: bool = False) -> OOBTree:
    tree_root: OOBTree = OOBTree()
    current_root: OOBTree = tree_root

    for file in file_list:
        with io.open(fr'{file}', encoding='utf-8-sig') as file_reader:
            for line in file_reader:
                for word in line.split():
                    if is_inverse:
                        word = word[-1::-1]

                    current_root = tree_root
                    norm_word = normalize(word)

                    if norm_word is None:
                        continue

                    for index, char in enumerate(norm_word):
                        item = current_root.get(char, None)
                        if item is not None:
                            current_root = item
                        else:
                            current_root.insert(char, OOBTree())
                            current_root = current_root.get(char)
                        if index == len(norm_word) - 1:
                            current_root.insert('^', True)

    if serialize:
        pickle.dump(tree_root, io.open('pickled_term_tree.pkl', 'wb'),
                    protocol=pickle.HIGHEST_PROTOCOL)

    return tree_root


def transposition_index(file_list: List[str], save_to_file: bool = False) -> OOBTree:
    index: OOBTree = OOBTree()

    for file in file_list:
        with io.open(fr'{file}', encoding='utf-8-sig') as file_reader:
            for line in file_reader:
                for word in line.split():
                    norm_word = normalize(word)

                    if norm_word is not None:
                        perms: List[str] = [norm_word + '^']
                        perm = list(norm_word + '^')

                        for i in range(len(norm_word)):
                            perm.append(perm.pop(0))
                            perms.append(''.join(perm))

                        for item in perms:
                            if item in index:
                                index.get(item).add(norm_word)
                            else:
                                index.insert(item, {norm_word})
                    else:
                        continue

    if save_to_file:
        index_for_json = dict(index.items())

        for key in index.keys():
            index_for_json[key] = list(sorted(index.get(key)))
        fh.write_json('transposition_index', index_for_json)

    return index


def three_gram_index(file_list: List[str], save_to_file: bool = False) -> OOBTree:
    index: OOBTree = OOBTree()

    for file in file_list:
        with io.open(fr'{file}', encoding='utf-8-sig') as file_reader:
            for line in file_reader:
                for word in line.split():
                    norm_word = normalize(word)

                    if norm_word is not None:
                        grams = [fr'^{norm_word}^'[i:i + 3] for i in range(len(norm_word))]

                        for gram in grams:
                            if gram in index:
                                index.get(gram).add(norm_word)
                            else:
                                index.insert(gram, {norm_word})

                    else:
                        continue

    if save_to_file:
        index_for_json = dict(index.items())

        for key in index.keys():
            index_for_json[key] = list(sorted(index.get(key)))
        fh.write_json('three_gram_index', index_for_json)

    return index
