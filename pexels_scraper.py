from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import sys

def get_new_height(driver):
    # Scroll down using PAGE_DOWN multiple times
    for _ in range(50):  # Simulate a user scrolling gradually
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)  

    new_height = driver.execute_script("return document.body.scrollHeight")

    return new_height

def scrape_pexels_images(search_url, max_scrolls=100):
    # Setup Selenium WebDriver
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    driver.get(search_url)
    
    image_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    try:
        os.remove("output.txt")
        print("output file removed")
    except:
        print("output file was already removed")

    with open('output.txt', 'w') as f:
        for _ in range(max_scrolls):
            # Extract image elements
            images = driver.find_elements(By.CSS_SELECTOR, "img[srcset]")

            for img in images:
                img_url = img.get_attribute("srcset")
                    
                start = img_url.find('1200w, ') + 7
                end = img_url.find(' 1600w', start)
                url_max_res= img_url[start:end]
                if url_max_res not in image_urls:
                    image_urls.add(url_max_res)
                    print(url_max_res)
                    f.write(url_max_res+"\n")

            new_height= get_new_height(driver)

            if  new_height== last_height:
                print("Reached end of page or no new images found.")
                break  # Stop scrolling if no more content is loading
            last_height = new_height  # Update last height

        driver.quit()
        return list(image_urls)

if __name__ == "__main__":
    
    url = sys.argv[1]
    
    print ("Scraping Pexel website for images URL {}".format(url))

    image_links = scrape_pexels_images(url)

    
    