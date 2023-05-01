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

# Judgement file format - we'll ignore the second column
# 1 0 13 1
# 1 0 14 1
# 1 0 15 1
# 1 0 72 1
# 1 0 79 1
# 1 0 138 1
# 1 0 142 1
# 1 0 164 1
# 1 0 165 1
# 1 0 166 1
# 1 0 167 1

from baseProcessor import BaseProcessor
import re
from os.path import exists

class TimeQueryProcessor(BaseProcessor):

    QUERY_FILE = "data/time/time.que"
    DOC_FILE = "data/time/time.all"
    lines_regexp = {}
    JUDGEMENT_FILE = "data/time/time.rel"
    judgement_file = None
    judgements = {}

    def __init__(self):
        super().__init__(self.QUERY_FILE,self.DOC_FILE)
        self.judgement_file = self.JUDGEMENT_FILE

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

        return None, None


    def getAllDocuments(self):
        #Stream the document:
        all_documents = []
        thefile = self.getQueryFile()
        if not exists(thefile):
            print ("ERROR: file '{}' does not exists.".format(thefile))
            return 
        with open(thefile, 'r') as f:
            lines = f.readlines()

        entries = {}
        current_id = None
        current_content = ""

        for i,line in enumerate(lines):
            if line.startswith("*FIND"):
                if current_id is not None:
                    entry = {'id': current_id, 'content': current_content}
                    all_documents.append(entry)
                current_id = line.split()[1]
                current_content = ""
            else:
                current_content += " "+line.strip()

        # Add the last entry
        if current_id is not None:
            entry = {'id': current_id, 'content': current_content}
            all_documents.append(entry)


        return all_documents

    def getJudgementFile(self):
        return self.judgement_file


    def readOneJudgement(self,line):
        return 0,0,0


    ###
    # Structure to return:
    # [
    #     {
    #         "query_id": {
    #             "doc_id": "rel",
    #             "doc_id": "rel",
    #             ...
    #         }
    #     }
    # ]
    ###
    def getJudgements(self):
        self.judgements = {}
        thefile = self.getJudgementFile()
        if not exists(thefile):
            print ("ERROR: file '{}' does not exists.".format(thefile))
            return 
        with open(thefile,'r') as document_reader:
            for line in document_reader.readlines():
                fields = line.strip().split()
                if len(fields) > 0:
                    key = int(fields[0])
                    values = {int(v): 4 for v in fields[1:]}
                    self.judgements[key] = values



        return self.judgements

def main():
    time = TimeQueryProcessor()
    print(time.getAllDocuments())
    j = time.getJudgements()
    print(j)
    print(len(j))

if __name__ == "__main__":
    main()
    