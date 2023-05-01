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
import json

class TimeProcessor(BaseProcessor):

    QUERY_FILE = "data/time/time.qque"
    DOC_FILE = "data/time/time.all"
    lines_regexp = {}

    def __init__(self):
        super().__init__(self.QUERY_FILE,self.DOC_FILE)
        return

    def parse_one_line(self, line):

        return None, None


    def getAllDocuments(self):
        #Stream the document:
        all_documents = []
        thefile = self.getDocumentsFile()
        if not exists(thefile):
            print ("ERROR: file '{}' does not exists.".format(thefile))
            return 
        with open(thefile, 'r') as f:
            lines = f.readlines()

        entries = {}
        current_id = None
        current_date = None
        current_page = None
        current_content = ""

        for i,line in enumerate(lines):
            if line.startswith("*TEXT"):
                if current_id is not None:
                    entry = {'id': current_id, 'date': current_date, 'page': current_page, 'content': current_content}
                    all_documents.append(entry)
                current_id = line.split()[1]
                current_date = line.split()[2]
                current_page = line.split()[4]
                current_content = ""
            else:
                current_content += " "+line.strip()

        # Add the last entry
        if current_id is not None:
            entry = {'id': current_id, 'date': current_date, 'page': current_page, 'content': current_content}
            print("ENTRY: "+json.dumps(entry))
            all_documents.append(entry)


        return all_documents

def main():
    time = TimeProcessor()
    t_docs = time.getAllDocuments()
    print(t_docs)
    print(len(t_docs))

if __name__ == "__main__":
    main()
    