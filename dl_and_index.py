from processors.cranProcessor import CranProcessor
from indexers.cranIndexer import CranIndexer


def main():
    #Index cran dataset for now

    processor = CranProcessor()
    indexer = CranIndexer()

    documents = processor.getAllDocuments()
    print ("Loaded {} documents from the Cran collection.".format(len(documents)))

    indexer.createIndexTemplate()
    indexer.indexAllDocuments(documents)

if __name__ == "__main__":
    main()
    