from google.cloud import bigquery
from datetime import date
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
RAW_TABLE_NAME = os.getenv("RAW_TABLE_NAME")
ENHANCED_TABLE_NAME = os.getenv("ENHANCED_TABLE_NAME")
RAW_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{RAW_TABLE_NAME}"
ENHANCED_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{ENHANCED_TABLE_NAME}"


bq_client = bigquery.Client(project=PROJECT_ID)

def fetch_articles_by_type(article_type):
    query = f"""
    SELECT title, content, source_url, scraped_at, article_type
    FROM `{RAW_TABLE_ID}`
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

    job = bq_client.load_table_from_json(data,ENHANCED_TABLE_ID, job_config=job_config)
    job.result()
    print(f"Digest uploaded to BigQuery: {len(data)} record(s)")


def upload_articles_to_bigquery(data):
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    )
    print("RAW_TABLE_ID =", RAW_TABLE_ID)
    job = bq_client.load_table_from_json(data,RAW_TABLE_ID, job_config=job_config)
    job.result()
    print(f"Uploaded {len(data)} article(s) to BigQuery")

def fetch_enhanced_news():
    query=f"SELECT news_date, generated_news FROM `{ENHANCED_TABLE_ID}` WHERE news_date = CURRENT_DATE()"
    results = bq_client.query(query).result()

    return [
        {
            "news_date": row.news_date.isoformat(),
            "generated_news": row.generated_news
        } for row in results]



def upload_subscriber_email(email):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.subscribers"
    data = [{
        "email": email,
        "subscribed_at": datetime.now().isoformat()
    }]
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    )

    try:
        job = bq_client.load_table_from_json(data, table_id, job_config=job_config)
        job.result() 
        return {
            "success": True,
            "message": f"{email} subscribed successfully!"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Failed to subscribe {email}: {e}"
        }
    
def fetch_subscriber_emails():
    query = f"""
        SELECT email
        FROM `{PROJECT_ID}.{DATASET_ID}.subscribers`
    """
    try:
        result = bq_client.query(query)
        emails = [row["email"] for row in result]
        return emails
    except Exception as e:
        print(f"❌ Failed to fetch subscribers: {e}")
        return []