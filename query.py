import requests
import json
from elasticsearch import Elasticsearch
from nltk.tokenize import sent_tokenize 


def main():
    es = Elasticsearch(hosts=["http://localhost:9200"])

    q = input("Enter Your Query: ")

    # sentences = sent_tokenize(q)
    sentences =[]
    sentences.append(q)
    print (sentences)
    #TODO: Get the sentence vectors
    
    vector = []
    print(vector)
    knn_query = {
            "field": "sentence-vector",
            "query_vector": vector,
            "k": 10,
            "num_candidates": 100
    }

    # qs = {
    #     "query": {
    #         "has_child": {
    #             "type": "sentence",
    #             "query": {
    #                 "match": {
    #                     "sentence": q
    #                 }
    #             },
    #             "inner_hits": {
    #             },
    #             "knn":{
    #                 "field": "sentence-vector",
    #                 "query_vector": vector,
    #                 "k": 10,
    #                 "num_candidates": 100        
    #             }
    #         }
    #     },   
    # }


    qs = {
          "query": {
            "script_score": {
            "query": {
                "match": {
                "sentence": q
                }
            },
            "script": {
                "source": """
                double value = doc['sentence-vector'].size() == 0 ? 0 : dotProduct(params.query_vector, 'sentence-vector');
                return sigmoid(1, Math.E, -value); 
                """,
                "params": {"query_vector":vector}}
                }
            },
            "_source": ["title","sentence"]
    }   

    print("=======================")
    print(json.dumps(qs))
    print("=======================")

    r = es.search(
        index="articles-cran",
        query=qs,

    )

    print(r)

if __name__ == "__main__":
    main()
