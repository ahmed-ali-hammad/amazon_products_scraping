from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from product_info import *
import time


options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--incognito ")
driver = webdriver.Chrome('chromedriver.exe', options = options)

class JsonReport:
    def __init__(self):
        pass

class AmazonProductScraper:
    def __init__(self, product_name, filters, url):
        self.product_name = product_name
        self.price_filter = f"rh=p_36%3A{filters['min']}00-{filters['max']}00"
        self.url = url

    def run (self):
        print("running the app")
        self.start_search()
        links = self.get_links()
        asins = self.get_asin(links)
        shortened_links = self.get_shortened_links(asins)
        products_info = self.get_products_info(shortened_links)
        return products_info


    @staticmethod
    def get_links():
        container = driver.find_element_by_xpath("//div[@class='s-main-slot s-result-list s-search-results sg-row']")
        link_elements = container.find_elements_by_xpath("//a[@class='a-link-normal s-no-outline']")
        links = [link.get_attribute('href') for link in link_elements]
        # print(links)
        print(f"number of links are {len(links)}")
        return links


    @staticmethod   
    def get_asin(links):
        asins = []
        count = 0
        for link in links:
            if '%2F' in link:
                updated_link = link.replace('%2F','/')
                dp_index_start = updated_link.find('dp') + 3
                dp_index_end = updated_link.find('ref%') - 1
                dp = updated_link [dp_index_start : dp_index_end]
                asins.append(dp)
                count +=1
            else:
                dp_index_start = link.find('dp') + 3
                dp_index_end = link.find('ref') - 1
                dp = link [dp_index_start : dp_index_end]
                asins.append(dp)
                count +=1
        print(f'number of asins are {count}')
        return asins

    @staticmethod
    def get_shortened_links(asins):
        shortened_links = [f'https://www.amazon.com/dp/{asin}' for asin in asins]
        print(shortened_links)
        return shortened_links


    def start_search(self):
        driver.get(self.url)
        input_box = driver.find_element_by_xpath("//input[@id='twotabsearchtextbox']")
        input_box.send_keys(self.product_name)
        input_box.send_keys(Keys.ENTER)
        filtered_results = driver.current_url + "&" + self.price_filter
        driver.get(filtered_results)
        time.sleep(3)

    @staticmethod
    def get_products_info(shortened_links):
        products_info = []
        for link in shortened_links:
            driver.get(link)
            time.sleep(2)
            try:
                title = driver.find_element_by_xpath("//span[@id='productTitle']").text
            except:
                title = "title not found"
            # seller = 
            try:
                price = driver.find_element_by_xpath("//span[@id='priceblock_ourprice']").text
            except:
                price = "price not found"
            product = {"Product link": link, "title": title, "price": price}
            products_info.append(product)
        print(products_info)
        return products_info


if __name__ == '__main__':
    scraped_data = AmazonProductScraper(product_name, filters, url)
    data = scraped_data.run()





