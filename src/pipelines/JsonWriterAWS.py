import os
import json
from itemadapter import ItemAdapter
from src.utils.aws import *
from src.utils.destymd import destymd
from src.settings import *
from scrapy import signals

class JsonWriterAWS:
    def __init__(self):
        pass

    def open_spider(self, spider):
        hd = os.path.expanduser("~") + "/data"
        if not os.path.exists(hd):
            os.makedirs(hd)
        self.datapath=hd + "/" + spider.name + ".jsonl"
        self.file=open(self.datapath, "w")

    def close_spider(self, spider):
        self.file.close()
        upload_blob(
            BUCKET, 
            self.datapath,
            destymd(spider.name, "jsonl")
        )

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item