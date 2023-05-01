from os.path import exists
import os
import json
from elasticsearch import Elasticsearch

DEBUG = True    

class BaseIndexer:

    name= ""
    server= ""
    port= ""
    https= ""
    index_name= ""
    document_template = {}
    template_name = ""
    index_template = {}

    elastic = None

    def __init__(self, name,  server, port, https, index_name,document_template,template_name,index_template):
        self.name = name
        self.server = server
        self.port = port
        self.https = https
        self.index_name = index_name
        self.document_template = self.loadDocumentTemplate(document_template)
        self.template_name = template_name
        self.index_template = self.loadIndexTemplate(index_template)
        self.initElasticSearch(self.server, self.port, self.https)
        return

    def initElasticSearch(self, server, port, https):   
        if https:
            h = "https://" 
        else:
            h = "http://"
        self.elastic = Elasticsearch(
            hosts=[h+server+":"+str(port)],
<<<<<<< HEAD
        ssl_assert_fingerprint=os.environ.get("ssl_assert_fingerprint"),
        basic_auth=("elastic",os.environ.get("elastic_password"))
=======
            ssl_assert_fingerprint="4f79db39c521c04becaf33b2fc31683b40a9550b73687b2f0167a620ed24653c",
            basic_auth=("elastic","itrSC0xrVZh+7F6h-VVp"))
>>>>>>> develop
        self.elastic.info()
        return

    def getName(self):
        return self.name


    def getServer(self):
        return self.server

    def getPort(self):
        return self.port

    def getHttps(self):
        return self.https

    def getIndexName(self):
        return self.index_name

    def indexOneDocument(self, document):
        doc_id = document["id"]
        # Replace the values in the template dictionary with the ones from the document:
        theDoc = self.document_template.copy()
        for key in theDoc.keys():
            if theDoc[key] in document.keys():
                theDoc[key] = document[theDoc[key]]
        if DEBUG:
            print("To index:",json.dumps(theDoc))
            
        response = self.elastic.index(
            index=self.index_name,
            id=doc_id,
            document=theDoc
        )
        
        if 'acknowledged' in response:
            if response['acknowledged'] == True:
                print ("INDEX SUCCESS FOR INDEX:", response)

        # catch API error response
        elif 'error' in response:
            print ("ERROR:", response['error']['root_cause'])
            print ("TYPE:", response['error']['type'])
                
        return

    def indexAllDocuments(self,documents):
        for document in documents:
            self.indexOneDocument(document)
        return

    def createIndexTemplate(self):

        # self.elastic = Elasticsearch(hosts=["localhost"])

        response = self.elastic.indices.put_template(
            name=self.template_name,
            settings=self.index_template["settings"],
            mappings=self.index_template["mappings"],
            create = False,
            index_patterns=self.index_template["index_patterns"],
            aliases = self.index_template["aliases"],
            ignore=400
        )

        if 'acknowledged' in response:
            if response['acknowledged'] == True:
                print ("INDEX TEMPLATE SUCCESS FOR INDEX:", response)

        # catch API error response
        elif 'error' in response:
            print ("ERROR:", response['error']['root_cause'])
            print ("TYPE:", response['error']['type'])
        return

    def loadDocumentTemplate(self, document_template):
        if exists(document_template):
            with open(document_template,'r') as f:
                self.document_template = json.loads(f.read())   
        if DEBUG:
            print("Loaded document template: ",json.dumps(self.document_template))
            
        return self.document_template

    def loadIndexTemplate(self, index_template):
        if exists(index_template):
            with open(index_template,'r') as f:
                self.index_template = json.loads(f.read())   
        if DEBUG:
            print("Loaded index template: ",json.dumps(self.index_template))
            
        return self.index_template

    def fillInDocument(self,document):

        return
    
def main():
    base = BaseIndexer()
    # print(cran.getAllDocuments())

if __name__ == "__main__":
    main()
