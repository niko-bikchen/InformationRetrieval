import sys
import time
import json
import pickle
import pprint
import task_6.spimi as spimi
import task_6.preprocess as preprocess
import task_6.vbencoder as vbencoder

from task_6.storage_manager import StorageManager
from BTrees.OOBTree import OOBTree
from colorama import Fore, Style
from typing import List
from os import listdir, path

sys.setrecursionlimit(10000)


def count_total_file_size(documents: List[str], base_path: str) -> int:
    print(f'{Fore.BLUE}'
          f'Calculating the size of the collection being indexed...'
          f'{Style.RESET_ALL}')

    total_size: int = 0

    for document in documents:
        total_size += path.getsize(fr'{base_path}\\{document}')

    print(f'{Fore.GREEN}'
          f'Calculation complete.\n'
          f'{Fore.BLUE}'
          f'Size of the collection: {total_size / 1e+6} MB\n'
          f'Number of documents: {len(documents)}\n'
          f'{Style.RESET_ALL}')

    return total_size


def build_index(documents, base_path, block_size_limit: int):
    count_total_file_size(documents, base_path)

    print(f'{Fore.BLUE}Preprocessing documents...{Style.RESET_ALL}\n')

    documents = preprocess.preprocess_documents(documents, base_path)

    print(f'{Fore.GREEN}'
          f'\nPreprocessing complete.\n'
          f'{Fore.BLUE}'
          f'Starting SPIMI indexing...\n'
          f'{Style.RESET_ALL}')

    spimi.spimi_invert(documents, block_size_limit)

    blocks = [open(fr'blocks/{block_name}', 'r') for block_name in listdir('blocks/')]

    words_count = spimi.merge_blocks(blocks)

    print(f'{Fore.GREEN}'
          f'Merging complete.\n'
          f'Index build complete.\n'
          f'{Fore.BLUE}'
          f'Words indexed: {words_count}'
          f'{Style.RESET_ALL}')


start_time = time.time()
build_index(listdir(r"D:\PyCharmWorkspace\InfoRetrival\data\books\bigtxt"),
            r"D:\PyCharmWorkspace\InfoRetrival\data\books\bigtxt", 500000)
print(f'{Fore.BLUE}Indexing took {time.time() - start_time} seconds{Style.RESET_ALL}')

with open('term_tree.pkl', 'rb') as file_handler:
    data = pickle.load(file_handler)

term_tree = OOBTree(data)
storage = StorageManager(term_tree, 0)

print(storage.find_term('half'))

# Checking how the VB encoding works

encode_nums = vbencoder.vb_encode([1, 2, 3, 4])
print(encode_nums)
print(vbencoder.vb_decode(encode_nums))

with open('../task_2/my_inverted_index.json', 'r') as handler:
    index = json.load(handler)

for key in index:
    index[key] = vbencoder.preprocess_postings(index[key])

pprint.pprint(index)

for key in index:
    index[key] = vbencoder.vb_encode(index[key])

pprint.pprint(index)

for key in index:
    index[key] = vbencoder.vb_decode(index[key])

pprint.pprint(index)