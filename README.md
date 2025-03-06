# Deep Research AI System

A powerful dual-agent system for conducting deep web research and synthesizing information using AI. The system consists of a Research Agent that crawls and collects data using Tavily, and an Answer Drafting Agent that synthesizes the information using LangChain and LangGraph.

## Features

- Web crawling and data collection using Tavily
- Information synthesis using LangChain
- Knowledge graph generation with LangGraph
- Flexible storage options (Firebase or local)
- Modern, responsive web interface
- Real-time research progress updates
- Interactive knowledge graph visualization

## Prerequisites

Before you begin, you'll need:

1. **Python 3.8+**
2. **API Keys:**
   - **Tavily API Key:** Get it from [Tavily Dashboard](https://tavily.com/dashboard)
   - **OpenAI API Key:** Get it from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Firebase credentials** (optional, only if using Firebase storage)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd deep-research-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:

   a. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   b. Edit the `.env` file and add your API keys:
   ```env
   TAVILY_API_KEY=your_tavily_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   c. (Optional) Configure additional settings in `.env`:
   ```env
   # Server Configuration
   PORT=5000
   HOST=0.0.0.0

   # Research Agent Configuration
   MAX_RESEARCH_DEPTH=3
   MAX_URLS_PER_SEARCH=5
   CACHE_EXPIRY_MINUTES=60

   # Storage Configuration
   STORAGE_TYPE=local  # Options: firebase, local
   LOCAL_STORAGE_PATH=data
   ```

   d. (Optional) If using Firebase:
   - Add your Firebase credentials JSON file
   - Set the path in `.env`:
   ```env
   FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-credentials.json
   ```

## Usage

1. Start the server:
```bash
python app.py
```

2. The web interface will automatically open in your default browser at:
   - http://localhost:5000

3. Enter your research query and select a search depth (1-5)
   - Higher depth means more thorough research but takes longer
   - The system will display a loading indicator while researching

4. View the results:
   - Research synthesis
   - Interactive knowledge graph
   - Source documents with relevance scores

## Project Structure

```
/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create from .env.example)
├── src/
│   ├── agents/
│   │   ├── research_agent.py    # Tavily-based research agent
│   │   └── answer_agent.py      # LangChain-based answer agent
│   ├── config/
│   │   └── config.py           # Configuration settings
│   └── utils/
│       ├── storage.py          # Storage management
│       └── error_handler.py    # Error handling utilities
├── static/
│   ├── style.css              # Web interface styles
│   └── script.js              # Frontend JavaScript
└── templates/
    └── index.html            # Main HTML template
```

## API Keys and Security

1. **Never commit your API keys to version control**
   - The `.env` file is listed in `.gitignore`
   - Always use environment variables for sensitive data

2. **API Key Requirements:**
   - Tavily API Key: Must start with 'tvly-'
   - OpenAI API Key: Required for content synthesis
   - Both keys are validated on startup

3. **Storage Options:**
   - Local storage (default): No additional setup required
   - Firebase: Requires valid credentials JSON file

## Troubleshooting

1. **API Key Issues:**
   - Check that your API keys are correctly set in `.env`
   - Verify API key format (Tavily key should start with 'tvly-')
   - Check API key validity in respective dashboards

2. **Server Issues:**
   - Ensure port 5000 is available
   - Check logs for detailed error messages
   - Verify Python version compatibility

3. **Research Issues:**
   - Verify internet connectivity
   - Check API rate limits
   - Try reducing search depth if requests time out

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Tavily](https://tavily.com/) for the research API
- [LangChain](https://langchain.com/) for the language processing framework
- [D3.js](https://d3js.org/) for knowledge graph visualization 