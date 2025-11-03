import scrapy
import re

class PaginationSpiderSpider(scrapy.Spider):
    name = "pagination_spider"
    start_urls = ["https://toscrape.com"]
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }


    def start_requests(self):
        yield scrapy.Request(url="https://books.toscrape.com/index.html", callback=self.parse)

    def parse(self, response):
        categories_url = response.xpath('//ul[@class="nav nav-list"]/li/ul/li/a/@href').getall()
        for i in categories_url:
            making_url = "https://books.toscrape.com/"+str(i)
            yield scrapy.Request(
                url=making_url, callback=self.category_page, headers=self.headers
            )    
            
    def category_page(self, response):
        all_books_in_category = response.xpath('//li[@class="col-xs-6 col-sm-4 col-md-3 col-lg-3"]')
        
        for books in all_books_in_category:
            category_name = books.xpath('//div[@class="page-header action"]/h1/text()').get()
            booke_name = books.xpath('.//article[@class="product_pod"]/h3/a/text()').get()
            book_price = books.xpath('.//div[@class="product_price"]/p[@class="price_color"]/text()').get()
            rating = (books.xpath('.//p[contains(@class,"star-rating")]/@class').get() or '').split()[-1].strip()
            stock_available = books.xpath('.//p[@class="instock availability"]/text()').getall()
            stock_status = "".join(c.strip() for c in stock_available if c.strip())

            match_price = re.match(r'([^\d]+)([\d.]+)', book_price)
            if match_price:
                currency = match_price.group(1).strip()
                price_amount = float(match_price.group(2))
            else:
                currency = None
                price_amount = None


            yield {
                    'Category' : category_name,
                    'Book name' : booke_name,
                    'Book Price' : price_amount,
                    'Currency' : currency,
                    'Stock availablity' : stock_status,
                    'Rating' : rating
            }

            next_page = response.xpath('//li[@class="next"]/a/@href').get()
            if next_page:
                yield response.follow(next_page, callback=self.category_page, headers=self.headers)
