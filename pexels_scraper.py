from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
import time
import os
import logging
import argparse
from datetime import datetime
import requests

def create_output_folder(path: str)-> str:
    """Ensures the specified directory exists, creating it if necessary."""
    try:
        if not os.path.isdir(path):
            os.makedirs(path)
    except Exception as e:
        logging.error(f"Error creating folder {path}: {e}")        
        
    return path

def remove_file(path: str)-> str:
    try:
        os.remove(path)
        logging.debug("Output file removed")
    except:
        logging.debug("Output file was already removed")

def download_image (path, image_url, name):
    img_data = requests.get(image_url).content
    with open(path+'/'+str(name)+'.jpeg', 'wb') as handler:
        handler.write(img_data)

def get_new_height(driver):

    # Scroll down using PAGE_DOWN multiple times
    for _ in range(50):  # Simulate a user scrolling gradually
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)  

    new_height = driver.execute_script("return document.body.scrollHeight")

    logging.debug("New height is: {}",new_height)

    return new_height

def scrape_pexels_images(keyword,output_folder,max_scrolls=100,):

    # Setup Selenium WebDriver
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    driver.get("https://www.pexels.com/search/"+keyword)

    try:
        while True:

            logging.info("Scraping process is running... press CTRL-C to quit.")

            image_urls = set()
            last_height = driver.execute_script("return document.body.scrollHeight")
            counter=0

            create_output_folder(output_folder)

            kw_output_folder=create_output_folder(output_folder+"/"+keyword)

            remove_file(kw_output_folder+"/output.txt")

            with open(kw_output_folder+"/output.txt", 'w') as f:
                for _ in range(max_scrolls):
                    # Extract image elements
                    images = driver.find_elements(By.CSS_SELECTOR, "img[srcset]")
                    new_images = len(images)-counter
                    logging.info("Found " +str(new_images)+' new images')
                    for img in images:

                        img_url = img.get_attribute("srcset")        
                        start = img_url.find('1200w, ') + 7
                        end = img_url.find('?auto=compress&cs=tinysrgb&w=1600', start)
                        url_max_res= img_url[start:end]

                        if url_max_res not in image_urls:

                            image_urls.add(url_max_res)

                            logging.debug("Downloading: " +url_max_res)

                            download_image(kw_output_folder,url_max_res,counter)
                            f.write(url_max_res+"\n")
                            counter+=1


                    new_height= get_new_height(driver)

                    if  new_height== last_height:
                        logging.info("Reached end of page or no new images found.")
                        break  # Stop scrolling if no more content is loading
                    last_height = new_height  # Update last height

                
                return list(image_urls)    

    except KeyboardInterrupt:
        logging.info("Interrupted by user...")
    finally:
        logging.info("Closing Selenium WebDriver")
        driver.quit()
        logging.info("Tschüss!")        
        

   

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)

    # Initialize the parser
    parser = argparse.ArgumentParser(description='Scraper for licence-free images')
    
    # Add arguments
    parser.add_argument('--keyword', action="store", dest='keyword', default='doves')
    parser.add_argument('--output-folder', action="store", dest='output_folder', default='output')
    
    # Parse the arguments
    args = parser.parse_args()
    
    logging.info("Scraping Pexel website for images of {}".format(args.keyword))

    scrape_pexels_images(args.keyword, args.output_folder)


    