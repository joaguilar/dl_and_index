from processors.cranQueryProcessor import CranQueryProcessor
from elasticsearch import Elasticsearch
import json
from statistics import mean 
import csv
from math import log2
import  os

OPERADOR_ELASTIC= "Elastic Default"
OPERADOR_NORMOPS= "NormOps"

ELASTIC_CSV_FILE = "datosElastic.csv"
NORMOPS_CSV_FILE = "datosNormOps.csv"
DATOS_CSV_FILE = "datos.csv"

def initElasticSearch(server, port, https):   
    if https:
        h = "https://" 
    else:
        h = "http://"
    elastic = Elasticsearch(
        hosts=[h+server+":"+str(port)],
        ssl_assert_fingerprint="4f79db39c521c04becaf33b2fc31683b40a9550b73687b2f0167a620ed24653c",
        basic_auth=("elastic","itrSC0xrVZh+7F6h-VVp"))
    print(elastic.info())
    return elastic

queriesElasticTextAcumulator = []
def runQueries(elastic,queries):
    executedQueries = {}
    
    # elastic = Elasticsearch()
    for query in queries:
        queriesElasticTextAcumulator.append(query["content"])
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
        

    print("Run Queries: "+ json.dumps(executedQueries,indent=4))
    print(response["hits"]["hits"])

    return executedQueries

queriesNormOpsTextAcumulator = []
def runNormOpsQueries(elastic,queries):
    executedQueries = {}
    
    # elastic = Elasticsearch()
    for query in queries:
        queriesNormOpsTextAcumulator.append(query["content"])
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
        break

    print("Run Queries: "+ json.dumps(executedQueries,indent=4))
    print(response["hits"]["hits"])

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
    return avgPrecision,precisionAcumulator


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
    return avgRecall,recallAcumulator


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
                f1=0
                f1Acumulator.append(f1)
                continue
            f1 = (2*p*r)/(p+r)
            f1Acumulator.append(f1)

    avgF1 = mean(f1Acumulator)
    
    return avgF1,f1Acumulator

def findDocumentAtN(docs,n):
    for key in docs:
        value = docs[key]
        if value == n:
            return key
    return None

def calculateDCGOneQuery(query_id,judgements,results):
    dcg = 0
    query_dcg = 0
    
    if query_id in results.keys():
        query_dcg = 0
        hits = int(len(results[query_id])) # up to 10 results
        for i in range(0,hits):
            theDoc = findDocumentAtN(results[query_id],i)
            #Let's check if this document is relevant to the query:
            isRelevant = False
            dcgScore = 0
            if theDoc in judgements[query_id].keys():
                isRelevant = True
                #We need to add one...
                j = i + 1
                # print("Judgement: "+str(int(judgements[query_id][theDoc])))
                # print("log2(j+1): "+str(log2(j+1)))
                dcgScore = (2**(int(judgements[query_id][theDoc]))-1)/log2(j+1)
            else:
                dcgScore = 0
            query_dcg += dcgScore

            # print("Result {} is document {}, which is{}relevant to the query, DCG at {} is {}, Total DCG = {}".format(i,theDoc," " if isRelevant else " NOT ",i,dcgScore,query_dcg))

    return query_dcg 


def findDocumentAtI(docs,n):
    return docs[n][0]

def calculateIDCGOneQuery(query_id,judgements):
    query_idcg = 0
    jugaments_ordenado = sorted(judgements[query_id].items(), key=lambda x: -int(x[1]))
    if query_id in judgements.keys():
        query_idcg = 0
        hits = 10 if int(len(judgements[query_id])) > 10 else int(len(judgements[query_id]))
        for i in range(0,hits):
            
            theDoc = findDocumentAtI(jugaments_ordenado,i)
            #Let's check if this document is relevant to the query:
            isRelevant = False
            idcgScore = 0
            if theDoc in judgements[query_id].keys():
                isRelevant = True
                #We need to add one...
                j = i + 1
                
                idcgScore = (2**(int(judgements[query_id][theDoc]))-1)/log2(j+1)
            else:
                idcgScore = 0
            query_idcg += idcgScore

            

    return query_idcg 


