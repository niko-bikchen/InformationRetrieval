from colorama import Fore, Style
from typing import List
import task_5.spimi as spimi
import task_5.preprocess as preprocess
from os import listdir, path
import time


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
build_index(listdir(r"D:\PyCharmWorkspace\InformationRetrieval\data\books\smalltxt"),
            r"D:\PyCharmWorkspace\InformationRetrieval\data\books\smalltxt", 300000)
print(f'{Fore.BLUE}Indexing took {time.time() - start_time} seconds{Style.RESET_ALL}')
