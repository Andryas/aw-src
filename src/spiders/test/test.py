# -*- coding: utf-8 -*-
import json
import scrapy

from src.settings import *
from src.utils.lubridate import now

class TestSpider(scrapy.Spider):
    name = 'test'

    headers = {
        "x-domain": "www.centris.ca",
    }

    custom_settings = {
        'ITEM_PIPELINES': {
            'src.spiders.test.pipelines.MongoPipeline': 300
        }
    }

    def __init__(self, date=now()):
        self.date=date

    def start_requests(self):
        urls = [
            'https://quotes.toscrape.com/page/1/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'scraping': {
                    'date_scraping': self.date
                },
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

       

       