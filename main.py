# Import necessary modules
from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
import os
from dotenv import load_dotenv  # Load environment variables from .env file

# Load environment variables from .env file
load_dotenv()
# Get URLs from environment variables
ZILLOW_URL = os.environ.get("ZILLOW_URL")
FORM_URL = os.environ.get("FORM_URL")

# --- Part 1: Scrape data from Zillow Clone ---

# Send HTTP request to the Zillow-Clone site
response = requests.get(ZILLOW_URL)
zillow_web_page = response.text

# Lists to store scraped data
prices = []
links = []
addresses = []

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(zillow_web_page, "html.parser")
apartments = soup.find_all("div", class_="StyledPropertyCardDataWrapper")

# Loop through each apartment listing to extract price, link, and address
for apartment in apartments:
    # Extract price and clean it (remove non-digit characters except commas)
    price = apartment.find("span", class_="PropertyCardWrapper__StyledPriceLine").get_text(strip=True)
    clean_price = f'${re.sub(r"[^\d,]", "", price)}'
    prices.append(clean_price)
    # Extract link to the listing
    link = apartment.find("a" ,href=True)["href"]
    links.append(link)
    # Extract address and clean it (remove "|" symbol)
    address = apartment.find("address").get_text(strip=True).replace("|", "")
    addresses.append(address)

# --- Part 2: Fill in the Google Form using Selenium ---

# Configure Chrome to stay open after script finishes
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
# Open Chrome browser
driver = webdriver.Chrome(options=chrome_options)
driver.get(FORM_URL)
# Explicit wait for elements to load
wait = WebDriverWait(driver, 5)

# Loop through all apartment listings and submit them to the Google Form
for i in range(len(apartments)):
    # Find input fields using their aria-labelledby attributes
    address_box = driver.find_element(By.XPATH,
                                      '//input[@aria-labelledby="i1 i4"]')
    price_box = driver.find_element(By.XPATH,
                                    '//input[@aria-labelledby="i6 i9"]')
    link_box = driver.find_element(By.XPATH,
                                   '//input[@aria-labelledby="i11 i14"]')
    # Find the submit button
    send_button = driver.find_element(By.XPATH, '//div[@role="button" and @aria-label="Submit"]')
    # Enter data into form fields
    address_box.click()
    address_box.send_keys(addresses[i])
    price_box.click()
    price_box.send_keys(prices[i])
    link_box.click()
    link_box.send_keys(links[i])
    # Click the submit button
    send_button.click()
    # Wait for "Submit another response" link and click it
    send_another_form = wait.until(ec.presence_of_element_located((By.XPATH , '/html/body/div[1]/div[2]/div[1]/div/div[4]/a')))
    send_another_form.click()
    time.sleep(3) # short pause to allow page to load

# Close the browser after finishing
driver.quit()