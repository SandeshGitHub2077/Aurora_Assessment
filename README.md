# Member Question-Answering System

A simple question-answering system that can answer natural-language questions about member data provided by a public API.

## Features

- **Natural Language QA**: Answer questions about member messages using HuggingFace's question-answering models
- **RESTful API**: Simple `/ask` endpoint that accepts questions and returns answers
- **Smart Context Building**: Automatically filters relevant messages based on question keywords
- **Fallback Mechanisms**: Handles API failures gracefully with simple keyword-based extraction

## API Endpoints

### `POST /ask`

Ask a natural-language question about member data.

**Request:**
```json
{
  "question": "When is Layla planning her trip to London?"
}
```

**Response:**
```json
{
  "answer": "Based on the messages, Layla is planning her trip to London around 2025-04-10."
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Installation

### Prerequisites

- Python 3.8+
- Anaconda (for environment management)

### Setup

1. Create and activate the conda environment:
```bash
conda create -n qa-system python=3.10
conda activate qa-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env and add your HuggingFace API key if different
```

4. Run the application:
```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8001` (or port 8000 if available)

## Usage Examples

### Using curl

```bash
curl -X POST "http://localhost:8001/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "When is Layla planning her trip to London?"}'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8001/ask",
    json={"question": "How many cars does Vikram Desai have?"}
)
print(response.json())
```

## Design Notes

### Alternative Approaches Considered

#### 1. **Fine-tuned Domain-Specific Model**
   - **Approach**: Fine-tune a QA model (e.g., BERT, RoBERTa) on the specific member message dataset
   - **Pros**: Better accuracy for domain-specific questions, can learn member-specific patterns
   - **Cons**: Requires training data preparation, longer development time, needs retraining when data updates
   - **Why not chosen**: Time constraints and the need for a quick, deployable solution

#### 2. **Vector Database with Semantic Search (RAG)**
   - **Approach**: Use embeddings (e.g., sentence-transformers) to create vector representations of messages, store in a vector DB (e.g., Pinecone, Weaviate), and retrieve relevant context using semantic search
   - **Pros**: More accurate context retrieval, handles synonyms and related concepts better, scalable
   - **Cons**: Requires additional infrastructure, more complex setup, higher latency
   - **Why not chosen**: Simplicity and speed of deployment were priorities; current keyword-based filtering is sufficient for MVP

#### 3. **Named Entity Recognition (NER) + Rule-Based System**
   - **Approach**: Extract entities (names, dates, locations, etc.) using NER, build a knowledge graph, and answer questions using rule-based logic
   - **Pros**: Very precise for structured queries, interpretable, no API dependencies
   - **Cons**: Limited to predefined question types, brittle for natural language variations, requires extensive rule engineering
   - **Why not chosen**: Too rigid for natural language questions; QA models handle variations better

#### 4. **LLM-based Approach (GPT, Claude, etc.)**
   - **Approach**: Use large language models via OpenAI/Anthropic APIs to answer questions directly
   - **Pros**: Best natural language understanding, handles complex questions, few-shot learning
   - **Cons**: Higher cost, API rate limits, potential data privacy concerns, dependency on external services
   - **Why not chosen**: Cost considerations and preference for open-source solutions; HuggingFace provides good balance

#### 5. **Hybrid Approach (Current Implementation)**
   - **Approach**: Keyword-based context filtering + HuggingFace QA model
   - **Pros**: Good balance of accuracy and simplicity, cost-effective, fast to implement, handles API failures gracefully
   - **Cons**: Keyword filtering may miss semantically similar but lexically different terms
   - **Why chosen**: Best trade-off between development speed, accuracy, and maintainability for the MVP

### Future Improvements

1. **Semantic Search**: Replace keyword filtering with embedding-based semantic search
2. **Caching**: Cache frequently asked questions and their answers
3. **Multi-turn Conversations**: Support follow-up questions with conversation context
4. **Answer Confidence Scores**: Return confidence levels for answers
5. **Structured Data Extraction**: Pre-process messages to extract structured facts (triples) for faster querying

## Data Insights

### Anomalies and Inconsistencies Found

After analyzing the dataset (3,349 messages), the following findings were identified:

#### ✅ **Data Quality Strengths**
- All message IDs are unique
- All required fields (id, user_id, user_name, timestamp, message) are present
- Timestamps are valid and properly formatted
- User ID to user name mappings are consistent
- No suspicious test/placeholder messages detected
- No duplicate message content detected

#### ⚠️ **Potential Issues**

1. **Future Timestamps**: Some messages have timestamps in the future (beyond 2026), which may indicate:
   - Test data with placeholder dates
   - System clock issues during data generation
   - Intentional future-dated messages (e.g., scheduled requests)

2. **User Activity Distribution**: 
   - Significant variation in message counts per user
   - Some users have unusually high activity (3x+ above average)
   - This is likely normal behavior but worth monitoring for data quality

3. **Message Content Patterns**:
   - Messages are primarily in English
   - Mix of request types: bookings, preferences, updates, feedback
   - Some messages contain personal information (phone numbers, addresses) that should be handled with care

### Recommendations

1. **Data Validation**: Implement validation rules for timestamps to flag future dates
2. **Privacy**: Consider anonymizing or redacting sensitive information (phone numbers, addresses) in logs
3. **Monitoring**: Set up alerts for unusual patterns (e.g., sudden spike in messages from one user)
4. **Data Freshness**: Implement a mechanism to refresh the message cache periodically

## Deployment

### Docker Deployment

A `Dockerfile` is provided for containerized deployment:

```bash
docker build -t qa-system .
docker run -p 8000:8000 -e HF_API_KEY=your_key qa-system
```

### Cloud Deployment Options

1. **Heroku**: Use the provided `Procfile`
2. **AWS Lambda**: Use serverless framework with API Gateway
3. **Google Cloud Run**: Deploy container directly
4. **Railway/Render**: Simple container deployment

### Environment Variables

- `HF_API_KEY`: HuggingFace API key (defaults to provided key if not set)
- `MESSAGES_API_URL`: Override the messages API URL (optional)

## Testing

Run the data analysis script to check for anomalies:

```bash
python analyze_data.py
```

Test the API:

```bash
# Health check
curl http://localhost:8001/health

# Ask a question
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are Amira'\''s favorite restaurants?"}'
```

Or use the test script:
```bash
python test_qa.py
```

## Project Structure

```
.
├── app.py                 # Main FastAPI application
├── analyze_data.py        # Data analysis script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env.example          # Environment variables template
└── README.md             # This file
```

## License

This project is provided as-is for evaluation purposes.

