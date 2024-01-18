import scrapy


class WorkUaSpider(scrapy.Spider):
    name = "workua"
    start_urls = ["https://www.work.ua/jobs-chernivtsi_cv/"]
    scraped_count = 0

    def parse_vacancy(self, response):
        title = response.xpath('//h1[@id="h1-name"]/text()').get()
        salary = response.css(".glyphicon-hryvnia")[-1].xpath("./following-sibling::span/text()").get().replace("\u202f", "").replace("\u2009", "").replace("\xa0", "")
        if "грн" not in salary:
            salary = None
        description = "".join(response.xpath('//div[@id="job-description"]').getall())

        employer = response.css(".glyphicon-company").xpath("./following-sibling::a/span/text()").get()
        yield {"url": response.url, "title": title, "salary": salary, "employer": employer, "description": description}


    def parse(self, response):
        for card in response.css(".card"):
            vacancy_url = card.css(".add-bottom").xpath("./h2/a/@href").get()
            if vacancy_url is None:
                continue
            yield response.follow(vacancy_url, callback=self.parse_vacancy)
            self.scraped_count += 1
            if self.scraped_count >= 20:
                self.crawler.engine.close_spider(self, 'Зібрано 10 елементів')
        next_page = response.css(".pagination").xpath("./li")[-1].xpath("./a/@href").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
