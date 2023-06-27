import amazon_scraper

def main():
  product_name = input("Enter a product to scrape: ")
  amazon_scraper.initialize_scraper(product_name)

if __name__ == "__main__":
  main()