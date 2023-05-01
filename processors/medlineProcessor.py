# Sample document:
# .I 1
# .W
# correlation between maternal and fetal plasma levels of glucose and free
# fatty acids .                                                           
#   correlation coefficients have been determined between the levels of   
# glucose and ffa in maternal and fetal plasma collected at delivery .    
# significant correlations were obtained between the maternal and fetal   
# glucose levels and the maternal and fetal ffa levels . from the size of 
# the correlation coefficients and the slopes of regression lines it      
# appears that the fetal plasma glucose level at delivery is very strongly
# dependent upon the maternal level whereas the fetal ffa level at        
# delivery is only slightly dependent upon the maternal level .  

from processors.baseProcessor import BaseProcessor
import re
from os.path import exists

class MedlineProcessor(BaseProcessor):

    QUERY_FILE = "data/medline/med.qry"
    DOC_FILE = "data/medline/med.all"
    lines_regexp = {}

    def __init__(self):
        super().__init__(self.QUERY_FILE,self.DOC_FILE)

        #Regular expressions to detect the fields:
        self.lines_regexp = {
            'doc_id': re.compile(r'\.I (?P<id>[0-9]+).*\n'),
            'title': re.compile(r'\.T.*\n'),
            'author': re.compile(r'\.A.*\n'),
            'biblio': re.compile(r'\.B.*\n'),
            'text': re.compile(r'\.W.*\n'),
        }

        return

    def parse_one_line(self, line):
        for key, pattern in self.lines_regexp.items():
            found = pattern.search(line)
            if found:
                break
        if found:
            return key, found
        return None, None


    def getAllDocuments(self):
        #Stream the document:
        all_documents = []
        doc = {}
        is_title = False
        is_author = False
        is_biblio = False
        is_text = False
        title = ""
        biblio = ""
        author = ""
        text = ""
        doc_num = 0
        thefile = self.getDocumentsFile()
        if not exists(thefile):
            print ("ERROR: file '{}' does not exists.".format(thefile))
            return 
        with open(thefile,'r') as document_reader:
            for line in document_reader.readlines():
                # print("Processing line '{}'".format(line))
                key,data = self.parse_one_line(line)

                if key == None: #No regex matched, we are parsing one of the fields...
                    if is_title:
                        title += line.replace('\n',' ')
                    elif is_author:
                        author += line.replace('\n',' ')
                    elif is_biblio:
                        biblio += line.replace('\n',' ')
                    elif is_text:
                        text += line.replace('\n',' ')
                    continue
                else: # We got a match, let's reset the statuses
                    if is_title:
                        doc['title'] = title
                    elif is_author:
                        doc['author'] = author
                    elif is_biblio:
                        doc['bibliography'] = biblio
                    elif is_text:
                        doc['content'] = text
                    is_title = False
                    is_author = False
                    is_biblio = False
                    is_text = False
                    title = ""
                    biblio = ""
                    author = ""
                    text = ""                    

                if key == 'doc_id':
                    doc_id = data.group('id')
                    #starting a new document:
                    if doc == {}:
                        doc['id']=doc_id
                    else: # There was a document already, we save it to the array first
                        all_documents.append(doc.copy())
                        # print("Processed document: {}, # {}.".format(doc,doc_num))
                        print("Processed document: {}.".format(doc_num))
                        doc_num += 1
                        doc = {}
                        doc['id']=doc_id
                    continue

                if key == 'title':
                    #Title is in the next line:
                    is_title = True
                    continue

                if key == 'author':
                    is_author = True
                    continue

                if key == 'biblio':
                    is_biblio = True
                    continue

                if key == 'text':
                    is_text = True
                    continue

        return all_documents

def main():
    med = MedlineProcessor()
    print(med.getAllDocuments())

if __name__ == "__main__":
    main()
    