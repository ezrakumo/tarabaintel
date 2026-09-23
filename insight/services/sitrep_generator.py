import os
from openai import OpenAI
from django.utils import timezone
from datetime import timedelta
from insight.models import Report, FieldVerification, IntelligenceSummary

# Initialize OpenAI Client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_daily_sitrep():
    """Fetches last 24h data and generates an AI SITREP."""
    print("🧠 Starting AI SITREP Generation...")
    
    # 1. Gather Intelligence Data (Last 24 Hours)
    yesterday = timezone.now() - timedelta(hours=24)
    
    recent_reports = Report.objects.filter(submitted_at__gte=yesterday).values('issue_category', 'ai_urgency_level', 'description', 'lga__name')
    recent_verifications = FieldVerification.objects.filter(assigned_at__gte=yesterday).values('status', 'is_valid', 'assigned_agent__name')
    
    # 2. Format Data for the AI
    raw_data = {
        "total_reports": len(recent_reports),
        "reports": list(recent_reports),
        "verifications": list(recent_verifications)
    }

    # 3. The Intelligence Prompt
    prompt = f"""
    Act as a Senior National Security Intelligence Analyst for Taraba State, Nigeria. 
    Based on the following raw intelligence data from the last 24 hours, generate a concise, professional Situation Report (SITREP).
    
    RAW DATA: {raw_data}
    
    FORMAT THE OUTPUT EXACTLY LIKE THIS:
    **SITREP DATE:** [Today's Date]
    **THREAT LEVEL:** [LOW/MODERATE/HIGH/CRITICAL]
    
    **1. EXECUTIVE SUMMARY:** (2-3 sentences summarizing the security landscape)
    **2. KEY THREATS:** (Bullet points of the most critical incidents)
    **3. FIELD OPERATIONS:** (Status of agent verifications)
    **4. STRATEGIC RECOMMENDATIONS:** (Actionable advice for security forces based on the data)
    """

    # 4. Call the AI Brain
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a top-tier military intelligence analyst."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        ai_summary = response.choices[0].message.content
        print("✅ AI SITREP Generated Successfully!")
        
        # 5. Save to Database
        summary = IntelligenceSummary.objects.create(
            title=f"Daily SITREP - {timezone.now().strftime('%Y-%m-%d')}",
            content=ai_summary, # Make sure your model has a 'content' or 'summary' text field!
            generated_at=timezone.now(),
            statistics=raw_data
        )
        return summary
        
    except Exception as e:
        print(f"❌ AI Generation Failed: {e}")
        return None