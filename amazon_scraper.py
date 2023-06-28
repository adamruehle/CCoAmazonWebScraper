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
import threading
from queue import Queue
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

link_count = 0

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

def find_product_links(driver, product_links_queue):
  global link_count
  product_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
  for product_element in product_elements:
    link_element = product_element.find_element(By.CSS_SELECTOR, "h2 a")
    link_url = link_element.get_attribute("href")
    product_links_queue.put(link_url)
    link_count += 1
  print("current link count:", link_count)
  return product_links_queue

def find_next_button(driver, next_button_queue):
  try:
    next_button_queue.put(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next"))))
  except TimeoutException as e:
    next_button_queue.put("DNE")
  return next_button_queue

def dequeu_all(queue):
  result = []
  while not queue:
    item = queue.get()
    result.append(item)
  return result

def iterate_product_pages(driver):
  product_links = []
  while True:
    product_links_queue = Queue()
    next_button_queue = Queue()
    thread_links = threading.Thread(target=find_product_links, args=(driver, product_links_queue))
    thread_next_button = threading.Thread(target=find_next_button, args=(driver, next_button_queue))
    thread_links.start()
    thread_next_button.start()
    thread_links.join()
    thread_next_button.join()
    product_links.extend(dequeu_all(product_links_queue))
    next_button = next_button_queue.get()
    if isinstance(next_button, str) and next_button == "DNE":
      break
    driver.get(next_button.get_attribute("href"))
  return product_links

def initialize_scraper(product_name):
  options = webdriver.ChromeOptions()
  options.add_argument("--headless")
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  use_search_bar(driver, product_name)
  links = iterate_product_pages(driver)
  print("Link Count:", link_count)
  driver.quit()