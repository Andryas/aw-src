# -*- coding: utf-8 -*-
import json
import requests
import copy
import scrapy
import rabbitpy

from scrapy.loader import ItemLoader
from src.spiders.centris_ca.item import Items


from re import findall
from lxml import etree
from urllib.parse import unquote

from datetime import datetime

from src.utils.stringpy import str_replace
from src.utils.random_agent import random_agent
from src.utils.lubridate import now
from src.settings import *

class CentrisCaSpider(scrapy.Spider):
    name = 'centris_ca'

    headers = {
        "origin": "www.centris.ca",
        "user-agent": random_agent()
    }

    custom_settings = {
        'ITEM_PIPELINES': {
            'src.spiders.centris_ca.pipeline.Pipeline': 300
        }
    }

    def __init__(self, date = str(now()), mode = "generator"):
        self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        self.mode=mode

        # guarantees that the queue will exist
        self.connection = rabbitpy.Connection(RABBITMQ_URL)
        self.connection = self.connection.channel()

        self.queue = rabbitpy.Queue(self.connection, 'spider_{0}'.format(self.name))
        self.queue.durable = True
        self.queue.declare()

    def start_requests(self):
        url_get = "https://www.centris.ca/en/properties~for-{}?view=Thumbnail"
        url_post = "https://www.centris.ca/Property/GetInscriptions?"

        if self.mode=="generator":
            self.total_count = 0

            for type in ["rent", "sale"]:
                req = requests.get(url_get.format(type), headers=self.headers)
                self.headers["referer"] = url_get.format(type)
                self.headers["accept-language"]="en-US,en;q=0.9"

                start_position=0
                response = requests.post(url_post, headers=self.headers, cookies=req.cookies, json={'startPosition': start_position})
                data = json.loads(response.text)
                total_count = data['d']['Result']['count']
                self.total_count = self.total_count + total_count

                links = self.get_links(data['d']['Result']['html'])
                for link in links:
                    message = rabbitpy.Message(self.connection, json.dumps(str_replace(link, "/fr/", "/en/")))
                    message.publish('', 'spider_{0}'.format(self.name))
         
                j = 0
                while True:
                    response = requests.post(url_post, headers=self.headers, json={'startPosition': start_position}, cookies=req.cookies)
                    if j == 5:
                        break
                    elif response.status_code != 200:
                        req = requests.get(url_get.format(type), headers=self.headers)
                        j=+1
                    else:
                        if start_position >= total_count:
                            break
                        else:
                            start_position = start_position + 20 
                            j=0
                            data = json.loads(response.text)
                            links = self.get_links(data['d']['Result']['html'])
                            for link in links:
                                message = rabbitpy.Message(self.connection, json.dumps(str_replace(link, "/fr/", "/en/")))
                                message.publish('', 'spider_{0}'.format(self.name))
                            print(start_position)
            self.total_queue = len(self.queue)

        elif self.mode=="receiver":
            self.total_collect = 0
            with rabbitpy.Connection(RABBITMQ_URL) as conn:
                with conn.channel() as channel:
                    queue = rabbitpy.Queue(channel, "spider_" + self.name)
                    queue.durable = True
                    while len(queue) > 0:
                        message = queue.get()
                        data=message.body.decode()
                        url=json.loads(data)
                        yield scrapy.Request(
                            url=url, 
                            callback=self.parse_detail, 
                            headers=self.headers
                        )
                        message.ack()
            
    def parse_detail(self, response):
        loader = ItemLoader(Items(), response=response)

        loader.add_value("id", findall("(?<=/)[0-9]+(?=\\?)", unquote(response.url))[0])
        loader.add_value("url", unquote(response.url))
        loader.add_value("title", response.xpath("//span[@data-id='PageTitle']/text()").extract_first())
        loader.add_value("price", response.xpath("//div[@itemprop='offers']/meta[@itemprop='price']/@content").extract_first())
        loader.add_value("room", response.xpath("//div[@class='col-lg-12 description']//div[@class='row teaser']/div[@class='col-lg-3 col-sm-6 piece']/text()").extract_first())
        loader.add_value("bedroom", response.xpath("//div[@class='col-lg-12 description']//div[@class='row teaser']/div[@class='col-lg-3 col-sm-6 cac']/text()").extract_first())
        loader.add_value("bathroom", response.xpath("//div[@class='col-lg-12 description']//div[@class='row teaser']/div[@class='col-lg-3 col-sm-6 sdb']/text()").extract_first())
        loader.add_value("description", response.xpath("//div[@itemprop='description']/text()").extract_first())

        features_names = response.xpath("//div[@class='col-lg-12 description']//div[@class='col-lg-3 col-sm-6 carac-container']/div[@class='carac-title']/text()").extract()
        features_values = response.xpath("//div[@class='col-lg-12 description']//div[@class='col-lg-3 col-sm-6 carac-container']/div[@class='carac-value']/span/text()").extract()
        features = dict(zip(features_names, features_values))
        features['Walkscore'] = response.xpath("//div[@class='col-lg-12 description']//div[@class='walkscore']//span//text()").extract_first()
        loader.add_value("features", features)

        agents_url = response.xpath("//div[@class='property-summary-item__brokers-content']/div[@class='position-relative']/a/@href").extract()
        agents_name = response.xpath("//div[@class='property-summary-item__brokers-content']/div[@class='position-relative']//h1[@itemprop='name']/text()").extract()
        agents_job = response.xpath("//div[@class='property-summary-item__brokers-content']/div[@class='position-relative']//div[@itemprop='jobTitle']/text()").extract()
        agent = []
        for e in range(0, len(agents_job)):
            agent.append({
                'url': agents_url[e],
                'agents_name': agents_name[e],
                'agents_job': agents_job[e]
            })
        loader.add_value("agent", agent)

        address = response.xpath("//h2[@itemprop='address']/text()").extract_first()
        latitude = response.xpath("//div[@itemprop='geo']/meta[@itemprop='latitude']/@content").extract_first()
        longitude = response.xpath("//div[@itemprop='geo']/meta[@itemprop='longitude']/@content").extract_first()
        location = {
            'address': address,
            'geocode': {
                'lat': latitude,
                'lng': longitude
            }
        }
        loader.add_value("location", location)

        scripts = response.xpath("//script/text()").extract()
        scripts = [e for e in scripts if 'sdk/' in e]
        scripts = scripts[0]
        token = findall("(?<=sdk/\\?token=).+(?=';)", scripts)[0]

        url_scores = "https://api.locallogic.co/v1/scores?token={token}&lat={lat}&lng={lng}&locale=en&radius=1000&fields=value%2Ctext%2Ccategory"
        url_scores = url_scores.format(lat = latitude, lng = longitude, token = token)
        req = requests.get(url_scores, headers={'origin': "https://www.centris.ca", 'referer': "https://www.centris.ca/"})
        data = json.loads(req.text)
        if data['data']['attributes']:
            attributes = data["data"]["attributes"]
            attributes["url"] = url_scores
        else:
            attributes = {
                "url": url_scores
            }
        loader.add_value("attributes", attributes)
        
        self.total_collect = self.total_collect + 1
        yield loader.load_item()

    def get_links(self, dResultHtml):
        html = copy.deepcopy(dResultHtml)
        html = str(dResultHtml)
        html = html.replace('\n','').replace('\r','')
        html = etree.HTML(html)
        links = html.xpath("//a[@class='a-more-detail']/@href")
        links = ["https://www.centris.ca" + link for link in links]
        return(links)
