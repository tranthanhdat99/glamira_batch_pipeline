import scrapy
import yaml
from pymongo import MongoClient
from product_crawler.items import ProductItem

class ProductSpider(scrapy.Spider):
    name = 'product_spider'

    def start_requests(self):
        ingest_cfg = yaml.safe_load(open('config/ingest.yaml'))['ingest']
        mongo_cfg = yaml.safe_load(open('config/mongo.yaml'))['mongo']
        client = MongoClient(mongo_cfg['uri'])
        summary = client[mongo_cfg['database']][mongo_cfg['collections']['summary']]

        pipeline = [
            {'$match': {'collection': {'$in': ingest_cfg['product_collections']}}},
            {'$group': {'_id': '$product_id', 'current_url': {'$first': '$current_url'}}}
        ]
        for rec in summary.aggregate(pipeline):
            pid = rec['_id']
            url = rec.get('current_url')
            if not url:
                continue
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'product_id': pid}
            )
        client.close()

    def parse(self, response):
        item = ProductItem()
        item['product_id'] = response.meta['product_id']
        title = (
            response.css('h1.product-title::text').get() or
            response.xpath('//title/text()').get()
        )
        item['product_name'] = title.strip() if title else ''
        yield item