def calculateNDCGOneQuery(query_id,judgements,results):
    return calculateDCGOneQuery(query_id,judgements,results)/calculateIDCGOneQuery(query_id,judgements)


def calculateNDCGAllQueries(judgements,results):
    avgNDCG = 0
    NDCGAcumulator = []
    
    for query_id in judgements.keys():
        if query_id in results.keys():
            query_ndcg = calculateNDCGOneQuery(query_id,judgements,results)
            NDCGAcumulator.append(query_ndcg)
    avgNDCG = mean(NDCGAcumulator)

    return avgNDCG,NDCGAcumulator



def calculateDCGAllQueries(judgements,results):
    avgDCG = 0
    DCGAcumulator = []
    for query_id in judgements.keys():
        if query_id in results.keys():
            query_dcg = calculateDCGOneQuery(query_id,judgements,results)
            DCGAcumulator.append(query_dcg)
    avgDCG = mean(DCGAcumulator)

    return avgDCG


def calculateIDCGAllQueries(judgements,results):
    avgIDCG = 0
    IDCGAcumulator = []
    
    for query_id in judgements.keys():
        if query_id in results.keys():
            query_Idcg = calculateIDCGOneQuery(query_id,judgements)
            IDCGAcumulator.append(query_Idcg)
    avgIDCG = mean(IDCGAcumulator)

    return avgIDCG

def createCSV(nameFile):

    datos= [ ["Operador","Numero Query", "Query", "Precision","Recall","F1","NDCG","AVG Precision","AVG Recall","AVG F1","AVG NDCG"]]


    with open(nameFile, mode="w", newline="") as archivo:
        escritor = csv.writer(archivo)
        for fila in datos:
            escritor.writerow(fila)
        

def insertRowsCSV(operator,queries,judgements,nameFile):
    
    if not os.path.exists(nameFile):
        createCSV(nameFile)
    
    precision=calculatePrecisionAt10(judgements,queries)
    recall=calculateRecallAt10(judgements,queries)
    f1=calculateF1At10(judgements,queries)
    Ndcg=calculateNDCGAllQueries(judgements,queries) 

    for query_id in judgements.keys():
        if query_id in queries.keys():
            id=int(query_id)-1
            print("InserRows Ultimo Query_ID " + str(id))
            queryText=""
            queryText= queriesElasticTextAcumulator[id] if operator == OPERADOR_ELASTIC else queriesNormOpsTextAcumulator[id]
            datosQuery=[operator,query_id,queryText,precision[1][id],recall[1][id],
                        f1[1][id],Ndcg[1][id],precision[0],recall[0],
                        f1[0],Ndcg[0]
                        ]
            
            with open(nameFile, mode="a", newline="") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(datosQuery)



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
#    print(queries['200'])

    avgPrecision = calculatePrecisionAt10(judgements,queries)[0]
    print("Average Precision is {}".format(avgPrecision))

    avgRecall = calculateRecallAt10(judgements,queries)[0]
    print("Average Recall is {}".format(avgRecall))

    avgF1 = calculateF1At10(judgements,queries)[0]
    print("Average F1 is {}".format(avgF1))
    # nDCG = calculateNDCGAt10(judgements,queries)
    # calculateDCGOneQuery('1',judgements,queries)
    # calculateDCGOneQuery('200',judgements,queries)
    # calculateDCGOneQuery('8',judgements,queries)
    avgDcg = calculateDCGAllQueries(judgements,queries)    
    print("Average DCG is {}".format(avgDcg))

    avgIdcg = calculateIDCGAllQueries(judgements,queries)    
    print("Average IDCG is {}".format(avgIdcg))

    avgNdcg = calculateNDCGAllQueries(judgements,queries)[0]    
    print("Average NDCG is {}".format(avgNdcg))

    insertRowsCSV(OPERADOR_ELASTIC,queries,judgements,ELASTIC_CSV_FILE)
    




if __name__ == "__main__":
    main()
    