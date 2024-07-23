from src.settings import *
from scrapy import signals
from scrapy.signalmanager import dispatcher
from src.utils.aws import upload_blob, download_blob, check_file_exists
from datetime import datetime

import os
import sqlite3
from scrapy.http import Response
from src.utils.lubridate import now

class DeltaFetchAWS:

    def __init__(self, spider):
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed) # connect to spider_closed
        hd = os.path.expanduser("~") + "/data"
        self.datapath=hd + "/" + spider.name + ".db"
        if not os.path.exists(hd):
            os.makedirs(hd)
        if os.path.exists(self.datapath):
            os.remove(self.datapath)
        if check_file_exists(BUCKET, spider.name + "/" + spider.name + ".db"):
            download_blob(BUCKET, spider.name + "/" + spider.name + ".db", self.datapath)
        self.conn = sqlite3.connect(self.datapath)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scrapy (id INTEGER PRIMARY KEY, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, url TEXT);''')
        self.conn.commit()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(spider=crawler.spider)
    
    def spider_closed(self, spider):
        upload_blob(
            BUCKET, 
            self.datapath,
            spider.name + "/" + spider.name + ".db"
        )
        self.conn.close()
      
    def process_request(self, request, spider):
        item_id = request.meta.get('id')

        if item_id:
            result = None
            if spider.delta_days > 0:
                self.cursor.execute("SELECT * FROM scrapy WHERE id={}".format(item_id))
                result = self.cursor.fetchone()

            if result:
                delta=now(True, 0) - datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
                if delta.days > spider.delta_days:
                    print("The record is outdated. Creating a new request for it.")
                    self.cursor.execute("DELETE FROM scrapy WHERE id={}".format(item_id))
                    self.conn.commit()
                    self.cursor.execute("INSERT INTO scrapy (id, url) VALUES ({}, '{}')".format(item_id, request.url))
                    self.conn.commit()
                else:
                    spider.logger.info(f"ID {item_id} exists in database. Ignoring request.")
                    return Response(url=request.url, status=200, body=b"Fake")
            else:
                try:
                    self.cursor.execute("INSERT INTO scrapy (id, url) VALUES ({}, '{}')".format(item_id, request.url))
                    self.conn.commit()
                except sqlite3.IntegrityError:
                    print("The record does not exist in the database. Creating a new request for it.")
                

