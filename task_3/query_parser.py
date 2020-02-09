from BTrees.OOBTree import OOBTree
from typing import List, Set
from task_3.index_builder import normalize
import re


def search_phrase_index(index: OOBTree, query: str) -> List[Set[int]]:
    words = query.split()

    # If a query consists of two words
    if len(words) == 2:
        # Just search the index
        return index.get(fr'{normalize(words.pop(0))} {normalize(words.pop(0))}', None)
    else:
        # Otherwise, split the query into pairs of words
        phrase: List[str] = []
        result: List[Set[int]] = []

        for word in words:
            # Add word to the phrase (a pair of words)
            phrase.append(normalize(word))

            # If we have two words in the phrase
            if len(phrase) == 2:
                # Search this phrase in the index
                item = index.get(fr'{phrase.pop(0)} {phrase[0]}', {})
                # Append the search result (list of file's ids) to the result
                result.append(item)

                # If we have two lists in the result
                if len(result) == 2:
                    # Intersect them
                    result.append(set(result.pop(0)).intersection(set(result.pop(0))))
                else:
                    continue
            else:
                continue

    return result


def search_coordinate_index(coord_index: OOBTree, query: str):
    # Find all ranges
    ranges = re.findall(r"#\d#", query)

    # If ranges were used
    if ranges:
        # Convert them to list of numbers
        ranges_num = [int(num.replace('#', '')) for num in ranges]
        # Split words by ranges notation
        words = re.split(r"#\d#", query)
        temp = []

        # If we have phrases in the query which consist of two words
        for index, item in enumerate(words):
            # Split them
            more_words = item.split()

            # Add a 0 range between them
            if len(more_words) >= 2:
                temp += [normalize(word) for word in more_words]
                for _ in range(0, len(more_words) - 1):
                    ranges_num.insert(index, 0)
            else:
                temp.append(normalize(item.strip()))

        words = temp.copy()
    else:
        # Otherwise, split the query by spaces
        words = list(map(lambda x: normalize(x), query.split()))
        # If we have only one word in the query
        if len(words) == 1:
            # Just search the index
            return set(coord_index.get(words.pop(), dict()).keys())
        # Add a 0 range between them
        ranges_num = [0] * (len(words) - 1)

    results: List[Set[int]] = []
    word_pair = [words.pop(0)]
    distance = ranges_num.pop(0) + 1

    first_word_dict = coord_index.get(word_pair[0], {})
    first_word_docs = first_word_dict.keys()

    # For each word in the query we search documents
    # which satisfy the range between first word in
    # the query and the second word in the query,
    # then between first word and the second and so on.
    # At the end we intersect all the documents we
    # found during the procedures described earlier.
    for word in words:
        word_pair.append(word)
        if len(word_pair) == 2:
            next_word_dict = coord_index.get(word_pair.pop(), {})
            next_word_docs = next_word_dict.keys()

            common_docs = set(first_word_docs).intersection(set(next_word_docs))
            local_result = set()

            for doc in common_docs:
                first_word_positions = first_word_dict[doc]
                next_word_positions = list(filter(lambda x: x >= min(first_word_positions), next_word_dict[doc]))

                for position_next in next_word_positions:
                    for position_first in first_word_positions:
                        # After the condition was met we break from
                        # the two for statements by using for..else
                        # statement
                        if position_next - position_first == distance:
                            local_result.add(doc)
                            break
                    else:
                        continue
                    break
            results.append(local_result)

            if ranges_num:
                distance += int(ranges_num.pop(0)) + 1
            else:
                continue
        else:
            continue

    return set.intersection(*results)
