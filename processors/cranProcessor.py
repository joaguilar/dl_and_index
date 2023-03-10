# Sample document:
# .I 1
# .T
# experimental investigation of the aerodynamics of a
# wing in a slipstream .
# .A
# brenckman,m.
# .B
# j. ae. scs. 25, 1958, 324.
# .W
# experimental investigation of the aerodynamics of a
# wing in a slipstream .
#   an experimental study of a wing in a propeller slipstream was
# made in order to determine the spanwise distribution of the lift
# increase due to slipstream at different angles of attack of the wing
# and at different free stream to slipstream velocity ratios .  the
# results were intended in part as an evaluation basis for different
# theoretical treatments of this problem .
#   the comparative span loading curves, together with
# supporting evidence, showed that a substantial part of the lift increment
# produced by the slipstream was due to a /destalling/ or
# boundary-layer-control effect .  the integrated remaining lift
# increment, after subtracting this destalling lift, was found to agree
# well with a potential flow theory .
#   an empirical evaluation of the destalling effects was made for
# the specific configuration of the experiment .

from processors.baseProcessor import BaseProcessor
import re
from os.path import exists

class CranProcessor(BaseProcessor):

    QUERY_FILE = "data/cran/cran.qry"
    DOC_FILE = "data/cran/cran.all.1400"
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
    cran = CranProcessor()
    print(cran.getAllDocuments())

if __name__ == "__main__":
    main()
    