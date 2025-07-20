from google.cloud import bigquery
from datetime import date
# from config import PROJECT_ID, RAW_TABLE_ID, ENHANCED_TABLE_ID
from dotenv import load_dotenv
import os
load_dotenv()

bq_client = bigquery.Client(project=os.getenv("PROJECT_ID"))

def fetch_articles_by_type(article_type):
    query = f"""
    SELECT title, content, source_url, scraped_at, article_type
    FROM `{os.getenv("RAW_TABLE_ID")}`
    WHERE DATE(scraped_at) = CURRENT_DATE() AND LOWER(article_type) = '{article_type.lower()}'
    """
    results = bq_client.query(query).result()
    return [
        {
            "title": row.title,
            "content": row.content,
            "source_url": row.source_url,
            "scraped_at": row.scraped_at.isoformat(),
            "article_type": row.article_type
        } for row in results
    ]

def store_digest(digest_text):
    data = [{
        "news_date": date.today().isoformat(),
        "generated_news": digest_text,
    }]

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    )

    job = bq_client.load_table_from_json(data, os.getenv("ENHANCED_TABLE_ID"), job_config=job_config)
    job.result()
    print(f"Digest uploaded to BigQuery: {len(data)} record(s)")


def upload_articles_to_bigquery(data):
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    )

    job = bq_client.load_table_from_json(data, os.getenv("RAW_TABLE_ID"), job_config=job_config)
    job.result()
    print(f"Uploaded {len(data)} article(s) to BigQuery")
