from typing import List, Set
from BTrees.OOBTree import OOBTree
import re
from colorama import Fore, Style
from task_3.index_builder import normalize


def get_all_words(tree: OOBTree, words: List[str] = None, word: str = '') -> List[str]:
    if words is None:
        words = []

    for key in tree.keys():
        if key == '^':
            words.append(word + key)
            continue
        else:
            get_all_words(tree.get(key), words, word + key)

    return words


def get_words_by_joker(doc_index: OOBTree, gram_index: OOBTree, query: str) -> Set[str]:
    query: str = query.replace('*', '')
    words: Set[str] = set()

    if len(query) > 3:
        queries: List[str] = [query[i:i + 3] for i in range(len(query) - 2)]
        words = set(gram_index.get(queries.pop(0), []))

        for item in queries:
            words = words.intersection(set(gram_index.get(item, [])))
    elif len(query) == 3:
        words: Set[str] = set(gram_index.get(query, []))
    elif len(query) == 2:
        print(
            f'{Fore.YELLOW}'
            f'WARNING: One letter query with a joker'
            f' may process longer than queries '
            f'which have more letters.'
            f'{Style.RESET_ALL}'
        )

        for key in gram_index:
            if query in key:
                words.update(gram_index.get(key, []))
            else:
                continue
    else:
        return set()

    if query.index('^') == 0:
        words = set(filter(lambda x: x.startswith(query.replace('^', '')), words))
    else:
        words = set(filter(lambda x: x.endswith(query.replace('^', '')), words))

    return words


def search_with_joker(doc_index: OOBTree, gram_index: OOBTree, query: str) -> Set[str]:
    jokers: List[str] = re.findall(r'\*', query)
    docs: Set[str] = set()
    words: Set[str] = set()

    if len(jokers) == 1:
        index: int = query.index('*')

        if index == 0:
            words = get_words_by_joker(doc_index, gram_index, f'{query}^')

        elif index == len(query) - 1:
            words = get_words_by_joker(doc_index, gram_index, f'^{query}')
        else:
            split_query = query.split('*')

            a: Set[str] = get_words_by_joker(doc_index, gram_index, f'^{split_query[0]}')
            b: Set[str] = get_words_by_joker(doc_index, gram_index, f'{split_query[1]}^')

            words = a.intersection(b)
    elif len(jokers) == 2:
        split_query = query.split('*')

        a: Set[str] = get_words_by_joker(doc_index, gram_index, f'^{split_query[0]}')
        b: Set[str] = get_words_by_joker(doc_index, gram_index, f'{split_query[2]}^')

        words = a.intersection(b)

        words = set(filter(lambda x: True if split_query[1] in x else False, words))
    else:
        print(
            f'{Fore.RED}'
            f'ERROR: Queries with three jokers are not supported.'
            f'{Style.RESET_ALL}'
        )

    for word in words:
        docs.update(doc_index.get(normalize(word), []))

    return docs
