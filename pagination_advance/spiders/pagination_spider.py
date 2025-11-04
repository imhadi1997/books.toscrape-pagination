import scrapy
import re


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://toscrape.com"]
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    main_url = "https://books.toscrape.com/"
    #   Start of Website - URL from where website start(homepage)
    def start_requests(self):
        yield scrapy.Request(url=self.main_url, callback=self.parse, headers=self.headers)
        


    #   Get all categories Names & URLs from homepage                                                               
    def parse(self, response):
        all_categories = response.xpath('//ul[@class="nav nav-list"]/li/ul/li/a/text()').getall()                                   #   Category Names from a tag
        structured_all_categories = [cat.strip() for cat in all_categories if cat.strip()]                                  #   Removing extra spaces from category names
        category_url = response.xpath('//ul[@class="nav nav-list"]/li/ul/li/a/@href').getall()                              #   Category URLs getting from herf in a tag

        for url_of_catehory, category_name in zip(category_url, structured_all_categories):                                 #   Use loop on list of URLs (url of category) 
                make_category_url = str(self.main_url)+'/'+str(url_of_catehory)                                     
                            
                yield scrapy.Request(
                    url=make_category_url, 
                    callback=self.books_in_category, 
                    cb_kwargs={'category_name': category_name}, 
                    headers=self.headers)                                                                                   #   Parsing url to scrapy parser and calling category page function

    
    #   Function for getting all books from a category
    def books_in_category(self, response, category_name):
            all_books_in_category = response.xpath('//li[@class="col-xs-6 col-sm-4 col-md-3 col-lg-3"]')                    #   Getting all books from a category
                                                                
            for book in all_books_in_category:                                                                              #   Use loop on list of URLs of category to get books in a category
                #all_books_of_a_category = book.xpath('.//article[@class="product_pod"]/h3/a/text()').get()
                url_of_selected_book = book.xpath('.//article[@class="product_pod"]/h3/a/@href').get()
                spliting_href = str(url_of_selected_book).split("/")
                making_url_of_book = str(self.main_url)+"catalogue/"+str(spliting_href[-2])+"/"+str(spliting_href[-1])    #   after split() variable, used indexing to get exactly what i need to make a URL of book
                
                yield scrapy.Request(
                    url=making_url_of_book,
                    callback=self.extarcting_data_of_book,
                    cb_kwargs={'category_name': category_name, 'book_url' : making_url_of_book},
                    headers=self.headers
                )
                
                check_more_pages = response.xpath('//li[@class="next"]/a/@href').get()                                      #   Next button use if more pages - Pagination
                if check_more_pages:                                                                                        #   Recursion - if next button/more books on diff page of a category exists
                    yield response.follow(
                        url=check_more_pages, 
                        callback=self.books_in_category, 
                        cb_kwargs={'category_name' : category_name},
                        headers=self.headers) 
                else:
                    pass

    
    #   Extracting information of Book
    def extarcting_data_of_book(self, response, category_name, book_url):                                                   #   Extracting book information i.e name, price, stock etc
        book_name = response.xpath('//div[@class="col-sm-6 product_main"]/h1/text()').get()
        book_price = response.xpath('//p[@class="price_color"]/text()').get()
        book_rating_class = response.xpath('//p[contains(@class, "star-rating")]/@class').get()
        book_rating = book_rating_class.split()[-1] if book_rating_class else None
        stock_detail = response.xpath('//p[@class="instock availability"]/text()').getall()
        stock_avilability = "".join(stock_detail).strip()

        available_number = re.findall(r'\((\d+)', stock_avilability)
        if available_number:
            available_number = available_number[0]
        else:
            available_number = None


        match_price = re.match(r'([^\d]+)([\d.]+)', book_price)
        if match_price:
            currency = "gbp"                            #"match_price.group(1).strip()"
            price_amount = float(match_price.group(2))
        else:
            currency = None
            price_amount = None

        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        book_rating_int = rating_map.get(book_rating, 0)

        yield {
            'Category Name' : category_name,
            'Book Name' : book_name,
            'Price' : price_amount,
            'Currency' : currency,
            'in Stock' : available_number,
            'Rating' : book_rating_int,
            'URL of Book' : book_url
        }
