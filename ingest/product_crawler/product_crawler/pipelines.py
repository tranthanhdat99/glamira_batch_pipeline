import csv
import os
import yaml
from itemadapter import ItemAdapter

class CSVPipeline:
    def __init__(self):
        cfg = yaml.safe_load(open('config/ingest.yaml'))['ingest']
        self.output_csv = cfg['output_csv']
        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)

    def open_spider(self, spider):
        self.file = open(self.output_csv, 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(
            self.file,
            fieldnames=['product_id', 'product_name']
        )
        self.writer.writeheader()

    def process_item(self, item, spider):
        data = ItemAdapter(item).asdict()
        self.writer.writerow({
            'product_id':   data.get('product_id'),
            'product_name': data.get('product_name')
        })
        return item
    
    def close_spider(self, spider):
        self.file.close()