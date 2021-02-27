from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from product_info import *
import time
import json


options = webdriver.ChromeOptions()  # initializing the chrome options
options.add_argument("--headless")   # to run in the background
options.add_argument("--incognito ") # to run in incognito mode
driver = webdriver.Chrome('chromedriver.exe', options = options)

class JsonReport: # this class is used to save the scraped data to an external json file
    def __init__(self, data):
        self.data = data

    def json_create(self):
        print('saving the scraped data to an external file')
        with open ("scraped_data.json", "w") as f:
            json.dump(self.data, f , indent = 2)




class AmazonProductScraper: # this class is used to scrape the data
    def __init__(self, product_name, filters, url):
        self.product_name = product_name
        self.price_filter = f"rh=p_36%3A{filters['min']}00-{filters['max']}00" # this string is added to amazon search link to filter the results based on price range
        self.url = url # amazon.com url

    def run (self): # this method is responsible for excuring all the other methods inside the class
        print("running the app")
        self.start_search()
        links = self.get_links()
        asins = self.get_asin(links) # to get the unique id numnber for each item
        shortened_links = self.get_shortened_links(asins)
        products_info = self.get_products_info(shortened_links)
        driver.quit()
        return products_info


    def start_search(self):
        driver.get(self.url) # starting the driver
        input_box = driver.find_element_by_xpath("//input[@id='twotabsearchtextbox']") # locating the search box
        input_box.send_keys(self.product_name) # starting the search
        input_box.send_keys(Keys.ENTER)
        filtered_results = driver.current_url + "&" + self.price_filter # adding the price filter to narrow down the search
        driver.get(filtered_results)
        time.sleep(1) # waitng for the page to load all the items


    @staticmethod
    def get_links(): # this method is responsible for getting the the link for each item
        container = driver.find_element_by_xpath("//div[@class='s-main-slot s-result-list s-search-results sg-row']")
        link_elements = container.find_elements_by_xpath("//a[@class='a-link-normal s-no-outline']")
        links = [link.get_attribute('href') for link in link_elements]
        # print(f"number of links are {len(links)}")
        return links


    @staticmethod   
    def get_asin(links): # this method is used to get the unique id for each product
        asins = []
        count = 0
        for link in links:
            if '%2F' in link:
                updated_link = link.replace('%2F','/')
                dp_index_start = updated_link.find('dp') + 3
                dp_index_end = updated_link.find('ref%') - 1
                dp = updated_link [dp_index_start : dp_index_end]
                asins.append(dp)
                count += 1
            else:
                dp_index_start = link.find('dp') + 3
                dp_index_end = link.find('ref') - 1
                dp = link [dp_index_start : dp_index_end]
                asins.append(dp)
                count += 1
        # print(f'number of asins are {count}')
        return asins

    @staticmethod
    def get_shortened_links(asins):
        shortened_links = [f'https://www.amazon.com/dp/{asin}' for asin in asins]
        # print(shortened_links)
        return shortened_links



    @staticmethod
    def get_products_info(shortened_links): # this method is used to scrape the data form each product page individually
        products_info = []
        for link in shortened_links:
            driver.get(link) 
            time.sleep(1) # waiting for the page to load
            try:
                title = driver.find_element_by_xpath("//span[@id='productTitle']").text
            except:
                title = "Title not found"
            # seller = 
            try:
                price = driver.find_element_by_xpath("//span[@id='priceblock_ourprice']").text
            except:
                price = "Price not found"

            product = {"Product link": link, "Title": title, "Price": price}
            products_info.append(product)
        # print(products_info)
        return products_info


if __name__ == '__main__': 
    scraped_data = AmazonProductScraper(product_name, filters, url)
    data = scraped_data.run()
    json_output = JsonReport(data)
    json_output.json_create()





