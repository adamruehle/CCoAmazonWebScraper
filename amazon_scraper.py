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

def scrape_amazon_data(product_name):
  options = webdriver.ChromeOptions()
  # options.add_argument("--headless")
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  driver.get("https://www.amazon.com/")
  wait = WebDriverWait(driver, 10)
  search_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[id='twotabsearchtextbox']")))
  search_input.send_keys(product_name)
  search_input.submit()
  print("Current URL:", driver.current_url)
