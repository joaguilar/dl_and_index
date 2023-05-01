import time
from indexers.baseindexer import BaseIndexer

class TimeIndexer(BaseIndexer):

    NAME = "time"
    INDEX_TEMPLATE = "index_profiles/time_template.json"
    SERVER="localhost"
    PORT = 9200
    HTTPS = True
    INDEX_NAME = "time-<TS>"
    DOCUMENT_TEMPLATE = "index_profiles/time_doc.json"
    TEMPLATE_NAME = "time_template"

    def __init__(self):
        i_name= self.INDEX_NAME.replace("<TS>",str(time.time()))
        super().__init__(self.NAME,self.SERVER,self.PORT,self.HTTPS,i_name,self.DOCUMENT_TEMPLATE, self.TEMPLATE_NAME, self.INDEX_TEMPLATE)

        return

    