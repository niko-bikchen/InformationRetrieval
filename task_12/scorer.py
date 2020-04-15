import pickle
import json
from task_12.preprocess import preprocess_query
from rank_bm25 import BM25Okapi


def build_corpus(files):
    corpus = []
    aggregator = []

    for fileName in files:
        with open(fileName, 'r') as file_reader:
            for line in file_reader:
                for word in line.split('|'):
                    aggregator.append(word)
            corpus.append(aggregator.copy())
            aggregator.clear()

    with open('corpus.json', 'w') as file_handler:
        json.dump(corpus, file_handler, indent=2)

    with open('bm25_okapi.pickle', 'wb') as pickle_handler:
        pickle.dump(BM25Okapi(corpus), pickle_handler)

    return files


def ranked_search(query, documents):
    query = preprocess_query(query)

    with open('bm25_okapi.pickle', 'rb') as pickle_handler:
        bm25 = pickle.load(pickle_handler)

    documents_scores = bm25.get_scores(query)

    result = list(zip(documents, documents_scores))
    result_sorted = list(sorted(result, key=lambda tup: tup[1]))
    result_sorted.reverse()

    return result_sorted
