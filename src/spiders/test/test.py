# -*- coding: utf-8 -*-
import scrapy

from src.settings import *
from src.utils.lubridate import now

class TestSpider(scrapy.Spider):
    name = 'test'
    
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'src.middlewares.DeltaFetchGCP.DeltaFetchGCP': 50
        }
    }

    def start_requests(self):
        urls = [
            'https://quotes.toscrape.com/page/1/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.pagination)

    def pagination(self, response):
        for quote in response.css('div.quote'):
            yield {
                'created_at': now(False),
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall()
            }
        
        # for i in range(1,10):
            # yield scrapy.Request(url="https://quotes.toscrape.com/page/{}/".format(i), callback=self.parse)
        yield scrapy.Request(url="https://quotes.toscrape.com/page/3/", callback=self.parse, meta={"id": 3})
        yield scrapy.Request(url="https://quotes.toscrape.com/page/4/", callback=self.parse, meta={"id": 4})

    def parse(self, response):
        if b"Fake" in response.body:
            yield {
                "id": response.meta["id"], 
                "url": response.url
            }
        else:
            for quote in response.css('div.quote'):
                yield {
                    'created_at': now(False),
                    'text': quote.css('span.text::text').get(),
                    'author': quote.css('small.author::text').get(),
                    'tags': quote.css('div.tags a.tag::text').getall()
                }