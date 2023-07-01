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
from concurrent.futures import ThreadPoolExecutor

link_count = 0

def use_search_bar(driver, product_name):
  driver.get("https://www.amazon.com/")
  wait = WebDriverWait(driver, 10)
  search_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[id='twotabsearchtextbox']")))
  search_input.send_keys(product_name)
  search_input.submit()
  return driver.current_url

def find_product_links(driver, product_links_queue):
  global link_count
  product_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
  for product_element in product_elements:
    link_element = product_element.find_element(By.CSS_SELECTOR, "h2 a")
    link_url = link_element.get_attribute("href")
    product_links_queue.put(link_url)
    link_count += 1
  return product_links_queue

def find_next_button(driver, next_button_queue):
  try:
    next_button = WebDriverWait(driver, 20).until(
      EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next"))
    )
    next_button_queue.put(next_button)
  except TimeoutException as e:
    next_button_queue.put(None)
  return next_button_queue

def find_previous_button(driver, previous_button_queue):
  try:
    next_button = WebDriverWait(driver, 20).until(
      EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-previous"))
    )
    previous_button_queue.put(next_button)
  except TimeoutException as e:
    previous_button_queue.put(None)
  return previous_button_queue

def dequeu_all(queue):
  result = []
  while not queue:
    item = queue.get()
    result.append(item)
  return result

def iterate_pages_forward(driver, midpoint):
  global link_count
  product_links = []
  for i in range(1, midpoint):
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
    driver.get(next_button.get_attribute("href"))
    print("Current link count in forward:", link_count)
  return product_links

def iterate_pages_backward(driver, url, midpoint, last_page_number):
  url_parts = url.split("&")
  new_url = "&".join(url_parts[:-2]) + f"&page={last_page_number}"
  driver.get(new_url)
  global link_count
  product_links = []
  for x in range(last_page_number, midpoint):
    product_links_queue = Queue()
    previous_button_queue = Queue()
    thread_links = threading.Thread(target=find_product_links, args=(driver, product_links_queue))
    thread_previous_button = threading.Thread(target=find_previous_button, args=(driver, previous_button_queue))
    thread_links.start()
    thread_previous_button.start()
    thread_links.join()
    thread_previous_button.join()
    product_links.extend(dequeu_all(product_links_queue))
    previous_button = previous_button_queue.get()
    driver.get(previous_button.get_attribute("href"))
    print("Current link count in backward:", link_count)
  return product_links

def iterate_pages_forward_wrapper():
  driver = initialize_driver()  # Initialize a new driver in the subprocess
  iterate_pages_forward(driver, midpoint)

def iterate_pages_backward_wrapper():
  driver = initialize_driver()  # Initialize a new driver in the subprocess
  iterate_pages_backward(driver, url, midpoint, last_page_number)

def scrape_data(driver, product_name):
  global link_count
  print("Searching for product...")
  url = use_search_bar(driver, product_name)
  print("Gathering links...")
  last_page_elements = driver.find_elements(By.CSS_SELECTOR, "span.s-pagination-item.s-pagination-disabled")
  last_page_number = int(last_page_elements[1].text.strip())
  midpoint = (int)(last_page_number / 2) + 1
  with ThreadPoolExecutor() as executor:
    forward_links_future = executor.submit(iterate_pages_forward, driver, midpoint)
    backward_links_future = executor.submit(iterate_pages_backward, driver, url, midpoint, last_page_number)

    forward_links_future.result()
    backward_links_future.result()
  print("Total link count:", link_count)

def initialize_driver():
  options = webdriver.ChromeOptions()
  options.add_argument("--headless")
  options.add_argument("--log-level=3")
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  return driver

def quit_driver(driver):
  driver.quit()