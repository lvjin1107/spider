# -*- coding:utf-8 -*-
import requests
from lxml import etree
import json
import re
from bs4 import BeautifulSoup


class Car(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
        self.url = 'http://www.chinacar.com.cn/jiaoche'
        self.base_url = 'http://www.chinacar.com.cn'
        self.pn = 0
        self.data = list()

    def send_request(self, url):
        '''发送请求'''
        html = requests.get(url, headers=self.headers).content
        return html

    def parse(self, html):
        '''获取到所有的车的类型'''
        html = etree.HTML(html)

        car_link_list = html.xpath('//div[@class="cars_all wrap"]/ul/li/a/@href')
        car_type_list = html.xpath('//div[@class="cars_all wrap"]/ul/li/@class')
        # print car_type_list
        for car_type, car_link in zip(car_type_list, car_link_list):
            car_link = self.base_url + car_link
            # print car_link
            # print car_type
            car_type = car_type[3:]
            # print car_type
            html = requests.get(car_link).content

            self.parse_item(html, car_type)

    def parse_item(self, html, car_type):

        '''获取到列表页的消息'''
        html_obj = etree.HTML(html)
        car_detail_list = html_obj.xpath('//div[@class="mainBox"]/div/div/div/div[@class="pic"]/a/@href')
        next_page = html_obj.xpath('//div[@class="page"]/div/div/a/text()')[-2:-1]

        while True:
            next_url = self.url + '/p_slist_0_' + car_type + '_z_0_0_0_0_0_' + str(self.pn) + '.html'
            html = requests.get(next_url, headers=self.headers).content
            self.pn += 1

            if self.pn >= next_page:
                break
            for car_detail in car_detail_list:
                car_detail = self.base_url + car_detail

                html = requests.get(car_detail).content
                self.parse_car(html)


        # print html

    def parse_car(self, html):
        '''
        详情页的数据: 获取到详情页的数据,但是详情页的参数配置,通过xpath获取不到想要获取到数据,所以通过正则取匹配出想要获取到的数据

        '''
        pattern = re.compile(r'<div.*?class="cars_ct_right">(.*?)</div>', re.S | re.I)
        html_obj = re.findall(pattern, html)
        pattern = re.compile('<td.*?>(.*?)</td>', re.S | re.I)
        content = re.findall(pattern, str(html_obj))[2]
        # print content
        pattern = re.compile(r'\/jiaoche\/seriepram_\d+\.html', re.I|re.S|re.M)
        url = re.findall(pattern, content)
        url = self.base_url + url[0]
        # print url
        # print serirpram_url
        html = self.send_request(url)
        self.car_data(html)

    def car_data(self, html):
        '''
            获取到需要获取到的参数
        '''
        html_obj = etree.HTML(html)
        car_name_list = html_obj.xpath('//table[@id="serie_pram_tab"]/tr[1]/td/div//a/text()')
        money_list = html_obj.xpath('//table[@id="serie_pram_tab"]/tr[2]/td/text()')[1:]
        construction_list = html_obj.xpath('//table[@id="serie_pram_tab"]/tr[5]/td/text()')[1:]
        oil_list = html_obj.xpath('//table[@id="serie_pram_tab"]/tr[12]/td/text()')[1:]
        display_list = html_obj.xpath('//table[@id="serie_pram_tab"]/tr[29]/td/text()')[1:]
        oil_type_list = html_obj.xpath('//table[@id="serie_pram_tab"]/tr[44]/td/text()')[1:]
        drive_type_list = html_obj.xpath('//table[@id="serie_pram_tab"]/tr[56]/td/text()')[1:]
        # print car_name_list
        # print construction_list
        for car_name, money, construction, oil, display, oil_type, drive_type in zip(car_name_list, money_list, construction_list, oil_list,display_list,oil_type_list, drive_type_list):
            item = dict()
            item['car_name'] = car_name
            item['money'] = money
            item['construction'] = construction.strip()
            item['oil'] = oil
            item['display'] = display
            item['oil_type'] = oil_type
            item['drive_type'] = drive_type
            self.data.append(item)

        self.write_page()
    def write_page(self):
        '''写入到磁盘文件'''
        content = json.dumps(self.data)
        print '正在写入到磁盘文件'
        with open('car.json', 'w') as f:
            f.write(content)

    def start_work(self):
        '''开始工作'''
        html = self.send_request(self.url)
        self.parse(html)


if __name__ == '__main__':
    car = Car()
    car.start_work()
