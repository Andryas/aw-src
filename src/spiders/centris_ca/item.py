# -*- coding: utf-8 -*-
import scrapy

from itemloaders.processors import TakeFirst, MapCompose
from src.utils.stringpy import str_strip_white_space

class Items(scrapy.Item):
    id=scrapy.Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    url=scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
    title=scrapy.Field(input_processor=MapCompose(str, str_strip_white_space), output_processor=TakeFirst())
    price=scrapy.Field(input_processor=MapCompose(float), output_processor=TakeFirst())
    room=scrapy.Field(input_processor=MapCompose(str, str_strip_white_space), output_processor=TakeFirst())
    bedroom=scrapy.Field(input_processor=MapCompose(str, str_strip_white_space), output_processor=TakeFirst())
    bathroom=scrapy.Field(input_processor=MapCompose(str, str_strip_white_space), output_processor=TakeFirst())
    description=scrapy.Field(input_processor=MapCompose(str, str_strip_white_space), output_processor=TakeFirst())
    feature=scrapy.Field(output_processor=TakeFirst())
    location=scrapy.Field(output_processor=TakeFirst())
    attribute=scrapy.Field(output_processor=TakeFirst())
    agent=scrapy.Field()
