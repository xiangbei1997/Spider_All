# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy import Selector
import time
import json
import re

class ShanxiJianzhuImformationSpider(scrapy.Spider):
    name = 'shandong'

    def start_requests(self):
        pool = redis.ConnectionPool(host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        now_time = time.time() * 1000
        now_time = int(now_time)
        reduce_time = now_time - 964344
        self.url = 'http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback=jQuery17109359142758390728_%s&methodname=GetCorpInfo&CorpName=&CorpCode=&CertType=&LegalMan=&CurrPageIndex=%s&PageSize=%s&' % (reduce_time, 1, 12)
        self.province_flag = True
        self.index = 1
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.data = {}
        self.data['licenseNum'] = ''
        self.data['contactMan'] = ''
        self.data['area'] = ''
        self.data['companyArea'] = '山东省'
        self.data['contactAddress'] = ''
        self.data['contactPhone'] = ''
        self.data['token'] = self.token
        self.flag = True
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        data_line = response.text
        data_dict = re.split('jQuery\d+_\d+\(', data_line)[1]
        data_dict = data_dict.replace(')', '')
        json_data = json.loads(data_dict)
        for i in json_data['data']['CorpInfoList']:
            company_name = i['CorpName']
            number = i['CorpCode']
            if number != None:
                if len(number) != 18:
                    self.data['licenseNum'] = ''
                else:
                    self.data['licenseNum'] = number
            else:
                self.data['licenseNum'] = ''
            self.data['companyName'] = company_name
            yield scrapy.Request(
                url='https://api.maotouin.com/rest/companyInfo/addCompanyRecord.htm',
                # url='http://192.168.199.188:8080/web/rest/companyInfo/addCompanyRecord.htm',
                method="POST",
                headers={'Content-Type': 'application/json'},
                body=json.dumps(self.data),
                callback=self.zz,
                meta={'company_name': company_name, 'data': self.data}
            )
        self.index = self.index + 1
        if not self.index == 1686:
            now_time = time.time() * 1000
            now_time = int(now_time)
            time.sleep(0.5)
            reduce_time = now_time - 964344
            yield scrapy.Request(url='http://221.214.94.41:81/InformationReleasing/Ashx/InformationReleasing.ashx?callback='
                                     'jQuery17109359142758390728_%s&methodname=GetCorpInfo&CorpName=&CorpCode=&CertType=&LegalMan=&CurrPageIndex=%s&PageSize=%s&' % (reduce_time, self.index, 12), callback=self.parse)

    def zz(self, response):
        not_company_code = json.loads(response.text)['code']
        not_search_company_name = response.meta['company_name']
        zz_data = response.meta['data']
        self.r.sadd('all_company_name', not_search_company_name)
        print(response.text)
        data = json.dumps(zz_data, ensure_ascii=False)
        print(response.meta['data'], 'aaaaaaaaaaaaaaaaaa')
        if not_company_code == -102:
            self.r.sadd('title_name1', not_search_company_name)
            self.r.sadd('title_102', data)
            self.r.sadd('title_name3', not_search_company_name)
            print(not_search_company_name, '没找到的企业')
        else:
            print(not_search_company_name, '找到的企业')