# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import redis
import json
import re


class HydraulicGoodAction(scrapy.Spider):
    name = 'HydraulicGoodAction'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.url = 'http://xypt.mwr.gov.cn/UnitCreInfo/listCydwPage.do?'
        pool = redis.ConnectionPool(
            host='106.12.112.205', password='tongna888')
        self.r = redis.Redis(connection_pool=pool)
        self.token = 'LnHRF8R1jmqOLFnnK048DcokeilQRDS2'
        self.index = 1
        self.flag = True

    def start_requests(self):
        yield scrapy.Request(url=self.url + 'currentPage=1&showCount=20',
                             callback=self.parse,
                             )

    def parse(self, response):
        # print(response.text)
        if self.flag:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[6].xpath('./a/@onclick') \
                .extract_first()
            self.flag = False
        else:
            page = Selector(response=response).xpath('//li[@style="cursor:pointer;"]')[8].xpath('./a/@onclick') \
                .extract_first()
        page = re.findall('nextPage\((\d+)\)', page)[0]
        page = int(page) + 1
        print(page, 'page')
        person_url = Selector(response=response).xpath('//table[@id="example-advanced"]/tbody/tr')
        for p in person_url:
            zz = p.xpath('./td[2]/a/@href').extract_first()
            unit_type = p.xpath('./td[3]/text()').extract_first()
            if unit_type is None:
                unit_type = ''
            a = re.findall('javascript:toChangeTop\(\'(.*)\'\);toDetail\(\'(.*)\'\)', zz)
            yield scrapy.Request(url='http://xypt.mwr.gov.cn/UnitCreInfo/frontunitInfoList.do?ID=%s&menu=%s'
                                     % (a[0][1], a[0][0]),
                                 callback=self.company_info,
                                 meta={'unit_type': unit_type}
                                 )
        self.index += 1
        if page != self.index:
            yield scrapy.Request(url=self.url + 'currentPage=%s&showCount=20' % self.index,
                                 callback=self.parse,
                                 )

    def company_zz(self, response):
        print(response.text)

    def company_info(self, response):
        company_name = Selector(response=response).xpath('//td[@colspan="3"]')[0].xpath('./a/@title').extract_first()
        number = Selector(response=response).xpath('//td[@colspan="3"]')[3].xpath(
            'text()').extract_first()
        if number.split():
            number = number.split()[0]
            if len(number) == 18:
                number = number
        else:
            number = ''

        tr = Selector(response=response).xpath('//table[@id="table_good"]/tbody/tr')
        if tr:
            for t in tr:
                good_action = {'project_name': '', 'good_grade': '',
                               'have_date': '', 'send_department': '',
                               'have_number': '', 'company_name': company_name,
                               'number': number
                               }
                # 项目名称
                if len(t.xpath('./td/text()')) >= 2:
                    try:
                        project_name = t.xpath('./td/text()')[0].extract().split()[0]
                        good_action['project_name'] = project_name
                    except IndexError:
                        continue

                    # 奖项级别
                    good_grade = t.xpath('./td/text()')[1].extract()
                    if good_grade is not None:
                        if good_grade.split():
                            good_action['good_grade'] = good_grade.split()[0]

                    # 颁发单位
                    send_department = t.xpath('./td/text()')[2].extract()
                    if send_department is not None:
                        send_department = send_department.split()[0]
                        good_action['send_department'] = send_department

                    # 颁奖文号
                    have_number = t.xpath('./td/text()')[3].extract()
                    if have_number is not None or have_number != '/':
                        good_action['have_number'] = have_number

                    # 颁奖时间
                    try:
                        have_date = t.xpath('./td/text()')[4].extract()
                        if have_date is not None:
                            good_action['have_date'] = have_date
                    except IndexError:
                        continue
                    print(good_action)

    def person_post(self, response):
        print(response)

    def ability_zz(self, response):
        print(response)
