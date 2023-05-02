from processors.cranQueryProcessor import CranQueryProcessor
from processors.medlineQueryProcessor import MedlineQueryProcessor
from processors.timeQueryProcessor import TimeQueryProcessor
from elasticsearch import Elasticsearch
import json
from statistics import mean 
import csv
from math import log2
import  os
import nltk
from nltk.tokenize import word_tokenize 
from enum import Enum


#Constants
OPERADOR_ELASTIC= "Elastic Default"
OPERADOR_NORMOPS= "NormOps"

ELASTIC_CRAN_CSV_FILE = "datosElastic_cran.csv"
NORMOPS_CRAN_CSV_FILE = "datosNormOps_cran.csv"
ELASTIC_MIDLE_CSV_FILE = "datosElastic_medline.csv"
NORMOPS_MIDLE_CSV_FILE = "datosNormOps_medline.csv"
ELASTIC_TIME_CSV_FILE = "datosElastic_time.csv"
NORMOPS_TIME_CSV_FILE = "datosNormOps_time.csv"
DATOS_CSV_FILE = "datos.csv"

class DocDataNorm(Enum):
    SIGMOID= "SIGMOID"
    HALF_SIGMOID= "HALF-SIGMOID"

class DocData(Enum):
    TF = "TF"
    BM25TF= "BM25TF"

class Weigth(Enum):
    IDF="IDF"
    BM25IDF="BM25IDF"

class InputWeigthNorm(Enum):
    SUM="SUM"
    MAX ="MAX"
    MAG="MAG"
    T_SCORE="T-SCORE"
    SOFTMAX="SOFTMAX"
    NONE="NONE"

class Function(Enum):
    AVG="AVG"
    PROB="PROB"
    MAX="MAX"
    SUM="SUM"
    MUL="MUL"





def initElasticSearch(server, port, https):   
    if https:
        h = "https://" 
    else:
        h = "http://"
    elastic = Elasticsearch(
        hosts=[h+server+":"+str(port)],
        ssl_assert_fingerprint=os.environ.get("ssl_assert_fingerprint"),
        basic_auth=("elastic",os.environ.get("elastic_password")))
    print(elastic.info())
    return elastic

queriesElasticTextAcumulator = []
scoresValuesElastic={}
def runQueries(elastic,queries, index):
    executedQueries = {}
    
    # elastic = Elasticsearch()
    for query in queries:
        queriesElasticTextAcumulator.append(query["content"])
        response = elastic.search(
            index=index,
            query={
                "match": {
                    "full_text": {
                        "query": query["content"]
                    }
                }
            },
            size=10
        )

        pos = 0
        for hit in response["hits"]["hits"]:
            scoresValuesElastic[query["id"]]=hit["_score"]
            if query["id"] in executedQueries.keys():
                executedQueries[query["id"]][hit["_id"]] = pos
            else:
                executedQueries[query["id"]]={hit["_id"]: pos}
            pos += 1
        

    #print("Run Queries: "+ json.dumps(executedQueries,indent=4))
    print(response["hits"]["hits"])

    return executedQueries


valuesQueryClauses=[]
def setvaluesQueryClauses(filedName,idField,docData,docDataNorm,weigth,max,power):
   valuesQueryClauses.append([filedName,idField,docData,docDataNorm,weigth,str(max),str(power)])

def createClauses(words,filedName,idField,docData,docDataNorm,weigth,max,power):

    clauses=[]
    #print("PUREBA NLTK "+ json.dumps(words,indent=2))
    setvaluesQueryClauses(filedName,idField,docData,docDataNorm,weigth,max,power)

    for i in range(0,len(words)-1):

        clauses.append(
             {
                "normTerm": {
                    "fieldName": filedName,
                    "term": words[i],
                    "idfField": idField,
                    "docData": docData,
                    "docDataNorm": docDataNorm,
                    "max": str(max),
                    "weight": weigth,
                    "power": str(power)
                }

            }
        )

    return clauses

valuesQueryNormOps=[]
def setvaluesQueryNormOps(indexData,normWeight,nomrTreshold,normMinClauses,normInputWeight,normFunction):
   valuesQueryNormOps.append([indexData,str(normWeight),str(nomrTreshold),str(normMinClauses),normInputWeight,normFunction])


