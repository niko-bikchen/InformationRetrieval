import json
import collections
from task_7.preprocess import preprocess_query


def build_index(files_zones):
    index = {}
    files_ids = {}
    file_id = 0

    for file in files_zones:
        file_id += 1
        files_ids[file_id] = file

        for zone in files_zones[file]:
            for word in files_zones[file][zone]:
                if word in index:
                    index[word].add(f'{file_id}|{zone}')
                else:
                    index[word] = {f'{file_id}|{zone}'}

    for item in index:
        index[item] = list(index[item])

    with open('index.json', 'w') as file_handler:
        json.dump(index, file_handler, indent=2, sort_keys=True)

    with open('files_ids.json', 'w') as file_handler:
        json.dump(files_ids, file_handler, indent=2, sort_keys=True)

    return files_ids


def ranked_search(query, zones_weights):
    with open('./index.json', 'r') as file_handler:
        index = json.load(file_handler)

    with open('./files_ids.json', 'r') as file_handler:
        files_ids = json.load(file_handler)

    query = preprocess_query(query)
    index_data = []

    for word in query:
        index_data.extend(index.get(word, []))

    document_data = {}

    for item in index_data:
        document_id, document_zone = item.split('|', 1)

        if document_id in document_data:
            document_data[document_id].add(document_zone)
        else:
            document_data[document_id] = {document_zone}

    for document in document_data:
        document_score = 0

        for zone in document_data[document]:
            document_score += zones_weights[zone]

        document_data[document] = document_score
        document_score = 0

    sorted_document_data = [k for k, _ in sorted(document_data.items(), key=lambda el: el[1])]
    sorted_document_data.reverse()

    return [files_ids[document_id] for document_id in sorted_document_data]
