from processors.cranProcessor import CranProcessor
from indexers.cranIndexer import CranIndexer
from processors.medlineProcessor import MedlineProcessor
from indexers.medlineIndexer import MedlineIndexer

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


if __name__ == "__main__":
    main()
    