queriesNormOpsTextAcumulator = []
scoresValuesNormOps={}
def runNormOpsQueries(elastic,queries,indexData,weight,treshold,minClauses,inputWeigthNorm,function,filedName_clauses,idField_clauses,docData_clauses,docDataNorm_clauses,weigth_clauses,max_clauses,power_clauses):
    executedQueries = {}
    
    
    # elastic = Elasticsearch()
    for query in queries:
        setvaluesQueryNormOps(indexData,weight,treshold,minClauses,inputWeigthNorm,function)
        queriesNormOpsTextAcumulator.append(query["content"])
        words = word_tokenize(query["content"])
        response = elastic.search(
            index=indexData,
            query={
                "normOr": {
                    "weight": weight,
                    "threshold": treshold,
                    "minClauses": minClauses,
                    "inputWeightNorm": inputWeigthNorm,
                    "function": function,
                    "clauses": createClauses(words,filedName_clauses,idField_clauses,docData_clauses,docDataNorm_clauses,weigth_clauses,max_clauses,power_clauses)

                }#end normOPs
            },
            size=10
        )

        

        pos = 0
        for hit in response["hits"]["hits"]:
            scoresValuesNormOps[query["id"]]=hit["_score"]
            if query["id"] in executedQueries.keys():
                executedQueries[query["id"]][hit["_id"]] = pos
            else:
                executedQueries[query["id"]]={hit["_id"]: pos}
            pos += 1
        #break

    # print("Run Queries: "+ json.dumps(executedQueries,indent=4))
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
        precision = calculatePrecisionOneQuery(query_id,judgements,results)
        if precision == -1:
            continue # We don't calculate for queries that are not available
        precisionAcumulator.append(precision)

    avgPrecision = mean(precisionAcumulator) if len(precisionAcumulator) != 0 else 0
    return avgPrecision,precisionAcumulator


def calculateRecallOneQuery(query_id,judgements,results):
    recall = 0
    relevant_found = 0 # relevant documents found out of 10
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
        recall = calculateRecallOneQuery(query_id,judgements,results)
        if recall == -1:
            continue
        recallAcumulator.append(recall)

    avgRecall = mean(recallAcumulator) if len(recallAcumulator) != 0 else 0
    return avgRecall,recallAcumulator


def calculateF1At10(judgements,results):
    avgF1 = 0
    f1Acumulator = []
    
    for query_id in judgements.keys():
      
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

    avgF1 = mean(f1Acumulator) if len(f1Acumulator) != 0 else 0
    
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
    avgNDCG = mean(NDCGAcumulator) if len(NDCGAcumulator) != 0 else 0

    return avgNDCG,NDCGAcumulator



def calculateDCGAllQueries(judgements,results):
    avgDCG = 0
    DCGAcumulator = []
    for query_id in judgements.keys():
        if query_id in results.keys():
            query_dcg = calculateDCGOneQuery(query_id,judgements,results)
            DCGAcumulator.append(query_dcg)
    avgDCG = mean(DCGAcumulator) if len(DCGAcumulator) != 0 else 0

    return avgDCG


def calculateIDCGAllQueries(judgements,results):
    avgIDCG = 0
    IDCGAcumulator = []
    
    for query_id in judgements.keys():
        if query_id in results.keys():
            query_Idcg = calculateIDCGOneQuery(query_id,judgements)
            IDCGAcumulator.append(query_Idcg)
    avgIDCG = mean(IDCGAcumulator) if len(IDCGAcumulator) != 0 else 0

    return avgIDCG

def createCSV(nameFile):

    datos= [ ["Operador","Numero Query", "Query","Score", "Precision","Recall","F1","NDCG","AVG Precision","AVG Recall","AVG F1","AVG NDCG",
              "IndexData","Weigth_NormOps","Treshold_NormOps","Min Clauses_NormOps","Input WeigthNorm","Function_NormOps",
              "FieldName_Clauses","IdField_clauses","DocData_clauses","DocDataNorm_clauses","Weigth_clauses","Max_clauses","Power_clauses"]]


    with open(nameFile, mode="w", newline="") as archivo:
        escritor = csv.writer(archivo)
        for fila in datos:
            escritor.writerow(fila)
        

def insertRowsCSV(operator,queries,judgements,nameFile):
    
    if  os.path.exists(nameFile):
        os.remove(nameFile)
    
    createCSV(nameFile)
    
    precision=calculatePrecisionAt10(judgements,queries)
    recall=calculateRecallAt10(judgements,queries)
    f1=calculateF1At10(judgements,queries)
    Ndcg=calculateNDCGAllQueries(judgements,queries) 

    for query_id in judgements.keys():
        if query_id in queries.keys():
            id=int(query_id)-1
            #print("InserRows Ultimo Query_ID " + str(id))
            queryText=""
            try:
                queryText= queriesElasticTextAcumulator[id] if operator == OPERADOR_ELASTIC else queriesNormOpsTextAcumulator[id]
                score= scoresValuesElastic[query_id]  if operator == OPERADOR_ELASTIC else scoresValuesNormOps[query_id]
                datosQuery=[operator,query_id,queryText,score,precision[1][id],recall[1][id],
                            f1[1][id],Ndcg[1][id],precision[0],recall[0],f1[0],Ndcg[0]
                            ]
                
                if operator == OPERADOR_NORMOPS:
                    datosExtra=[valuesQueryNormOps[id][0],valuesQueryNormOps[id][1],valuesQueryNormOps[id][2],
                                valuesQueryNormOps[id][3],valuesQueryNormOps[id][4],valuesQueryNormOps[id][5],
                                valuesQueryClauses[id][0],valuesQueryClauses[id][1],valuesQueryClauses[id][2],
                                valuesQueryClauses[id][3],valuesQueryClauses[id][4],valuesQueryClauses[id][5],
                                valuesQueryClauses[id][6]
                                ]
                    for i in range(0,len(datosExtra)):
                        datosQuery.append(datosExtra[i])
                
                with open(nameFile, mode="a", newline="") as archivo:
                    escritor = csv.writer(archivo)
                    escritor.writerow(datosQuery)

            except IndexError:
                print("No encontro valores para la query: "+str(query_id))
                continue



