# import pymongo
# from src.utils.lubridate import now

# class Pipeline:

#     def __init__(self, MONGO_URI, MONGO_DB):
#         self.MONGO_URI=MONGO_URI
#         self.MONGO_DB=MONGO_DB
    
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#             MONGO_URI=crawler.settings.get('MONGO_URI'),
#             MONGO_DB=crawler.settings.get('MONGO_DATABASE')
#         )
#     def open_spider(self, spider):
#         self.client = pymongo.MongoClient(self.MONGO_URI)
#         self.db = self.client[self.MONGO_DB]

#     def close_spider(self, spider):
#         # stats={}
#         # stats["created_at"]=spider.date
#         # stats["spider"]=spider.name
#         # stats["mode"]=spider.mode
#         # if spider.mode == "generator":
#         #     stats["total_count"]=spider.total_count
#         #     stats["total_queue"]=spider.total_queue
#         # elif spider.mode == "receiver": 
#         #     stats["total_collect"]=spider.total_collect
#         # self.db["stats"].insert(stats)
#         self.client.close()

#     def process_item(self, item, spider):
#         item = dict(item)
#         self.db[spider.name].update(
#             {
#                 "id": item["id"]
#             }, 
#             {
#                 "$setOnInsert": {
#                     'created_at': now(),
#                 },
#                 "$set": item,
#                 "$push": {"crawled_at": spider.date}
#             }, 
#             upsert=True
#         )

#         return item