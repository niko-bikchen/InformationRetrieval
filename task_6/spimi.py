import re
import sys
import ast
from task_6.storage_manager import encode_b64, decode_b64, StorageManager
from typing import Set, Dict, List
from colorama import Fore, Style
from collections import OrderedDict


def spimi_invert(documents, block_size_limit: int) -> List[str]:
    block: Dict[str, Set[str]] = {}
    block_id: int = 0
    block_paths: List[str] = []
    storage = StorageManager()

    for index, fileId in enumerate(documents):

        print(f'{Fore.BLUE}'
              f'Processing {fileId}...'
              f'{Style.RESET_ALL}')

        for term in documents[fileId]:
            if term in block:
                block[term].add(fileId)
            else:
                block[term] = {fileId}

            storage.save_to_storage(term, fileId)

        if sys.getsizeof(block) > block_size_limit or (index == len(documents) - 1):
            print(f'{Fore.BLUE}'
                  f'Block #{block_id} exceeds size limit\n'
                  f'Commencing block saving process...'
                  f'{Style.RESET_ALL}')

            block_path = save_block(sort_terms(block), block_id)

            block_paths.append(block_path)
            block_id += 1

            block.clear()

        print(f'{Fore.GREEN}'
              f'Finished processing {fileId}\n'
              f'{Style.RESET_ALL}')

    print(f'{Fore.GREEN}'
          f'SPIMI indexing complete.\n'
          f'{Fore.BLUE}'
          f'Starting merging blocks into single index...\n'
          f'{Style.RESET_ALL}')

    del storage
    return block_paths


def save_block(block: Dict[str, Set[str]], block_id: int) -> str:
    base_path: str = r'blocks/'
    block_name: str = f'block-{block_id}.txt'

    print(f'{Fore.BLUE}'
          f'Saving block #{block_id}...'
          f'{Style.RESET_ALL}')

    with open(f'{base_path}{block_name}', 'w') as block_file:
        for term in block:
            encoded_term = encode_b64(term)
            encoded_docs = set(map(lambda doc: encode_b64(doc), list(block[term])))

            block_file.write(f'{str(encoded_term)}:{str(encoded_docs)}\n')

    print(f'{Fore.GREEN}'
          f'Finished saving block #{block_id}'
          f'{Style.RESET_ALL}')

    return fr'{base_path}{block_name}'


def merge_blocks(blocks: list):
    merge_completed = False
    spimi_index = open('index/SPIMI_inverted_index.txt', 'w')
    block_lines_buffer = OrderedDict()
    words_count = 0

    for block_index, block in enumerate(blocks):
        line = block.readline()
        line_tpl = line.split(':', 1)

        term_enc = ast.literal_eval(line_tpl[0])
        pos_set_enc = ast.literal_eval(line_tpl[1])

        term = decode_b64(term_enc)
        pos_set = set(map(lambda doc: decode_b64(doc), pos_set_enc))

        block_lines_buffer[block_index] = {term: pos_set}

    while not merge_completed:
        block_tuples = [(block_lines_buffer[block_id], block_id) for block_id in block_lines_buffer]
        smallest_tuple = min(block_tuples, key=lambda tup: list(tup[0].keys()))
        smallest_term = (list(smallest_tuple[0].keys())[0])
        smallest_term_block_ids = [block_id for block_id in block_lines_buffer if
                                   smallest_term in [term for term in block_lines_buffer[block_id]]]
        smallest_term_postings = sorted(
            sum([list(pl[smallest_term]) for pl in
                 (block_lines_buffer[block_id] for block_id in smallest_term_block_ids)],
                []))

        spimi_index.write(f'{str(smallest_term)}:{str(smallest_term_postings)}\n')
        words_count += 1

        for block_id in smallest_term_block_ids:
            block = [file for file in blocks if re.search(fr'block-{block_id}', file.name)]

            if block[0]:
                line = block[0].readline()
                if not line == '':
                    line_tpl = line.split(':', 1)

                    term_enc = ast.literal_eval(line_tpl[0])
                    pos_set_enc = ast.literal_eval(line_tpl[1])

                    term = decode_b64(term_enc)
                    postings = set(map(lambda doc: decode_b64(doc), pos_set_enc))

                    block_lines_buffer[block_id] = {term: postings}
                else:
                    del block_lines_buffer[block_id]
                    i = blocks.index(block[0])
                    blocks[i].close()
                    blocks.remove(block[0])
            else:
                i = blocks.index(block[0])
                blocks[i].close()
                blocks.remove(block[0])

        if not blocks:
            merge_completed = True

    spimi_index.close()
    return words_count


def sort_terms(block: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    print(f'{Fore.BLUE}'
          f'Sorting terms in block...'
          f'{Style.RESET_ALL}')

    sorted_terms = sorted(block.keys())
    sorted_block = OrderedDict()

    for term in sorted_terms:
        sorted_block[term] = block[term]

    print(f'{Fore.GREEN}'
          f'Finished sorting terms in block'
          f'{Style.RESET_ALL}')

    return sorted_block
