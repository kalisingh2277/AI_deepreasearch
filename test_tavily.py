from tavily import TavilyClient
import os
from dotenv import load_dotenv

def test_tavily_api():
    # Load environment variables
    load_dotenv()
    
    # Get Tavily API key
    tavily_api_key = os.getenv('TAVILY_API_KEY')
    
    print(f"\nTesting Tavily API key: {tavily_api_key[:8]}...")  # Only show first 8 characters for security
    
    try:
        # Initialize Tavily client
        client = TavilyClient(api_key=tavily_api_key)
        
        # Make a simple test query
        result = client.search(
            query="What is Tavily?",
            search_depth=1,
            max_results=2
        )
        
        # Check if we got results
        if result and 'results' in result:
            print("\n✅ Tavily API key is valid and working!")
            print(f"\nFound {len(result['results'])} results")
            print("\nSample result:")
            if result['results']:
                print(f"Title: {result['results'][0].get('title', 'No title')}")
                print(f"URL: {result['results'][0].get('url', 'No URL')}")
        else:
            print("\n❌ API response format is unexpected")
            print("Response:", result)
            
    except Exception as e:
        print("\n❌ Error testing Tavily API key:")
        print(str(e))
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. Network connectivity problems")
        print("3. API rate limit exceeded")
        print("\nPlease verify your API key at: https://tavily.com/dashboard")

if __name__ == "__main__":
    test_tavily_api() 