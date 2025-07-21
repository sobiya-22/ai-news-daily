import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_APIKEY")
if not api_key:
    raise EnvironmentError("GEMINI_APIKEY is not set in environment variables.")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-pro")

# Format articles
def format_articles(articles):
    return "".join(
        f"\nTitle: {a['title']}\nContent: {a['content']}\nURL: {a['source_url']}\n---\n" for a in articles
    )

# Generate news digest
def generate_news_digest(featured, regular):
    prompt = f"""
    You are an intelligent, concise, and professional assistant tasked with generating a daily tech news digest suitable for email distribution. The digest should highlight the most important stories of the day in a clean and reader-friendly format.

    Below are two sets of articles:

    FEATURED ARTICLES:
    {format_articles(featured)}

    REGULAR ARTICLES:
    {format_articles(regular)}

    Please generate the email content using the following structure:

    1. **Opening Summary**  
    A short 2-3 line introduction that gives readers a quick overview of today's tech news—mention any major themes, breaking stories, or trending topics.

    2. **Featured Highlights**  
    - Provide 3-4 crisp bullet points summarizing the most important and impactful featured articles.  
    - Ensure the tone is informative, professional, and engaging.

    3. **Quick Bytes**  
    - Summarize each regular article in a single sentence or short bullet point.  
    - Keep it sharp and to the point, ideal for skimming.

    Ensure the overall tone is professional yet approachable, perfect for an early morning tech newsletter.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating digest: {e}"
