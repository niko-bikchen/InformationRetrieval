import my_modules.file_handler as fh
import task_4.index_builder as ib
import task_4.query_parser as qp
import pickle
import json
from BTrees.OOBTree import OOBTree

# ib.build_term_tree(fh.files_in_dir(r'D:\PyCharmWorkspace\InfoRetrival\data\books\smalltxt'), serialize=True)

# index = ib.transposition_index(fh.files_in_dir(r'D:\PyCharmWorkspace\InfoRetrival\data\books\smalltxt'),
#                                save_to_file=True)
# print(len(index.keys()))

index = ib.three_gram_index(fh.files_in_dir(r'D:\PyCharmWorkspace\InfoRetrival\data\books\midtxt'),
                            save_to_file=True)
print(len(index.keys()))

with open('three_gram_index.json', 'r') as handler:
    data = json.load(handler)

gram_index = OOBTree()
gram_index.update(data)

with open('../task_2/my_inverted_index.json', 'r') as handler:
    data = json.load(handler)

doc_index = OOBTree()
doc_index.update(data)

print(qp.search_with_joker(doc_index, gram_index, 'th*'))
