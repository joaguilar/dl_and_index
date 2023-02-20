from processors.cranQueryProcessor import CranQueryProcessor
from elasticsearch import Elasticsearch
import json
from statistics import mean 
import csv

def initElasticSearch(server, port, https):   
    if https:
        h = "https://" 
    else:
        h = "http://"
    elastic = Elasticsearch(
        hosts=[h+server+":"+str(port)],
        ssl_assert_fingerprint="ec7271bc5116b6c27d595af549090f6176189b20ee64d80a5d2f1de712997ae1",
        basic_auth=("elastic","a4JP3X56d3N5vsgUXsR="))
    print(elastic.info())
    return elastic

def runQueries(elastic,queries):
    executedQueries = {}
    # elastic = Elasticsearch()
    for query in queries:
        response = elastic.search(
            index="cran",
            query={
                "match": {
                    "full_text": {
                        "query": query["content"]
                    }
                }
            },
            size=10
        )

        #We want this:
            # [
            #     {
            #         "query_id": {
            #             "doc_id": "pos",
            #             "doc_id": "pos",
            #             ...
            #         }
            #     }
            # ]

        pos = 0
        for hit in response["hits"]["hits"]:
            if query["id"] in executedQueries.keys():
                executedQueries[query["id"]][hit["_id"]] = pos
            else:
                executedQueries[query["id"]]={hit["_id"]: pos}
            pos += 1

        # print(response["hits"]["hits"])

    return executedQueries

def calculatePrecisionOneQuery(query_id,judgements,results):
    precision = 0
    relevant_found = 0 # relevant documents found out of 10
    total_found = 0
    #Compare which documents were returned in the results dictionary with the relevant ones:
    if query_id in results.keys():
        result_docs = results[query_id]
        for doc_id in result_docs.keys():
            if doc_id in judgements[query_id]:
                relevant_found += 1
            total_found += 1 #Number of documents returned
        precision = relevant_found / total_found
    else:
        return -1
    return precision

def calculatePrecisionAt10(judgements,results):
    avgPrecision = 0
    precisionAcumulator = []
    precision = 0

    for query_id in judgements.keys():
        # precision = 0
        # relevant_found = 0 # relevant documents found out of 10
        # total_found = 0
        # #Compare which documents were returned in the results dictionary with the relevant ones:
        # if query_id in results.keys():
        #     result_docs = results[query_id]
        #     for doc_id in result_docs.keys():
        #         if doc_id in judgements[query_id]:
        #             relevant_found += 1
        #         total_found += 1 #Number of documents returned
            # precision = relevant_found / total_found
        precision = calculatePrecisionOneQuery(query_id,judgements,results)
        if precision == -1:
            continue # We don't calculate for queries that are not available
        precisionAcumulator.append(precision)

    avgPrecision = mean(precisionAcumulator)
    return avgPrecision


def calculateRecallOneQuery(query_id,judgements,results):
    recall = 0
    relevant_found = 0 # relevant documents found out of 10
    total_found = 0
    #Compare which documents were returned in the results dictionary out of the relevant ones:
    if query_id in results.keys():
        total_relevant = min(len(judgements[query_id]),10)
        result_docs = results[query_id]
        for doc_id in result_docs.keys():
            if doc_id in judgements[query_id]:
                relevant_found += 1
            
        recall = relevant_found / total_relevant
    else:
        return -1
    return recall

def calculateRecallAt10(judgements,results):
    avgRecall = 0
    recallAcumulator = []
    
    for query_id in judgements.keys():
        recall = 0
        relevant_found = 0 # relevant documents found out of 10
        total_found = 0
        #Compare which documents were returned in the results dictionary out of the relevant ones:
        # if query_id in results.keys():
        #     total_relevant = min(len(judgements[query_id]),10)
        #     result_docs = results[query_id]
        #     for doc_id in result_docs.keys():
        #         if doc_id in judgements[query_id]:
        #             relevant_found += 1
                
        #     recall = relevant_found / total_relevant
        recall = calculateRecallOneQuery(query_id,judgements,results)
        if recall == -1:
            continue
        recallAcumulator.append(recall)

    avgRecall = mean(recallAcumulator)
    return avgRecall


def calculateF1At10(judgements,results):
    avgF1 = 0
    f1Acumulator = []
    
    for query_id in judgements.keys():
        precision = 0
        relevant_found = 0 # relevant documents found out of 10
        total_found = 0
        #Compare which documents were returned in the results dictionary with the relevant ones:
        if query_id in results.keys():
            p = calculatePrecisionOneQuery(query_id,judgements,results)
            r = calculateRecallOneQuery(query_id,judgements,results)
            if p == 0 and r ==0:
                continue
            f1 = (2*p*r)/(p+r)
            f1Acumulator.append(f1)
    avgF1 = mean(f1Acumulator)
    return avgF1

def main():
    #Index cran dataset for now

    processor = CranQueryProcessor()

    documents = processor.getAllDocuments()
    print ("Loaded {} documents from the Cran collection.".format(len(documents)))
    print(documents[0])
    print(documents[1])
    judgements = processor.getJudgements()

    print("Judgements loaded: {}".format(len(judgements)))

    print(judgements['1'])
    print(judgements['200'])

    elastic = initElasticSearch("localhost","9200",True)

    queries = runQueries(elastic,documents)

    print("Queries executed with results: {}".format(len(queries)))

    print(queries['1'])
    print(queries['200'])

    precision = calculatePrecisionAt10(judgements,queries)
    print("Average Precision is {}".format(precision))
    recall = calculateRecallAt10(judgements,queries)
    print("Average Recall is {}".format(recall))
    f1 = calculateF1At10(judgements,queries)
    print("Average F1 is {}".format(f1))
    # nDCG = calculateNDCGAt10(judgements,queries)



if __name__ == "__main__":
    main()
    