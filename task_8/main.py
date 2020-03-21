import os
from task_8.preprocess import preprocess_documents
from task_8.scorer import build_index, find_clusters, ranked_search

# preprocess_documents(os.listdir(r"D:\PyCharmWorkspace\InfoRetrival\data\books\bigtxt"),
#                      r"D:\PyCharmWorkspace\InfoRetrival\data\books\bigtxt")
# build_index([fr'./normalized_files/{file}' for file in os.listdir('./normalized_files')])
# find_clusters(r'./index.json', r'./files_ids.json')
print(ranked_search("listening for the clock"))
