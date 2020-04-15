import re
import os
import random
import inflect
import warnings
import collections
import unicodedata
import contractions

from typing import List, Dict
from lxml import etree
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer

warnings.filterwarnings('ignore', category=UserWarning, module='bs4')


def flatten_list(lst):
    if isinstance(lst, collections.Iterable) and not isinstance(lst, str):
        return [a for i in lst for a in flatten_list(i)]
    else:
        return [lst]


def flatten_dict(d) -> dict:
    for (key, value) in d.items():
        if isinstance(value, str) or value is None:
            if key == 'p':
                return {f'{k}-{random.randint(0, 50000)}': v for k, v in d.items()}
            return {k: v for k, v in d.items()}
        else:
            d[key] = dict()
            for e in value:
                d[key].update(flatten_dict(e))
    return d


def fb2_get_description_contents(description_element) -> Dict[str, list]:
    if not description_element.getchildren():
        return {re.sub(r'{.+}', '', description_element.tag): description_element.text}
    else:
        return {re.sub(r'{.+}', '', description_element.tag): list(
            map(lambda element: fb2_get_description_contents(element),
                description_element.getchildren()))}


def fb2_get_body_contents(body_element) -> list:
    if not body_element.getchildren():
        return [body_element.text]
    else:
        res = list(map(lambda element: fb2_get_body_contents(element), body_element.getchildren()))
        if body_element.text is not None:
            res.append(body_element.text)
        return res


def fb2_get_zones_contents(file_path):
    fb2_body = ''
    fb2_description = {}
    xml_root = etree.parse(file_path).getroot()
    root_children = xml_root.getchildren()

    for children in root_children:
        tag = str(children.tag)

        if tag.endswith('body'):
            fb2_body = fb2_get_body_contents(children)
        if tag.endswith('description'):
            fb2_description = fb2_get_description_contents(children)
        else:
            continue

    fb2_body = ' '.join(list(filter(lambda el: True if el is not None else False, flatten_list(fb2_body))))
    fb2_description = flatten_dict(fb2_description)

    fb2_author = fb2_description['description']['title-info']['author']
    fb2_annotation = fb2_description['description']['title-info']['annotation']
    fb2_title = fb2_description['description']['title-info']['book-title']

    author = ' '.join([v for (_, v) in fb2_author.items() if v is not None])
    annotation = ' '.join([v for (_, v) in fb2_annotation.items() if v is not None])
    title = fb2_title

    files_zones = {'body': fb2_body, 'author': author, 'annotation': annotation, 'title': title}

    return files_zones


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


def preprocess_query(query):
    query = contractions.fix(query)
    query = word_tokenize(query)
    norm_query = normalize(query)

    return norm_query


def preprocess_documents(files, folder_path):
    files_zones = {}

    for file in files:
        file_path = os.path.join(folder_path, file)
        zones = fb2_get_zones_contents(file_path)
        files_zones[file] = zones

    for file in files_zones:
        for zone in files_zones[file]:
            files_zones[file][zone] = contractions.fix(files_zones[file][zone])
            words = word_tokenize(files_zones[file][zone])
            files_zones[file][zone] = normalize(words).copy()
            words.clear()

    return files_zones
