我是如何分析和爬取外国网站的图片

### 确定爬取的对象  

我的爬取网站是：http://hideakihamada.com

在浏览器F12打开查看页面元素，分析一下这个网站的情况，可以看到幻灯片的图片地址藏在这个id=supersized的ul标签里面，也看到页面导航栏的元素是id=menu的ul标签下面，粗略分析之后，我们才来开始安装环境也写代码。



## 搭建python环境（docker）

docker环境不用说啦，一条语句就可以搞定的事情
我自己使用的是3.5的版本，其他版本请随意

    docker pull python:3.5
    
## 进入容器安装爬虫框架

    pip install scrapy 
    
    
### 创建爬虫项目

    scrapy startproject CrawlImages
    

### 命令行调试爬取对象的页面元素

    scrapy shell http://hideakihamada.com
    
    # 使用选择器输出页面的元素
    response.css('#menu').css('a').xpath('@href').extract()
    
    # 可以看到正常输出导航栏的菜单元素
    
    # 接下来输出幻灯片的地址
    response.css('#supersized')


瓦特，这是怎么回事，明明页面有的元素，这个万能的爬虫选择器为什么没法get到我要的数据呢。还是得好好思考一下，我脑子一下子复杂起来，懒加载？后端渲染数据？前端渲染数据？不知道什么回事，我在浏览器页面审核元素找了找，发现了更多的秘密，原来在scrapt里面还有后面才渲染出来的变量，存了特别多的照片url。直觉告诉我，这个网站还没全部加载完就被我的小虫虫先爬了一下，于是后面加载的数据小虫虫就拿不到数据了。于是找了一下相关插件，先不找是不是最强的，找个能用的就好，这个插件就是辅助小虫虫在拿到页面之前把网站先全部加载完，不管该网站用什么技术去渲染。


## 安装渲染网页的插件

- 专门渲染网页的插件——splash，docker安装即可

    
    docker run -p 8050:8050 --name=splash scrapinghub/splash

    #查看容器的ip地址
    docker inspect splash
    
可以用主机ip加端口浏览器访问是不是能正常打开，能的话就恭喜你了，下面我们继续分析


### 爬虫代码

    # 在项目 CrawlImagesItem 里面加个字段可以保存url的
    img_url = scrapy.Field()
    
    
爬虫配置
    
    # 在settings文件里面添加配置项
    
    SPLASH_URL = 'http://172.17.0.2:8050'  #这个ip一定要通的，不然小虫虫访问不到就没用了
    
    #下载器中间件
    DOWNLOADER_MIDDLEWARES = {
        'scrapy_splash.SplashCookiesMiddleware': 723,
        'scrapy_splash.SplashMiddleware': 725,
        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    }
    
    SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    }
    
    # 去重过滤器
    DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
    # 使用Splash的Http缓存
    HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
    
爬虫代码

    # CrawlImages.py
    
    name = "chicho"
    allowed_domains = ["hideakihamada.com"]
    start_urls = [
        "http://hideakihamada.com",
    ]
        
    # 在小虫虫发起请求之前，需要接一下刚才那个页面渲染插件
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse, args={'wait':1}, endpoint='render.html')
            
            
    def parse(self, response):
        images_item = CrawlImagesItem()
        images_item['img_url'] = []

        #获取页面的url
        images = response.css("#supersized").css('img').xpath('@src').extract()
        # 这里输出看是不是正常能输出渲染后的数据
        print(images)
        
        for image in images:
            images_item['img_url'].append(image)
        yield images_item
        
接下来运行代码一步步调试

    scrapy crawl CrawlImages
    
print(images)能输出元素出来，说明刚才的那个插件没问题了，继续往下走

### 一个网站多个菜单，我们需要让小虫虫去自动发现爬取其他页面的数据

还是这个文件里面 CrawlImages.py

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
        
不要忘了刚才在分析问题的时候遗漏的重要东西，就是该网站把很多图片的url渲染到js变量里面了，我们需要拿下来扔到item里面，于是改装一下parse方法

        def parse(self, response):
        chicho_item = ChichoItem()
        chicho_item['img_url'] = []

        # 获取script标签里面所有的url
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
        
我们的目的是搞事情阿，就是要下载发现的所有图片，所以当然少不了下载图片的代码
接下来在settings文件里面加上配置
    
    # 图片存储设置
    IMAGES_STORE = '/www/images'  //路径看着办，根据自己项目情况修改
    
    # 里面的PIPELINES指向的是项目pipelines文件的类
    ITEM_PIPELINES = {
        'Chicho.pipelines.CrawlImagesPipeline': 2,
        'Chicho.pipelines.MyImagesPipeline': 1
    }
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
    
    
写pipelines文件的代码

    
    from scrapy.pipelines.images import ImagesPipeline
    import scrapy
    
    class CrawlImagesPipeline(object):
    
        def process_item(self, item, spider):
            return item
    
    
    class MyImagesPipeline(ImagesPipeline):
    
        def get_media_requests(self, item, info):
            for url in item['img_url']:
                yield scrapy.Request(url, meta={'item': item})
                

写到这里已经可以吃饭了，饿了没心思继续写了，最后一行代码结束这个文章，剩下的看你自己的造化了

    scrapy crawl CrawlImages