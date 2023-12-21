from src.settings import *

class PipelineDefault:
    # def __init__(self):
    #     pass

    # def open_spider(self, spider):
    #     pass

    # def close_spider(self, spider):
    #     pass

    def process_item(self, item, spider):
        return item