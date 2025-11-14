"""
Question-Answering System for Member Data
"""
import os
import sys
import requests
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

load_dotenv()

app = FastAPI(title="Member QA System", version="1.0.0")

# Configuration
MESSAGES_API_URL = "https://november7-730026606190.europe-west1.run.app/messages"
HF_API_KEY = os.getenv("HF_API_KEY")
# Note: HF_API_KEY will be checked when needed, not at import time for Vercel compatibility
# This allows the app to import even if the key is not set (will fail gracefully later)

# Initialize QA pipeline if transformers is available
qa_pipeline = None
if TRANSFORMERS_AVAILABLE:
    try:
        qa_pipeline = pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2",
            tokenizer="deepset/roberta-base-squad2"
        )
    except Exception as e:
        print(f"Warning: Could not load QA pipeline: {e}")
        qa_pipeline = None

# Cache for messages data
_messages_cache = None


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


def fetch_all_messages():
    """Fetch all messages from the API."""
    global _messages_cache
    
    if _messages_cache is not None:
        return _messages_cache
    
    try:
        response = requests.get(MESSAGES_API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        _messages_cache = data.get("items", [])
        return _messages_cache
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


def build_context_for_question(question: str, messages: list, max_context_length: int = 5000) -> str:
    """
    Build a context string from messages that are relevant to the question.
    Uses simple keyword matching to filter relevant messages.
    """
    question_lower = question.lower()
    question_words = set(question_lower.split())
    
    # Extract potential entity names (capitalized words)
    potential_names = [word for word in question.split() if word[0].isupper()]
    
    relevant_messages = []
    
    for msg in messages:
        msg_text = msg.get("message", "").lower()
        user_name = msg.get("user_name", "").lower()
        
        # Check if message is relevant
        is_relevant = False
        
        # Check for name matches
        for name in potential_names:
            if name.lower() in user_name:
                is_relevant = True
                break
        
        # Check for keyword matches
        if not is_relevant:
            msg_words = set(msg_text.split())
            if question_words.intersection(msg_words):
                is_relevant = True
        
        if is_relevant:
            relevant_messages.append(msg)
    
    # If no relevant messages found, use all messages (fallback)
    if not relevant_messages:
        relevant_messages = messages
    
    # Build context string
    context_parts = []
    current_length = 0
    
    for msg in relevant_messages[:100]:  # Limit to top 100 relevant messages
        msg_str = f"{msg.get('user_name', 'Unknown')}: {msg.get('message', '')} (Date: {msg.get('timestamp', '')[:10]})\n"
        if current_length + len(msg_str) > max_context_length:
            break
        context_parts.append(msg_str)
        current_length += len(msg_str)
    
    return "\n".join(context_parts)


def answer_question_with_hf(question: str, context: str) -> str:
    """Use HuggingFace to answer the question based on context."""
    # Check API key
    if not HF_API_KEY:
        return answer_question_simple(question, context)
    
    # Try using local transformers pipeline first (faster, no API calls)
    if qa_pipeline is not None:
        try:
            result = qa_pipeline(question=question, context=context)
            answer = result.get("answer", "")
            score = result.get("score", 0)
            
            if answer and score > 0.1:
                return answer
            elif answer:
                return f"I found some information, but the confidence is low: {answer}"
        except Exception as e:
            print(f"Pipeline error: {e}, falling back to API")
    
    # Use HuggingFace Inference API
    try:
        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Try multiple API endpoint formats
        api_urls = [
            "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2",
            f"https://api-inference.huggingface.co/pipeline/question-answering/deepset/roberta-base-squad2"
        ]
        
        for api_url in api_urls:
            try:
                # Try direct format first
                payload = {
                    "question": question,
                    "context": context
                }
                
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict):
                        if "answer" in result:
                            answer = result["answer"]
                            score = result.get("score", 1.0)
                            if answer and len(answer.strip()) > 0:
                                if score > 0.05:  # Lower threshold
                                    return answer
                                else:
                                    # Low confidence but return anyway
                                    return answer
                        elif "error" not in result:
                            # Try to extract answer from response
                            if "text" in result:
                                return result["text"]
                elif response.status_code == 503:
                    # Model is loading, will fall back to simple method
                    print("HF model is loading, using fallback", file=sys.stderr)
                
                # Try with inputs wrapper
                payload = {
                    "inputs": {
                        "question": question,
                        "context": context
                    }
                }
                
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict) and "answer" in result:
                        return result["answer"]
                    elif isinstance(result, list) and len(result) > 0:
                        if isinstance(result[0], dict) and "answer" in result[0]:
                            return result[0]["answer"]
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"API error: {e}")
    
    # Final fallback to simple method
    return answer_question_simple(question, context)


