from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

project_directory = os.getenv("PROJECT_DIR")
page_directory = os.path.join(project_directory, r'Data\pages')

class WebCrawler(CrawlSpider):
    name = "mycrawler"
    allowed_domains = ["community.canvaslms.com"]
    start_urls = ["https://community.canvaslms.com/t5/All-Product-Guides/ct-p/all_guides",
                  "https://community.canvaslms.com/t5/Instructor-Guide/Instructor-Getting-Started-Resources/ta-p/579378",
                  "https://community.canvaslms.com/t5/Canvas-Basics-Guide/Where-do-I-find-my-institution-s-URL-to-access-Canvas/ta-p/82",
                  "https://community.canvaslms.com/t5/Troubleshooting/Logging-into-Canvas/ta-p/875",
                  "https://community.canvaslms.com/t5/Canvas-Basics-Guide/tkb-p/basics",
                  "https://community.canvaslms.com/t5/Video-Guide/Canvas-Overview-Students/ta-p/383771",
                  "https://community.canvaslms.com/t5/Student-Guide/Student-Getting-Started-Resources/ta-p/579371",
                  "https://community.canvaslms.com/t5/Instructor-Guide/Instructor-Getting-Started-Resources/ta-p/579378",
                  "https://community.canvaslms.com/t5/Admin-Guide/Admin-Getting-Started-Resources/ta-p/579393",
                  "https://community.canvaslms.com/t5/Observer-Guide/Observer-Parent-Getting-Started-Resources/ta-p/579341"]

    rules = (
        Rule(LinkExtractor(allow="t5/Canvas-Basics-Guide"), callback="parse_detail"),
        Rule(LinkExtractor(allow="t5/Troubleshooting"), callback="parse_detail"),
        Rule(LinkExtractor(allow="t5/Video-Guide"), callback="parse_detail"),
        Rule(LinkExtractor(allow="t5/Student-Guide"), callback="parse_detail"),
        Rule(LinkExtractor(allow="t5/Instructor-Guide"), callback="parse_detail"),
        Rule(LinkExtractor(allow="t5/Admin-Guide"), callback="parse_detail"),
        Rule(LinkExtractor(allow="t5/Observer-Guide"), callback="parse_detail"),
    )

    seen = {}

    def replace_title(self, title, url):
        replace = title
        for x in ["Student", "Admin", "Instructor", "Observer"]:
            if (x + "-Guide") in url and "How do I" in title:
                role = "as a " + x.lower() if x == "Student" else "as an " + x.lower() 
                if role not in title:
                    replace =  replace + " " + role
        # for x in ["Student-Guide", "Admin-Guide", "Instructor-Guide", "Observer-Guide", "Video-Guide", "Canvas-Basics-Guide", "Troubleshooting"]:
        #     if x in url and x.replace("-", " ") not in title:
        #         replace = x.replace("-", " ") + " - " + replace
        return replace

    def extract_title(self, response):
        title = response.css('div.lia-message-subject::text').getall()
        title = ''.join(title)
        if len(title.strip()) == 0:
            title = response.css('title::text').getall()
            title = ''.join(title)
        replace_char = ['\n', '\t', '?', '!', ':', '*']
        for char in replace_char:
            title = title.replace(char, '')

        title = title.replace('/', ' or ')
        title = title.replace("’", "'")
        return title

    def parse_detail(self, response):
        curr_url = response.url.replace('community.canvaslms.com:443', 'community.canvaslms.com')
        title = self.extract_title(response)
        title = self.replace_title(title , curr_url)
        WebCrawler.seen[curr_url] = title
        yield {
            'url': curr_url,
            'title': title
        }

        # for img in response.css('div.lia-message-body-content img::attr(src)').getall():
        #     item = NeuralcrawlingItem()
        #     item['image_urls'] = [response.urljoin(img)]
        #     yield item

        content = response.css('div.lia-message-body-content').get()
        if content is not None:
            filename = WebCrawler.seen[curr_url]

            with open(os.path.join(page_directory, filename), 'w', encoding='utf-8') as f:
                f.write(content)

            self.log(f'Saved file {filename}')


def run_crawler(spider_name):
    output_file = os.path.join(project_directory, r'Data\urls.json')
    if os.path.exists(output_file):
        os.remove(output_file)
    subprocess.run(['scrapy', 'crawl', spider_name, '-o', output_file])

run_crawler(WebCrawler.name)