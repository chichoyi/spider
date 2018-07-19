import scrapy
from scrapy_splash import SplashRequest
from Chicho.items import ChichoItem
import re

class ChichoSpider(scrapy.Spider):
    name = "chicho"
    allowed_domains = ["hideakihamada.com"]
    start_urls = [
        "http://hideakihamada.com",
    ]

    # 懒得去设置菜单缓存或者去重了，直接在刚才命令行那里copy来的
    tmp_nav = [
        '/people', '/artists', '/family', '/haruandmina', '/haruandmina-2', 'http://www.one-day.jp/', '/goinggrain',
         '/tokyosomewhere', '/myplanet-2014', '/myplanet-2017', '/akikokikuchi-2016', '/toshikiseto-2017',
         '/editorial-2014', '/editorial-2015', '/editorial-2016', '/editorial-2017', '/editorial-2018',
         '/lifestyle-2013', '/lifestyle-2014', '/lifestyle-2015', '/lifestyle-2016', '/lithuania', '/taiwan',
         '/india-2014', '/egypt-2014', '/usa-2014', '/germany-2015', '/japan-tottori-2014', '/japan-kitakyushu',
         '/japan-kagoshima-2015', '/shodoshima-2013', '/shodoshima-2014', '/studiocamelhouse',
         '/toyota-municipal-museum-of-art', '/video', '/books', '/web', '/catalog', '/magazines', '/commercials', '/cv',
         '/blog', '/contact'
    ]
    for i_nav in tmp_nav:
        start_urls.append("http://hideakihamada.com"+i_nav)

    # 在小虫虫发起请求之前，需要接一下刚才那个页面渲染插件
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse, args={'wait':1}, endpoint='render.html')

    def parse(self, response):
        chicho_item = ChichoItem()
        chicho_item['img_url'] = []

        # 获取javascript的url
        tmp_data = response.xpath('//script[@type="text/javascript"]')[1].extract()
        my_tmp_data = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        image_urls = re.findall(my_tmp_data, tmp_data)
        regex = re.compile(r'^.*?(jpg|png|jpeg)$')
        for image_url in image_urls:
            if regex.search(image_url):
                chicho_item['img_url'].append(image_url)

        #获取页面的url
        images = response.css("#supersized").css('img').xpath('@src').extract()
        for image in images:
            chicho_item['img_url'].append(image)
        yield chicho_item