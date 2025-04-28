import os
from datetime import datetime
import openai

# Set your OpenAI API key in environment variables for security
# os.environ["OPENAI_API_KEY"] = "your-api-key"

def summarize_with_openai(text):
    """
    Summarize the given text using OpenAI's API
    """
    try:
        client = openai.OpenAI()
        
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes news articles. For each news there should be one line"},
                {"role": "user", "content": f"Please summarize the following news article in a concise paragraph:\n\n{text}"}
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in summarization: {e}")
        return None

def main():
    print("Starting summarization process...")
    
    # Check if input file exists
    input_file = "document_1.txt"
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found.")
        return
    
    try:
        # Load scraped article text
        with open(input_file, 'r', encoding='utf-8') as f:
            article_text = f.read()
        
        print(f"Loaded article text ({len(article_text)} characters) for summarization.")
        
        # Summarize the article text
        summary = summarize_with_openai(article_text)
        
        if not summary:
            print("Failed to generate summary.")
            return None
            
        print("Successfully generated summary.")
        
        # Save summary to a text file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"summary.txt"
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            # f.write(f"NEWS SUMMARY - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"\n{summary}\n\n")
            # f.write("\nOriginal Article Text:\n")
            # f.write("-" * 80 + "\n")
            
            # Include a snippet of the original text (first 500 chars)
            # snippet = article_text[:500]
            # if len(article_text) > 500:
            #     snippet += "...[text truncated]"
            # f.write(snippet)
        
        print(f"Summarization complete! Saved to {output_filename}")
        return output_filename
    
    except Exception as e:
        print(f"Error during summarization process: {e}")
        return None

if __name__ == "__main__":
    main()