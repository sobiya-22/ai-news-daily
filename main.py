import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
# from config import VENTUREBEAT_AI_URL
from query_data import upload_articles_to_bigquery,fetch_articles_by_type, store_digest
from enhance_content import generate_news_digest
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def parse_article(driver, url, article_type):
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        return {
            "title": driver.find_element(By.CSS_SELECTOR, "h1.article-title").text,
            "content": driver.find_element(By.CSS_SELECTOR, "div.article-content").text,
            "source_url": url,
            "scraped_at": datetime.now().isoformat(),
            "article_type": article_type
        }
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return None

def scrape_articles(driver, css_selector, article_type, limit=5):
    driver.get(os.getenv("VENTUREBEAT_AI_URL"))
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )
    links = [a.get_attribute("href") for a in driver.find_elements(By.CSS_SELECTOR, css_selector)][:limit]
    scraped = []
    for link in links:
        print(f"Scraping {article_type.capitalize()} Article: {link}")
        article = parse_article(driver, link, article_type)
        if article:
            scraped.append(article)
    return scraped

def main():
    driver = setup_driver()
    try:
        featured = scrape_articles(driver, "article.FeaturedArticles__article > a", "featured", limit=2)
        regular = scrape_articles(driver, "#river a.ArticleListing__image-link", "regular", limit=5)

        all_articles = featured + regular
        with open("venturebeat_articles.json", "w", encoding="utf-8") as f:
            json.dump(all_articles, f, indent=4, ensure_ascii=False)
        print("Articles saved to JSON")

        upload_articles_to_bigquery(all_articles)

        featured_articles = fetch_articles_by_type("featured")
        regular_articles = fetch_articles_by_type("regular")

        if not (featured_articles or regular_articles):
            print("No articles found for today.")
            return

        digest = generate_news_digest(featured_articles, regular_articles)
        print("\nDaily Digest:\n")
        print(digest)
        print('Storing data to bigquery: \n')
        store_digest(digest)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()


