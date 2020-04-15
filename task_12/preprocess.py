import io
import re
import os
import warnings
import unicodedata
from typing import List

import contractions
import inflect
from colorama import Fore, Style
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore', category=UserWarning, module='bs4')


def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


def remove_between_square_brackets(text):
    return re.sub(r'\[[^]]*\]', '', text)


def denoise_text(text):
    text = strip_html(text)
    text = remove_between_square_brackets(text)
    return text


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
    try:
        words = replace_numbers(words)
    except Exception as e:
        print('Cannot convert number to string. Number too big. ', str(e))

    return words


def preprocess_documents(documents, base_path):
    preprocessed_documents: List[str] = []

    for file_id in documents:
        with io.open(fr'{base_path}\\{file_id}', mode='r', encoding='utf-8-sig') as file_reader:
            with io.open(fr'normalized_files\\{os.path.splitext(file_id)[0]}.txt', mode='w') as file_writer:
                print(f'{Fore.BLUE}Preprocessing {file_reader.name}{Style.RESET_ALL}...')

                for line in file_reader:
                    line = denoise_text(line)
                    line = contractions.fix(line)
                    words = word_tokenize(line)
                    norm_words = normalize(words)

                    if len(norm_words) == 0:
                        continue

                    file_writer.write(f"{'|'.join(norm_words)}\n")
                    norm_words.clear()

                preprocessed_documents.append(fr'normalized_files\\{os.path.splitext(file_id)[0]}.txt')

                print(f'{Fore.GREEN}Finished preprocessing {file_reader.name}{Style.RESET_ALL}')

    return preprocessed_documents


def preprocess_query(query):
    query = contractions.fix(query)
    query = word_tokenize(query)
    norm_query = normalize(query)

    return norm_query
