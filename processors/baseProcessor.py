
DEBUG = True

class BaseProcessor:

    query_file = ""
    document_file = ""
    position_in_doc = 0 #Position of the line to read in the document
    documents = []

    def __init__(self, queryfile, documentfile):
        self.query_file = queryfile
        self.document_file = documentfile
        self.documents = []
        return

    def getQueryFile(self):
        return self.query_file

    def getDocumentsFile(self):
        return self.document_file

    def resetDocument(self):
        self.position_in_doc=0
        return self.position_in_doc

    def getNextDocument(self):
        if len(self.documents) == 0:
            #Load the documents:
            if DEBUG:
                print ("Loading all documents...")
            self.documents = self.getAllDocuments()
            #Position is 0
            self.position_in_doc = 0
            if DEBUG:
                    print ("{} Documents loaded. Done...".format(len(self.documents)))
        if len(self.documents) <= self.position_in_doc:
            to_return = self.documents[self.position_in_doc]
            self.position_in_doc += 1
        else:
            to_return = None
        return to_return,self.position_in_doc


    def getAllDocuments(self):
        return []