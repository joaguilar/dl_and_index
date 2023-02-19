from processors.cranQueryProcessor import CranQueryProcessor


def main():
    #Index cran dataset for now

    processor = CranQueryProcessor()

    documents = processor.getAllDocuments()
    print ("Loaded {} documents from the Cran collection.".format(len(documents)))
    print(documents[0])
    print(documents[1])


if __name__ == "__main__":
    main()
    