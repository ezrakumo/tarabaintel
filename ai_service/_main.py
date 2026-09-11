import os
import re
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq

# Load environment variables
load_dotenv()

app = FastAPI(title="TarabaInsight AI Analytics Microservice v2.0 (Groq)")

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ReportAnalysisRequest(BaseModel):
    report_id: str
    description: str
    issue_category: str = ""
    location_desc: str = ""

class ReportAnalysisResponse(BaseModel):
    report_id: str
    ai_suggested_category: str
    ai_confidence_score: float
    keywords_found: list[str]
    sentiment: str
    urgency_level: str
    duplicate_check: str
    extracted_entities: dict

def analyze_with_groq(description: str, user_category: str) -> dict:
    prompt = f"""
    You are an AI analyst for Taraba State's community intelligence platform.
    Analyze the following citizen report and provide structured insights.
    
    Report Description: "{description}"
    User-Selected Category: {user_category if user_category else "Not specified"}
    
    Provide your analysis in STRICT JSON format. Do not include any conversational text, 
    markdown formatting, or explanations. Output ONLY the JSON object.
    
    JSON Structure:
    {{
        "suggested_category": "One of [WATER, HEALTH, AGRIC, SECURITY, INFRA, EDUCATION, OTHER]",
        "confidence_score": 0.95,
        "keywords": ["keyword1", "keyword2"],
        "sentiment": "One of [POSITIVE, NEUTRAL, NEGATIVE, URGENT]",
        "urgency_level": "One of [LOW, MEDIUM, HIGH, CRITICAL]",
        "duplicate_likelihood": "One of [LOW, MEDIUM, HIGH]",
        "extracted_entities": {{
            "locations": ["Location1"],
            "organizations": ["Org1"],
            "dates": ["Date1"]
        }}
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": "You are a professional intelligence analyst. Output ONLY valid JSON. No markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        
        ai_response_text = response.choices[0].message.content.strip()
        
        # BULLETPROOF JSON EXTRACTION
        json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            analysis = json.loads(clean_json)
        else:
            raise ValueError("No JSON object found in AI response")
        
        return {
            "suggested_category": analysis.get("suggested_category", "UNKNOWN"),
            "confidence": float(analysis.get("confidence_score", 0.5)),
            "keywords": analysis.get("keywords", []),
            "sentiment": analysis.get("sentiment", "NEUTRAL"),
            "urgency": analysis.get("urgency_level", "MEDIUM"),
            "duplicate": analysis.get("duplicate_likelihood", "LOW"),
            "entities": analysis.get("extracted_entities", {})
        }
        
    except Exception as e:
        print(f"Groq API error: {e}")
        return simple_keyword_fallback(description)

def simple_keyword_fallback(description: str) -> dict:
    text = description.lower()
    categories = {
        "WATER": ["water", "pump", "borehole", "well", "flood"],
        "HEALTH": ["hospital", "clinic", "doctor", "medicine", "sick"],
        "AGRIC": ["farm", "crop", "cattle", "herder", "harvest"],
        "SECURITY": ["attack", "thief", "police", "danger", "violence"],
        "INFRA": ["road", "bridge", "electricity", "power", "school"]
    }
    
    best_category = "UNKNOWN"
    max_score = 0
    found_keywords = []
    
    for category, keywords in categories.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > max_score:
            max_score = score
            best_category = category
            found_keywords = [kw for kw in keywords if kw in text]
    
    return {
        "suggested_category": best_category,
        "confidence": min(max_score / 3.0, 1.0),
        "keywords": found_keywords,
        "sentiment": "NEUTRAL",
        "urgency": "MEDIUM",
        "duplicate": "LOW",
        "entities": {}
    }

@app.post("/analyze", response_model=ReportAnalysisResponse)
async def analyze_report(request: ReportAnalysisRequest):
    try:
        analysis = analyze_with_groq(request.description, request.issue_category)
        return ReportAnalysisResponse(
            report_id=request.report_id,
            ai_suggested_category=analysis["suggested_category"],
            ai_confidence_score=analysis["confidence"],
            keywords_found=analysis["keywords"],
            sentiment=analysis["sentiment"],
            urgency_level=analysis["urgency"],
            duplicate_check=analysis["duplicate"],
            extracted_entities=analysis["entities"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "TarabaInsight AI Microservice v2.0 (Groq-Powered)",
        "status": "operational",
        "model": "qwen/qwen3.8-27b"
    }