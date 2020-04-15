import os
from task_12.preprocess import preprocess_documents
from task_12.scorer import build_corpus, ranked_search

# preprocess_documents(os.listdir(r"D:\PyCharmWorkspace\InformationRetrieval\data\books\bigtxt"),
#                      r"D:\PyCharmWorkspace\InformationRetrieval\data\books\bigtxt")

dir_contents = os.listdir('./normalized_files')
# build_corpus([fr'./normalized_files/{file}' for file in dir_contents])


print(ranked_search("born in Saratoga county January 23, 1821", dir_contents))
