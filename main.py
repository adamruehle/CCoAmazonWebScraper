import amazon_scraper

def main():
  driver = amazon_scraper.initialize_driver()
  print("Scrape (s) ListProduct (p) Quit (q)")
  user_input = ""
  while True:
    user_input = input("What should I do? ")
    if user_input == "s":
      product_to_search = input("Enter a product to search for: ")
      amazon_scraper.scrape_data(driver, product_to_search)
    if user_input == "q":
      print("Exiting...")
      amazon_scraper.quit_driver(driver)
      break


if __name__ == "__main__":
  main()