from BTrees.OOBTree import OOBTree
import json
import task_3.index_builder as ib
import task_3.query_parser as qp
import my_modules.file_handler as fh

# Creates phrase index and prints out number of phrases
# index, _ = ib.phrase_index(fh.files_in_dir(r'D:\PyCharmWorkspace\InfoRetrival\data\books\midtxt'), True)
# print(len(index))

# Creates coordinate index and prints out number of phrases
# index, _ = ib.coordinate_index(fh.files_in_dir(r'D:\PyCharmWorkspace\InfoRetrival\data\books\midtxt'), True)
# print(len(index))

# Reads file with phrase index and saves it into a variable
# with open('phrase_index.json', 'r') as handler:
#     data = json.load(handler)

# Reads file with coordinate index and saves it into a variable
with open('coordinate_index.json', 'r') as handler:
    data = json.load(handler)

# Creating BTree from the index read from file
index = OOBTree()
index.update(data)

# Search functions
# print(qp.search_phrase_index(index, 'THE LEECH AND HIS PATIENT'))
print(qp.search_coordinate_index(index, 'Prynne #20# Pearl'))