def answer_question_simple(question: str, context: str) -> str:
    """Simple fallback answer extraction using keyword matching."""
    question_lower = question.lower()
    lines = context.split("\n")
    
    # Extract member name from question
    question_words = question.split()
    member_name = None
    for word in question_words:
        if word[0].isupper() and len(word) > 2:
            # Check if it's a name (not a location)
            if word.lower() not in ["london", "paris", "tokyo", "dubai", "milan", "monaco", "new", "york", "san", "francisco", "when", "what", "where", "how", "who"]:
                member_name = word
                break
    
    # Find relevant lines
    relevant_lines = []
    for line in lines:
        if not line.strip():
            continue
        line_lower = line.lower()
        # Check if line mentions the member
        if member_name and member_name.lower() in line_lower:
            relevant_lines.append(line)
        # Check for keyword matches
        elif any(word in line_lower for word in question_lower.split() if len(word) > 3):
            relevant_lines.append(line)
    
    # If no specific matches, use all lines
    if not relevant_lines:
        relevant_lines = lines[:10]
    
    # Extract answer based on question type
    if "when" in question_lower or "date" in question_lower or "time" in question_lower:
        # Look for dates and temporal references
        for line in relevant_lines:
            if "Date:" in line:
                date_part = line.split("Date:")[-1].strip()[:10]
                # Extract the message content
                if ":" in line:
                    message_part = line.split(":", 1)[1].split("(Date:")[0].strip()
                    if message_part:
                        return f"Based on the messages, {message_part} (around {date_part})."
        
        # Look for temporal words
        temporal_words = ["today", "tomorrow", "next week", "this friday", "next month", "friday", "saturday", "sunday", "monday", "tuesday", "wednesday", "thursday"]
        for line in relevant_lines:
            line_lower = line.lower()
            for temp_word in temporal_words:
                if temp_word in line_lower:
                    if ":" in line:
                        message_part = line.split(":", 1)[1].strip()
                        if "(Date:" in message_part:
                            message_part = message_part.split("(Date:")[0].strip()
                        if message_part:
                            return f"Based on the messages: {message_part}"
    
    if "how many" in question_lower:
        # Try to extract numbers
        for line in relevant_lines:
            words = line.split()
            for i, word in enumerate(words):
                if word.isdigit() and int(word) > 0:
                    # Get context around the number
                    context_start = max(0, i-3)
                    context_end = min(len(words), i+4)
                    context_words = " ".join(words[context_start:context_end])
                    return f"Based on the messages: {context_words}"
    
    if "what" in question_lower or "which" in question_lower or "where" in question_lower:
        # Extract the most relevant message
        for line in relevant_lines:
            if ":" in line:
                message_part = line.split(":", 1)[1].strip()
                if message_part and len(message_part) > 10:
                    # Remove date part if present
                    if "(Date:" in message_part:
                        message_part = message_part.split("(Date:")[0].strip()
                    if message_part:
                        return f"Based on the messages: {message_part}"
    
    if "who" in question_lower:
        # Extract names mentioned
        for line in relevant_lines:
            if ":" in line:
                name_part = line.split(":")[0].strip()
                message_part = line.split(":", 1)[1].strip()
                if "(Date:" in message_part:
                    message_part = message_part.split("(Date:")[0].strip()
                if message_part:
                    return f"Based on the messages: {name_part} - {message_part}"
    
    # Return the most relevant line
    if relevant_lines:
        best_line = relevant_lines[0]
        if ":" in best_line:
            message_part = best_line.split(":", 1)[1].strip()
            if "(Date:" in message_part:
                message_part = message_part.split("(Date:")[0].strip()
            if message_part:
                return f"Based on the messages: {message_part}"
    
    # Final fallback
    return "I found relevant information in the messages, but couldn't extract a specific answer. Please check the member messages for details."


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Member QA System",
        "version": "1.0.0",
        "endpoints": {
            "/ask": "POST - Ask a question about member data",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Answer a natural-language question about member data.
    
    Example questions:
    - "When is Layla planning her trip to London?"
    - "How many cars does Vikram Desai have?"
    - "What are Amira's favorite restaurants?"
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        # Fetch messages
        messages = fetch_all_messages()
        
        if not messages:
            return AnswerResponse(answer="No member messages are currently available.")
        
        # Build context
        context = build_context_for_question(request.question, messages)
        
        if not context:
            return AnswerResponse(answer="I couldn't find any relevant information to answer your question.")
        
        # Get answer using HuggingFace API
        answer = answer_question_with_hf(request.question, context)
        
        return AnswerResponse(answer=answer)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

