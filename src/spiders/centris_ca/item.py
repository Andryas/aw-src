# -*- coding: utf-8 -*-
import scrapy

from itemloaders.processors import TakeFirst, MapCompose

class Items(scrapy.Item):
    id=scrapy.Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    url=scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
    title=scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
    price=scrapy.Field(input_processor=MapCompose(float), output_processor=TakeFirst())
    room=scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
    bedroom=scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
    bathroom=scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
    description=scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
    features=scrapy.Field(output_processor=TakeFirst())
    agent=scrapy.Field()
    location=scrapy.Field(output_processor=TakeFirst())
    attributes=scrapy.Field(output_processor=TakeFirst())
