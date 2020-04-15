import os
import pprint
from task_7.preprocess import preprocess_documents
from task_7.ranger import build_index, ranked_search

DIR_PATH = os.path.abspath('../data/books/fb2')

# files_zones = preprocess_documents(os.listdir(DIR_PATH), DIR_PATH)
# ids_map = build_index(files_zones)

pprint.pprint(ranked_search('courage and honour', {'body': 0.1, 'author': 0.2, 'title': 0.4, 'annotation': 0.3}))