def main():
    #Index cran dataset for now

    nltk.download('punkt')
    

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

    queries = runQueries(elastic,documents,"cran")
    queries_norm = runNormOpsQueries(elastic,documents,"cran",2.0,0.5,5,InputWeigthNorm.SUM.value,Function.AVG.value,"content","content",DocData.TF.value,DocDataNorm.SIGMOID.value,Weigth.IDF.value,5,1)
    
    print("------------------CRAN---------------------------")

    print("Values Elastic Operator in CRAN")

    avgPrecision = calculatePrecisionAt10(judgements,queries)[0]
    print("Average Precision is {}".format(avgPrecision))

    avgRecall = calculateRecallAt10(judgements,queries)[0]
    print("Average Recall is {}".format(avgRecall))

    avgF1 = calculateF1At10(judgements,queries)[0]
    print("Average F1 is {}".format(avgF1))
    
    avgDcg = calculateDCGAllQueries(judgements,queries)    
    print("Average DCG is {}".format(avgDcg))

    avgIdcg = calculateIDCGAllQueries(judgements,queries)    
    print("Average IDCG is {}".format(avgIdcg))

    avgNdcg = calculateNDCGAllQueries(judgements,queries)[0]    
    print("Average NDCG is {}".format(avgNdcg))

    print("-------------------------------------------------------")

    print("Values NormOps Operator in CRAN")

    avgPrecision = calculatePrecisionAt10(judgements,queries_norm)[0]
    print("Average Precision is {}".format(avgPrecision))

    avgRecall = calculateRecallAt10(judgements,queries_norm)[0]
    print("Average Recall is {}".format(avgRecall))

    avgF1 = calculateF1At10(judgements,queries_norm)[0]
    print("Average F1 is {}".format(avgF1))
    
    avgDcg = calculateDCGAllQueries(judgements,queries_norm)    
    print("Average DCG is {}".format(avgDcg))

    avgIdcg = calculateIDCGAllQueries(judgements,queries_norm)    
    print("Average IDCG is {}".format(avgIdcg))

    avgNdcg = calculateNDCGAllQueries(judgements,queries_norm)[0]    
    print("Average NDCG is {}".format(avgNdcg))


    ##create csv
    print("Create CSV to CRAN "+OPERADOR_ELASTIC)
    insertRowsCSV(OPERADOR_ELASTIC,queries,judgements,ELASTIC_CRAN_CSV_FILE)
    print("Create CSV to CRAN "+OPERADOR_NORMOPS)
    insertRowsCSV(OPERADOR_NORMOPS,queries_norm,judgements,NORMOPS_CRAN_CSV_FILE)
    

    # Medline

    print("------------------MEDLINE---------------------------")

    medProcessor =  MedlineQueryProcessor()
    meddocuments = medProcessor.getAllDocuments()
    medjudgements = medProcessor.getJudgements()

    medqueries = runQueries(elastic,meddocuments,"medline")
    medqueries_norm=runNormOpsQueries(elastic,meddocuments,"medline",2.0,0.5,5,InputWeigthNorm.SUM.value,Function.AVG.value,"content","content",DocData.TF.value,DocDataNorm.SIGMOID.value,Weigth.IDF.value,5,1)

    print("Medline Queries executed with results: {}".format(len(medqueries)))
    print(medqueries['1'])

    print("Values Elastic Operator in Midle")

    avgPrecision = calculatePrecisionAt10(medjudgements,medqueries)[0]
    print("Average Precision is {}".format(avgPrecision))

    avgRecall = calculateRecallAt10(medjudgements,medqueries)[0]
    print("Average Recall is {}".format(avgRecall))

    avgF1 = calculateF1At10(medjudgements,medqueries)[0]
    print("Average F1 is {}".format(avgF1))

    avgDcg = calculateDCGAllQueries(medjudgements,medqueries)    
    print("Average DCG is {}".format(avgDcg))

    avgIdcg = calculateIDCGAllQueries(medjudgements,medqueries)    
    print("Average IDCG is {}".format(avgIdcg))

    avgNdcg = calculateNDCGAllQueries(medjudgements,medqueries)[0]    
    print("Average NDCG is {}".format(avgNdcg))

    print("-------------------------------------------------------")

    
    print("Values NormOps in Midle")

    avgPrecision = calculatePrecisionAt10(medjudgements,medqueries_norm)[0]
    print("Average Precision is {}".format(avgPrecision))

    avgRecall = calculateRecallAt10(medjudgements,medqueries_norm)[0]
    print("Average Recall is {}".format(avgRecall))

    avgF1 = calculateF1At10(medjudgements,medqueries_norm)[0]
    print("Average F1 is {}".format(avgF1))

    avgDcg = calculateDCGAllQueries(medjudgements,medqueries_norm)    
    print("Average DCG is {}".format(avgDcg))

    avgIdcg = calculateIDCGAllQueries(medjudgements,medqueries_norm)    
    print("Average IDCG is {}".format(avgIdcg))

    avgNdcg = calculateNDCGAllQueries(medjudgements,medqueries_norm)[0]    
    print("Average NDCG is {}".format(avgNdcg))

    print("Create CSV to Midle "+OPERADOR_ELASTIC)
    insertRowsCSV(OPERADOR_ELASTIC,medqueries,medjudgements,ELASTIC_MIDLE_CSV_FILE)
    print("Create CSV to Midle "+OPERADOR_NORMOPS)
    insertRowsCSV(OPERADOR_NORMOPS,medqueries_norm,medjudgements,NORMOPS_MIDLE_CSV_FILE)

    
    #Time

    print("------------------TIME---------------------------")

    timeProcessor =  TimeQueryProcessor()
    timedocuments = timeProcessor.getAllDocuments()
    timejudgements = timeProcessor.getJudgements()

    timequeries = runQueries(elastic,timedocuments,"time")
    timequeries_norm=runNormOpsQueries(elastic,timedocuments,"time",2.0,0.5,5,InputWeigthNorm.SUM.value,Function.AVG.value,"content","content",DocData.TF.value,DocDataNorm.SIGMOID.value,Weigth.IDF.value,5,1)

    print("Time Queries executed with results: {}".format(len(timequeries)))
    print(timequeries['1'])

    print("Values Elastic Operator in Time")

    avgPrecision = calculatePrecisionAt10(timejudgements,timequeries)[0]
    print("Average Precision is {}".format(avgPrecision))

    avgRecall = calculateRecallAt10(timejudgements,timequeries)[0]
    print("Average Recall is {}".format(avgRecall))

    avgF1 = calculateF1At10(timejudgements,timequeries)[0]
    print("Average F1 is {}".format(avgF1))

    avgDcg = calculateDCGAllQueries(timejudgements,timequeries)    
    print("Average DCG is {}".format(avgDcg))

    avgIdcg = calculateIDCGAllQueries(timejudgements,timequeries)    
    print("Average IDCG is {}".format(avgIdcg))

    avgNdcg = calculateNDCGAllQueries(timejudgements,timequeries)[0]    
    print("Average NDCG is {}".format(avgNdcg))

    print("-------------------------------------------------------")

    
    # print("Values NormOps in Time")

    # avgPrecision = calculatePrecisionAt10(timejudgements,timequeries_norm)[0]
    # print("Average Precision is {}".format(avgPrecision))

    # avgRecall = calculateRecallAt10(timejudgements,timequeries_norm)[0]
    # print("Average Recall is {}".format(avgRecall))

    # avgF1 = calculateF1At10(timejudgements,timequeries_norm)[0]
    # print("Average F1 is {}".format(avgF1))

    # avgDcg = calculateDCGAllQueries(timejudgements,timequeries_norm)    
    # print("Average DCG is {}".format(avgDcg))

    # avgIdcg = calculateIDCGAllQueries(timejudgements,timequeries_norm)    
    # print("Average IDCG is {}".format(avgIdcg))

    # avgNdcg = calculateNDCGAllQueries(timejudgements,timequeries_norm)[0]    
    # print("Average NDCG is {}".format(avgNdcg))

    print("Create CSV to Time "+OPERADOR_ELASTIC)
    insertRowsCSV(OPERADOR_ELASTIC,timequeries,timejudgements,ELASTIC_TIME_CSV_FILE)
    # print("Create CSV to Time "+OPERADOR_NORMOPS)
    # insertRowsCSV(OPERADOR_NORMOPS,timequeries_norm,timejudgements,NORMOPS_TIME_CSV_FILE) 



if __name__ == "__main__":
    main()
    