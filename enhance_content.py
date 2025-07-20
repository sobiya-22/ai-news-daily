import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_APIKEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

def format_articles(articles):
    return "".join(
        f"\nTitle: {a['title']}\nContent: {a['content']}\nURL: {a['source_url']}\n---\n" for a in articles
    )

def generate_news_digest(featured, regular):
    prompt = f"""
    You are a helpful and professional assistant summarizing daily tech news.

    FEATURED ARTICLES:
    {format_articles(featured)}

    REGULAR ARTICLES:
    {format_articles(regular)}

    Format:
    1. **Introduction**
    2. **Featured Highlights**: 3-4 concise bullet points
    3. **Quick Bytes**: 1-liner for each regular article
    """
    response = model.generate_content(prompt)
    return response.text
