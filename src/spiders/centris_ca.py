import json
import requests
import copy
import scrapy
import math

from scrapy.loader import ItemLoader
from src.items.RealEstate import RealEstate

from re import findall
from urllib.parse import unquote
from lxml import etree

from src.utils.stringpy import str_strip_white_space, str_replace
from src.utils.lubridate import now
from src.utils.log_error import log_error
from src.settings import *

class CentrisCaSpider(scrapy.Spider):
    name = 'centris_ca'
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'src.pipelines.JsonWriterGCP.JsonWriterGCP': 200
        },
        'DOWNLOADER_MIDDLEWARES': {
            "src.middlewares.DeltaFetchGCP.DeltaFetchGCP": 450
        }
    }

    base_url = "https://www.centris.ca"

    update_query_sale = {
        "query": {
            "UseGeographyShapes": 0,
            "Filters": [],
            "FieldsValues": [
            {
                "fieldId": "Category",
                "value": "Residential",
                "fieldConditionId": "",
                "valueConditionId": ""
            },
            {
                "fieldId": "SellingType",
                "value": "Sale",
                "fieldConditionId": "",
                "valueConditionId": ""
            },
            {
                "fieldId": "LandArea",
                "value": "SquareFeet",
                "fieldConditionId": "IsLandArea",
                "valueConditionId": ""
            },
            {
                "fieldId": "SalePrice",
                "value": 20000,
                "fieldConditionId": "ForSale",
                "valueConditionId": ""
            },
            {
                "fieldId": "SalePrice",
                "value": 50000,
                "fieldConditionId": "ForSale",
                "valueConditionId": ""
            }
            ]
        },
       "isHomePage": "false"
    }

    update_query_rent = {
        "query": {
            "UseGeographyShapes": 0,
            "Filters": [],
            "FieldsValues": [
                {
                    "fieldId": "Category",
                    "value": "Residential",
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "SellingType",
                    "value": "Rent",
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "LandArea",
                    "value": "SquareFeet",
                    "fieldConditionId": "IsLandArea",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "RentPrice",
                    "value": 850,
                    "fieldConditionId": "ForRent",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "RentPrice",
                    "value": 999999999999,
                    "fieldConditionId": "ForRent",
                    "valueConditionId": ""
                }
            ]
        },
        "isHomePage": "false"
    }

    headers = {
        "Content-Type": "application/json;charset=UTF-8", 
        "Accept":"application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
    }
    
    created_at = now(False)

    def start_requests(self):
        yield scrapy.Request(
            url= self.base_url + "/en/properties~for-rent?view=Thumbnail", 
            headers=self.headers,
            callback=self.pagination_price_range
        )
        
    def pagination_price_range(self, response):
        # NOTE the way this crawler was structured is because to progress in the
        # pagination effectively it is necessary to keep the SAME SESSION,
        # otherwise the UpdateQuery/ wont work.

        all_items_urls = []

        rentRange = response.xpath("//price[@data-field-id='RentPrice']/@data-field-value-id").getall()
        rentRange = [int(item) for item in rentRange]
        rentRange = sorted(set(list(rentRange)))
        # rentRange = [0, 2000] # for test purpose only

        for i in range(0, len(rentRange)-1):
            body = copy.deepcopy(self.update_query_rent)
            body["query"]["FieldsValues"][3]["value"]=rentRange[i]
            body["query"]["FieldsValues"][4]["value"]=rentRange[i+1]

            req = requests.post(
                url = "https://www.centris.ca/property/UpdateQuery",
                headers=self.headers,
                json=body
            )

            body = copy.deepcopy(self.update_query_rent)
            body=body["query"]
            body["FieldsValues"][3]["value"]=rentRange[i]
            body["FieldsValues"][4]["value"]=rentRange[i+1]
            
            req2 = requests.post(
                "https://www.centris.ca/property/GetPropertyCount",
                headers = self.headers,
                json=body
            )
            data = req2.json()
            n = data["d"]["Result"]["listingCount"]
            n = math.ceil(n/20)

            for j in range(0, n):
                req3 = requests.post(
                    "https://www.centris.ca/Property/GetInscriptions?",
                    headers={
                        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
                    },
                    json={"startPosition": j * 20},
                    cookies=req.cookies
                )
                try:
                    data = req3.json()
                    links = self.get_links(data['d']['Result']['html'])
                    for link in links:
                        all_items_urls.append(link)
                except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                        log_error(e, self.name)
                    

        salesRange = response.xpath("//price[@data-field-id='SalePrice']/@data-field-value-id").getall()
        salesRange = [int(item) for item in salesRange]
        salesRange = sorted(set(list(salesRange)))

        for i in range(0, len(salesRange)-1):
            body = copy.deepcopy(self.update_query_sale)
            body["query"]["FieldsValues"][3]["value"]=salesRange[i]
            body["query"]["FieldsValues"][4]["value"]=salesRange[i+1]
            
            req = requests.post(
                url = "https://www.centris.ca/property/UpdateQuery",
                headers=self.headers,
                json=body
            )

            body = copy.deepcopy(self.update_query_sale)
            body=body["query"]
            body["FieldsValues"][3]["value"]=salesRange[i]
            body["FieldsValues"][4]["value"]=salesRange[i+1]
            
            req2 = requests.post(
                "https://www.centris.ca/property/GetPropertyCount",
                headers = self.headers,
                json=body
            )
            data = req2.json()
            n = data["d"]["Result"]["listingCount"]
            n = math.ceil(n/20)

            for j in range(0, n+1):
                req3 = requests.post(
                    "https://www.centris.ca/Property/GetInscriptions?",
                    headers={
                        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
                    },
                    json={"startPosition": j * 20},
                    cookies=req.cookies
                )
                try:
                    data = req3.json()
                    links = self.get_links(data['d']['Result']['html'])
                    for link in links:
                        all_items_urls.append(link)
                except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                        log_error(e, self.name)

        all_items_urls = list(set(all_items_urls))

        for link in all_items_urls:
            yield scrapy.Request(
                url = str_replace(link, "/fr/", "/en/"), 
                callback=self.parse_detail,
                meta={"id": int(findall("(?<=/)[0-9]+(?=\\?)", unquote(link))[0])}
            )

    def parse_detail(self, response):
        if b"Fake" in response.body:
            yield {
                "id": response.meta["id"], 
                "url": response.url
            }
        else:
            loader = ItemLoader(RealEstate(), response=response)

            loader.add_value("created_at", self.created_at)
            loader.add_value("id", findall("(?<=/)[0-9]+(?=\\?)", unquote(response.url))[0])
            loader.add_value("url", unquote(response.url))
            loader.add_value("title", response.xpath("//span[@data-id='PageTitle']/text()").extract_first())
            loader.add_value("price", response.xpath("//div[@itemprop='offers']/meta[@itemprop='price']/@content").extract_first())
            loader.add_value("description", response.xpath("//div[@itemprop='description']/text()").extract_first())
            
            loader.add_value("room", response.xpath("//div[@class='col-lg-12 description']//div[@class='row teaser']/div[@class='col-lg-3 col-sm-6 piece']/text()").extract_first())
            loader.add_value("bedroom", response.xpath("//div[@class='col-lg-12 description']//div[@class='row teaser']/div[@class='col-lg-3 col-sm-6 cac']/text()").extract_first())
            loader.add_value("bathroom", response.xpath("//div[@class='col-lg-12 description']//div[@class='row teaser']/div[@class='col-lg-3 col-sm-6 sdb']/text()").extract_first())

            feature_names = response.xpath("//div[@class='col-lg-12 description']//div[@class='col-lg-3 col-sm-6 carac-container']/div[@class='carac-title']/text()").extract()
            feature_names = [str_strip_white_space(str(x)) for x in feature_names]
            feature_values = response.xpath("//div[@class='col-lg-12 description']//div[@class='col-lg-3 col-sm-6 carac-container']/div[@class='carac-value']/span/text()").extract()
            feature_values = [str_strip_white_space(str(x)) for x in feature_values]
            feature = dict(zip(feature_names, feature_values))
            feature['walkscore'] = response.xpath("//div[@class='col-lg-12 description']//div[@class='walkscore']//span//text()").extract_first()
            loader.add_value("feature", feature)

            agent_url = response.xpath("//div[@class='property-summary-item__brokers-content']/div[@class='position-relative']/a/@href").extract()
            agent_name = response.xpath("//div[@class='property-summary-item__brokers-content']/div[@class='position-relative']//h1[@itemprop='name']/text()").extract()
            agent_job = response.xpath("//div[@class='property-summary-item__brokers-content']/div[@class='position-relative']//div[@itemprop='jobTitle']/text()").extract()
            agent = []
            for e in range(0, len(agent_job)):
                agent.append({
                    'url': agent_url[e],
                    'agent_name': agent_name[e],
                    'agent_job': agent_job[e]
                })
            loader.add_value("agent", agent)

            address = response.xpath("//h2[@itemprop='address']/text()").extract_first()
            latitude = response.xpath("//div[@itemprop='geo']/meta[@itemprop='latitude']/@content").extract_first()
            longitude = response.xpath("//div[@itemprop='geo']/meta[@itemprop='longitude']/@content").extract_first()
            location = {
                'address': address,
                'geocode': {
                    'lat': float(latitude),
                    'lng': float(longitude)
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
                attribute = data["data"]["attributes"]
                attribute["url"] = url_scores
            else:
                attribute = {
                    "url": url_scores
                }
            loader.add_value("attribute", attribute)
            
            yield loader.load_item()

    def get_links(self, dResultHtml):
        html = copy.deepcopy(dResultHtml)
        html = str(dResultHtml)
        html = html.replace('\n','').replace('\r','')
        html = etree.HTML(html)
        if html is None:
            return([])
        else:
            links = html.xpath("//a[@class='a-more-detail']/@href")
            links = ["https://www.centris.ca" + link for link in links]
            return(links)
