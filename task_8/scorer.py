import json
import math
from task_8.preprocess import preprocess_query
import numpy as np
import random


def build_index(files):
    index = {}
    files_ids = {}
    file_id = 0

    for fileName in files:
        file_id += 1
        files_ids[file_id] = fileName

        with open(fileName, 'r') as file_reader:
            for line in file_reader:
                line = line.replace('\r\n', '', 1).replace('\n', '', 1)

                for term in line.split('|'):
                    if term not in index:
                        index[term] = {file_id: 1}
                    else:
                        file = index[term].get(file_id, None)

                        if file is None:
                            index[term][file_id] = 1
                        else:
                            index[term][file_id] += 1

    with open('index.json', 'w') as file_handler:
        json.dump(index, file_handler, indent=2, sort_keys=True)

    with open('files_ids.json', 'w') as file_handler:
        json.dump(files_ids, file_handler, indent=2, sort_keys=True)

    return files_ids


def calculate_query_document_similarity(query, document, index, N):
    document_vector = []
    query_vector = []

    for term in query:
        document_vector.append(calculate_tf_idf(term, document, index, N))

    for term in query:
        term_docs = index.get(term, None)

        if term_docs is None:
            query_vector.append(0)
        else:
            df = len(term_docs.keys())
            tf = query.count(term)
            idf = math.log10(N / df)

            query_vector.append(tf - idf)

    document_vector = np.array(document_vector)
    query_vector = np.array(query_vector)

    vector_product = document_vector.dot(query_vector)

    euclidean_length_1 = calculate_euclidean_length(document_vector)
    euclidean_length_2 = calculate_euclidean_length(query_vector)
    euclidean_length_product = euclidean_length_1 * euclidean_length_2

    return vector_product / euclidean_length_product


def ranked_search(query):
    with open('./index.json', 'r') as file_handler:
        index = json.load(file_handler)
    with open('./files_ids.json', 'r') as file_handler:
        files_ids = json.load(file_handler)
    with open('./clusters.json', 'r') as file_handler:
        clusters = json.load(file_handler)

    leaders = [clusters[cluster]['leader'] for cluster in clusters]
    documents = list(files_ids.keys())
    query = preprocess_query(query)

    cosine_similarities = []

    for leader in leaders:
        cosine_similarities.append((leader, calculate_query_document_similarity(query, leader, index, len(documents))))

    cluster_scores = list(sorted(cosine_similarities, key=lambda tup: tup[1]))
    cluster_scores.reverse()

    useful_leader = cluster_scores.pop(0)
    useful_cluster = {}

    for cluster in clusters:
        if clusters[cluster]['leader'] == useful_leader[0]:
            useful_cluster = clusters[cluster]
            break
        else:
            continue

    followers_similarities = [(follower, calculate_query_document_similarity(query, follower, index, len(documents)))
                              for follower in useful_cluster['followers']]
    followers_similarities.append(useful_leader)

    result = list(sorted(followers_similarities, key=lambda tup: tup[1]))
    result.reverse()

    return list(map(lambda tup: (files_ids[tup[0]].replace('./normalized_files/', ''), tup[1]), result))


def calculate_tf_idf(term, document, index, N):
    term_docs = index.get(term, None)

    if term_docs is None:
        return 0
    else:
        df = len(term_docs.keys())
        tf = term_docs[document] if document in term_docs else 0
        idf = math.log10(N / df)

        return tf - idf


def document_to_vector(document, index, N):
    vector = []

    for term in index:
        if document not in index[term]:
            vector.append(0)
        else:
            vector.append(calculate_tf_idf(term, document, index, N))

    return vector


def calculate_euclidean_length(vector):
    sum_of_squares = 0

    for component in vector:
        sum_of_squares += component ** 2

    return math.sqrt(sum_of_squares)


def calculate_cosine_similarity(document_1, document_2, index, N):
    document_1_vector = np.array(document_to_vector(document_1, index, N))
    document_2_vector = np.array(document_to_vector(document_2, index, N))

    vector_product = document_1_vector.dot(document_2_vector)

    euclidean_length_1 = calculate_euclidean_length(document_1_vector)
    euclidean_length_2 = calculate_euclidean_length(document_2_vector)
    euclidean_length_product = euclidean_length_1 * euclidean_length_2

    return vector_product / euclidean_length_product


def find_clusters(index_path, files_ids_path):
    with open(index_path, 'r') as file_handler:
        index = json.load(file_handler)
    with open(files_ids_path, 'r') as file_handler:
        files_ids = json.load(file_handler)

    documents = list(files_ids.keys())
    clusters = {}
    cluster_id = 0

    leaders_number = math.floor(math.sqrt(len(documents)))
    followers_number = math.floor(len(documents) // leaders_number)

    leaders = list(map(str, list(random.sample(range(0, len(documents)), leaders_number))))
    followers = list(filter(lambda document: True if document not in leaders else False, documents))

    for leader in leaders:
        cluster_id += 1
        cosine_similarities = [(follower, calculate_cosine_similarity(leader, follower, index, len(files_ids.keys())))
                               for follower in
                               followers]

        sorted_similarities = list(map(lambda tup: tup[0], sorted(cosine_similarities, key=lambda tup: tup[1])))
        sorted_similarities.reverse()

        clusters[cluster_id] = {'leader': leader, 'followers': sorted_similarities[0:followers_number]}

    with open('clusters.json', 'w') as file_handler:
        json.dump(clusters, file_handler, indent=2)

    return clusters
