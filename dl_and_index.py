from processors.cranProcessor import CranProcessor
from indexers.cranIndexer import CranIndexer
from processors.medlineProcessor import MedlineProcessor
from indexers.medlineIndexer import MedlineIndexer
from processors.timeProcessor import TimeProcessor
from indexers.timeIndexer import TimeIndexer

def main():
    #Index cran dataset for now

    processor = CranProcessor()
    indexer = CranIndexer()
    

    documents = processor.getAllDocuments()
    print ("Loaded {} documents from the Cran collection.".format(len(documents)))

    indexer.createIndexTemplate()
    indexer.indexAllDocuments(documents)

    #Index medline:
    medprocessor = MedlineProcessor()
    medindexer = MedlineIndexer()
    meddocuments = medprocessor.getAllDocuments()
    print ("Loaded {} documents from the Medline collection.".format(len(meddocuments)))

    medindexer.createIndexTemplate()
    medindexer.indexAllDocuments(meddocuments)

    #Index Time:
    timeprocessor = TimeProcessor()
    timeindexer = TimeIndexer()
    timedocuments = timeprocessor.getAllDocuments()
    print ("Loaded {} documents from the Time collection.".format(len(timedocuments)))

    timeindexer.createIndexTemplate()
    timeindexer.indexAllDocuments(timedocuments)

if __name__ == "__main__":
    main()
    