import scrapy

class PaginationSpiderSpider(scrapy.Spider):
    name = "pagination_spider"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://toscrape.com"]
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    category_name = ""

    def start_requests(self):
          yield scrapy.Request(url="https://books.toscrape.com/index.html", callback=self.parse)


    def parse(self, response):
        categories_url = response.xpath('//ul[@class="nav nav-list"]/li/ul/li/a/@href').getall()
        for i in categories_url:
            making_url = "https://books.toscrape.com/"+str(i)
            self.category_name = str(i)
            yield scrapy.Request(
                url=making_url, callback=self.category_page, headers=self.headers
            )    
            
    def category_page(self, response):
        all_books_in_category = response.xpath('//li[@class="col-xs-6 col-sm-4 col-md-3 col-lg-3"]')
        
        for books in all_books_in_category:
            spliting_cat = self.category_name.split('/')
            aftersplit = (spliting_cat[3]).split("_")
            split_after_split = aftersplit[0]
            booke_name = books.xpath('.//article[@class="product_pod"]/h3/a/text()').get()
            book_price = (books.xpath('.//div[@class="product_price"]/p[@class="price_color"]/text()').get().strip()) 
            rating = (books.xpath('.//p[contains(@class,"star-rating")]/@class').get() or '').split()[-1].strip()
            stock_available = books.xpath('.//p[@class="instock availability"]/text()').get()
            stock_available = ''.join(stock_available).strip()
            
            yield {
                    'category_url' : split_after_split,
                    'book_name' : booke_name,
                    'price' : book_price,
                    'Stock availablity' : stock_available,
                    'rating' : rating
            }

            next_page = response.xpath('//li[@class="next"]/a/@href').get()
            if next_page:
                yield response.follow(next_page, callback=self.category_page, headers=self.headers)