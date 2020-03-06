import io
import re
import unicodedata
from typing import List

import contractions
import inflect
from colorama import Fore, Style
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer


def remove_non_ascii(words: List[str]) -> List[str]:
    new_words: List[str] = []

    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)

    return new_words


def to_lowercase(words: List[str]) -> List[str]:
    new_words: List[str] = []

    for word in words:
        new_word = word.lower()
        new_words.append(new_word)

    return new_words


def remove_punctuation(words: List[str]) -> List[str]:
    new_words: List[str] = []

    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)

        if new_word != '':
            new_words.append(new_word)

    return new_words


def replace_numbers(words: List[str]) -> List[str]:
    p = inflect.engine()
    new_words: List[str] = []

    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)

    return new_words


def stem_words(words: List[str]) -> List[str]:
    stemmer = SnowballStemmer('english')
    stems: List[str] = []

    for word in words:
        stem = stemmer.stem(word)
        stems.append(stem)

    return stems


def normalize(words: List[str]) -> List[str]:
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = stem_words(words)
    words = replace_numbers(words)

    return words


def preprocess_documents(documents, base_path):
    preprocessed_documents = {}

    for file_id in documents:
        with io.open(fr'{base_path}\\{file_id}', encoding='utf-8-sig') as file_reader:

            print(f'{Fore.BLUE}Preprocessing {file_reader.name}{Style.RESET_ALL}...')

            for line in file_reader:
                line = contractions.fix(line)
                words = word_tokenize(line)
                norm_words = normalize(words)

                if len(norm_words) == 0:
                    continue

                if preprocessed_documents.get(file_id, None) is None:
                    preprocessed_documents[file_id] = norm_words
                else:
                    preprocessed_documents[file_id].extend(norm_words)

            print(f'{Fore.GREEN}Finished preprocessing {file_reader.name}{Style.RESET_ALL}')

    return preprocessed_documents
