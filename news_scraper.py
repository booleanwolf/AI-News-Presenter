import requests
from bs4 import BeautifulSoup

import time
import os
from dotenv import load_dotenv
from openai import OpenAI
import openai 
client = OpenAI()
# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def fetch_article_content(url):
    """Fetch article content from a URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.find('title').text if soup.find('title') else "No title found"
        
        # Extract article content (this needs to be customized for different sites)
        paragraphs = soup.find_all('p')
        content = ' '.join([p.text for p in paragraphs])
        
        return {'title': title, 'content': content}
    
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def summarize_with_openai(content, max_tokens=500):
    """Summarize content using OpenAI API."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news articles concisely and accurately."},
                {"role": "user", "content": f"Summarize the following news article in a comprehensive way. Focus on key facts, quotes, and implications:\n\n{content}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error summarizing content: {e}")
        return None

def get_latest_news():
    """Get latest news from popular sites."""
    news_sites = [
        "https://www.prothomalo.com/",
        "https://www.thedailystar.net/",
    ]
    
    articles = []
    
    for site in news_sites:
        try:
            print(f"Fetching headlines from {site}...")
            response = requests.get(site)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links (this needs customization for each site)
            links = soup.find_all('a', href=True)
            
            # Filter for article links (basic approach)
            article_links = []
            for link in links:
                href = link['href']
                # Check if it's a full URL or relative path
                if not href.startswith('http'):
                    # Convert relative to absolute URL
                    base_url = site.split('/')[0] + '//' + site.split('/')[2]
                    href = base_url + ('' if href.startswith('/') else '/') + href
                
                # Basic filtering for article links (customize as needed)
                if any(term in href for term in ['/article/', '/news/', '/world/', '/story/']):
                    if href not in article_links:
                        article_links.append(href)
            
            # Process only the first 2 articles from each site for demo purposes
            for i, article_url in enumerate(article_links[:2]):
                print(f"Processing article {i+1}: {article_url}")
                article_data = fetch_article_content(article_url)
                
                if article_data and len(article_data['content']) > 100:  # Ensure we have substantial content
                    summary = summarize_with_openai(article_data['content'])
                    if summary:
                        articles.append({
                            'url': article_url,
                            'title': article_data['title'],
                            'summary': summary
                        })
        
        except Exception as e:
            print(f"Error processing site {site}: {e}")
    
    return articles

def save_document(articles, filename="document_1.txt"):
    """Save summarized articles to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# NEWS SUMMARIES\n\n")
        f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, article in enumerate(articles, 1):
            f.write(f"## {i}. {article['title']}\n")
            f.write(f"Source: {article['url']}\n\n")
            f.write(f"{article['summary']}\n\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"Saved {len(articles)} article summaries to {filename}")
    return filename

def main():
    print("Starting news collection and summarization...")
    articles = get_latest_news()
    
    if articles:
        document_file = save_document(articles)
        print(f"Process complete. Created {document_file} with {len(articles)} article summaries.")
    else:
        print("No articles were successfully processed.")

if __name__ == "__main__":
    main()