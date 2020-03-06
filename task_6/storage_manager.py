import io
import ast
import zlib
import base64
import pickle
from BTrees.OOBTree import OOBTree
from typing import Optional, Dict, Set
from colorama import Fore, Style


def encode_b64(term: str) -> bytes:
    return base64.b64encode(zlib.compress(term.encode('utf-8'), 6))


def decode_b64(term: bytes) -> str:
    return str(zlib.decompress(base64.b64decode(term)), 'utf-8')


class StorageManager(object):

    def __init__(self, tree: Optional[OOBTree] = None, serialize: int = 1):
        if tree is not None:
            self._term_tree: OOBTree = OOBTree(tree)
            self._stored_terms = len(self._term_tree.keys())
        else:
            self._term_tree: OOBTree = OOBTree()

        self._buffer: Dict[str, Set[str]] = dict()
        self._stored_terms: int = 0
        self._files_in_storage: int = 0
        self._storage_path: str = 'storage/'
        self._serialize = serialize

    def save_to_storage(self, term: str, doc: str):
        if term in self._buffer:
            self._buffer[term].add(doc)
        else:
            self._buffer[term] = {doc}

        if len(self._buffer.keys()) == 300:
            print(f'{Fore.BLUE}'
                  f'Saving terms to storage #{self._files_in_storage}...'
                  f'{Style.RESET_ALL}')

            store_name = f'store-{self._files_in_storage}.txt'

            with open(fr'{self._storage_path}{store_name}', 'w') as file_handler:
                for term in self._buffer:
                    self._stored_terms += 1

                    if term in self._term_tree:
                        self._term_tree.get(term).add(store_name)
                    else:
                        self._term_tree.insert(term, {store_name})

                    enc_term = encode_b64(term)
                    enc_postings = set(map(lambda el: encode_b64(el), self._buffer[term]))

                    file_handler.write(f'{str(enc_term)}:{str(enc_postings)}\n')

            self._files_in_storage += 1
            self._buffer.clear()

            print(f'{Fore.GREEN}'
                  f'Finished saving terms\n'
                  f'{Style.RESET_ALL}')

    def find_term(self, term: str) -> Set[str]:
        stores: Set[str] = self._term_tree[term]
        postings: Set[str] = set()

        for store in stores:
            with open(fr'{self._storage_path}{store}') as file_handler:
                for line in file_handler:
                    line_tpl = line.split(':', 1)

                    enc_term = ast.literal_eval(line_tpl[0])
                    enc_postings = ast.literal_eval(line_tpl[1])

                    dec_term = decode_b64(enc_term)
                    dec_postings = set(map(lambda el: decode_b64(el), enc_postings))

                    if dec_term == term:
                        postings = postings.union(dec_postings)
                    else:
                        continue

        return postings

    def __del__(self):
        if self._serialize == 1:
            print(f'{Fore.BLUE}'
                  f'Serializing term tree...'
                  f'{Style.RESET_ALL}')

            pickle.dump(self._term_tree, io.open('term_tree.pkl', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

            print(f'{Fore.GREEN}'
                  f'Finished serializing term tree\n'
                  f'{Style.RESET_ALL}')
