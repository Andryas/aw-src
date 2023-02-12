# -*- coding: utf-8 -*-
import scrapy

from itemloaders.processors import TakeFirst

class Items(scrapy.Item):
    results_search_term=scrapy.Field(output_processor=TakeFirst())
    results_scraping_date=scrapy.Field(output_processor=TakeFirst())