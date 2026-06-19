# Research Assistant - Setup & Run Guide

This guide allows you to set up, run, and test the multi-agent research assistant in under 10 minutes.

### 1. Requirements
- Python 3.10+ (macOS/Linux recommended)
- A Google Gemini API Key (`GOOGLE_API_KEY`)
- A Tavily Search API Key (`TAVILY_API_KEY`)

### 2. Environment Setup
Create a virtual environment and install dependencies.

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Configuration
Copy the example environment file and add your API keys.

```bash
cp .env.example .env
```
Open `.env` in your text editor and populate the keys:
```env
GOOGLE_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here
LLM_MODEL=gemini-2.5-flash
```

### 4. Running the Server
You can start the server manually using Uvicorn, or run the included shell script.

**Option A:**
```bash
uvicorn app.main:app --reload
```

**Option B:**
```bash
bash run.sh
```

Once running, navigate to [http://localhost:8000](http://localhost:8000) in your web browser to use the chat UI.

### 5. Running Tests
To verify graph routing correctness and boundary cases, run the test suite:

```bash
# Make sure your virtual environment is active!
pytest
```
