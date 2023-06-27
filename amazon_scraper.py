import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import datetime

def use_search_bar(driver, product_name):
  driver.get("https://www.amazon.com/")
  wait = WebDriverWait(driver, 10)
  search_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[id='twotabsearchtextbox']")))
  search_input.send_keys(product_name)
  search_input.submit()
  print("Current URL:", driver.current_url)

def find_product_at_index(driver, index):
  try:
    product_elements = driver.find_elements("css selector", "div[data-component-type='s-search-result']")
    if index < len(product_elements):
      product_element = product_elements[index]
      link_element = product_element.find_element(By.CSS_SELECTOR, "h2 a")
      link_url = link_element.get_attribute("href")
      print("Link URL:", link_url)
    else:
      print("Product index is out of range.")
  except Exception as e:
      print("Error occurred:", str(e))

def initialize_scraper(product_name):
  options = webdriver.ChromeOptions()
  # options.add_argument("--headless")
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  use_search_bar(driver, product_name)
  find_product_at_index(driver, 0)
  driver.quit()