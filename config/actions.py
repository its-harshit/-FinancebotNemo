from typing import Dict, List, Optional
from datetime import datetime
import json
import requests
from nemoguardrails.actions import action
import os

# Mock database for demonstration
grievances_db = []
accounts_db = {
    "ACC001": {"name": "John Doe", "balance": 5000, "status": "active"},
    "ACC002": {"name": "Jane Smith", "balance": 2500, "status": "active"},
    "ACC003": {"name": "Bob Wilson", "balance": 0, "status": "suspended"}
}

@action()
async def llama_guard_api_check(user_message: str) -> Dict:
    """Use Llama Guard via Hugging Face Inference API"""
    
    # Hugging Face Inference API endpoint
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/LlamaGuard-7b"
    
    # Get API key from environment
    hf_token = os.getenv("HUGGINGFACE_API_KEY")
    if not hf_token:
        return {
            "is_safe": True,  # Fail open if no API key
            "assessment": "no_api_key",
            "violated_categories": [],
            "source": "fallback"
        }
    
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    # Llama Guard prompt format
    llama_guard_prompt = f"""<s>[INST] Task: Check if there is unsafe content in 'User' messages in conversations according to our safety policy with the below categories.

<BEGIN UNSAFE CONTENT CATEGORIES>
O1: Violence and Hate.
O2: Sexual content.
O3: Criminal planning.
O4: Guns and illegal weapons.
O5: Regulated or controlled substances.
O6: Self-harm.
O7: Financial crimes and fraud.
<END UNSAFE CONTENT CATEGORIES>

<BEGIN CONVERSATION>
User: {user_message}
<END CONVERSATION>

Provide your safety assessment for User in the above conversation:
- First line must be 'safe' or 'unsafe'
- If unsafe, provide a second line that lists the violated categories. [/INST]"""

    try:
        # Call Hugging Face API
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": llama_guard_prompt,
                "parameters": {
                    "max_new_tokens": 50,
                    "temperature": 0.0,
                    "return_full_text": False
                }
            },
            timeout=15  # 15 second timeout for API
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                llama_response = result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                llama_response = result.get("generated_text", "").strip()
            else:
                llama_response = str(result).strip()
            
            # Parse Llama Guard response
            lines = llama_response.split('\n')
            safety_assessment = lines[0].lower().strip() if lines else "safe"
            is_safe = safety_assessment == "safe"
            
            violated_categories = []
            if not is_safe and len(lines) > 1:
                violated_categories = [cat.strip() for cat in lines[1].split(',')]
            
            return {
                "is_safe": is_safe,
                "assessment": safety_assessment,
                "violated_categories": violated_categories,
                "full_response": llama_response,
                "source": "huggingface_api"
            }
            
        elif response.status_code == 503:
            # Model loading - common with HF API
            return {
                "is_safe": True,  # Fail open
                "assessment": "model_loading",
                "violated_categories": [],
                "full_response": "Model is loading, please try again",
                "source": "fallback"
            }
        else:
            # Other API errors
            return {
                "is_safe": True,  # Fail open
                "assessment": "api_error",
                "violated_categories": [],
                "full_response": f"HTTP {response.status_code}: {response.text}",
                "source": "fallback"
            }
            
    except requests.exceptions.RequestException as e:
        # Network/timeout errors
        return {
            "is_safe": True,  # Fail open for availability
            "assessment": "network_error",
            "violated_categories": [],
            "full_response": str(e),
            "source": "fallback"
        }

@action()
async def llama_guard_with_fallback(user_message: str) -> Dict:
    """Llama Guard with intelligent fallback to existing checks"""
    
    # Try Llama Guard API first
    llama_result = await llama_guard_api_check(user_message)
    
    # If Llama Guard worked, use it
    if llama_result["source"] == "huggingface_api":
        return llama_result
    
    # Fallback to your existing pattern-based checks
    fallback_result = await simple_jailbreak_check(user_message)
    
    return {
        "is_safe": not fallback_result.get("is_jailbreak", False),
        "assessment": "fallback_pattern_check",
        "violated_categories": ["jailbreak"] if fallback_result.get("is_jailbreak") else [],
        "full_response": f"Fallback used: {llama_result['assessment']}",
        "source": "fallback_patterns"
    }

@action()
async def create_grievance(user_id: str, category: str, description: str, priority: str = "medium") -> Dict:
    """Create a new grievance ticket for the user."""
    grievance_id = f"GRV{len(grievances_db) + 1:03d}"
    grievance = {
        "id": grievance_id,
        "user_id": user_id,
        "category": category,
        "description": description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "assigned_to": None
    }
    grievances_db.append(grievance)
    return {
        "success": True,
        "grievance_id": grievance_id,
        "message": f"Grievance created successfully with ID: {grievance_id}"
    }

@action()
async def get_account_info(account_id: str) -> Dict:
    """Retrieve account information for a given account ID."""
    if account_id in accounts_db:
        account = accounts_db[account_id].copy()
        # Mask sensitive information for security
        account["balance"] = "***" if account["balance"] > 0 else "0"
        return {
            "success": True,
            "account": account
        }
    return {
        "success": False,
        "error": "Account not found"
    }

@action()
async def check_compliance(message: str = None, bot_response: str = None) -> Dict:
    """Check if the message complies with financial regulations."""
    # Support both parameter names for backward compatibility
    text_to_check = bot_response or message or ""
    
    compliance_issues = []
    
    # Check for sensitive financial terms
    sensitive_terms = ["credit card", "ssn", "social security", "password", "pin"]
    for term in sensitive_terms:
        if term.lower() in text_to_check.lower():
            compliance_issues.append(f"Contains sensitive term: {term}")
    
    # Check for investment advice (requires disclaimers)
    investment_terms = ["invest", "stock", "bond", "portfolio", "return"]
    has_investment_advice = any(term in text_to_check.lower() for term in investment_terms)
    
    # Generate appropriate disclaimer
    disclaimer = ""
    if has_investment_advice:
        disclaimer = "\n\nDisclaimer: This information is for educational purposes only and should not be considered as financial advice. Please consult with a qualified financial advisor before making investment decisions."
    
    return {
        "is_compliant": len(compliance_issues) == 0,
        "compliant": len(compliance_issues) == 0,  # Keep both for compatibility
        "issues": compliance_issues,
        "requires_disclaimer": has_investment_advice,
        "disclaimer": disclaimer
    }

@action()
async def get_grievance_status(grievance_id: str) -> Dict:
    """Get the status of a specific grievance."""
    for grievance in grievances_db:
        if grievance["id"] == grievance_id:
            return {
                "success": True,
                "grievance": grievance
            }
    return {
        "success": False,
        "error": "Grievance not found"
    }

@action()
async def escalate_grievance(grievance_id: str, reason: str) -> Dict:
    """Escalate a grievance to higher priority."""
    for grievance in grievances_db:
        if grievance["id"] == grievance_id:
            grievance["priority"] = "high"
            grievance["escalation_reason"] = reason
            grievance["escalated_at"] = datetime.now().isoformat()
            return {
                "success": True,
                "message": f"Grievance {grievance_id} escalated successfully"
            }
    return {
        "success": False,
        "error": "Grievance not found"
    }

@action()
async def calculate_response_time(grievance_id: str) -> Dict:
    """Calculate the response time for a grievance."""
    for grievance in grievances_db:
        if grievance["id"] == grievance_id:
            created_time = datetime.fromisoformat(grievance["created_at"])
            current_time = datetime.now()
            response_time = (current_time - created_time).total_seconds() / 3600  # hours
            
            return {
                "success": True,
                "response_time_hours": round(response_time, 2),
                "within_sla": response_time <= 24  # 24-hour SLA
            }
    return {
        "success": False,
        "error": "Grievance not found"
    }

@action()
async def simple_jailbreak_check(user_message: str) -> Dict:
    """Simple pattern-based jailbreak detection."""
    
    # Just a few key patterns to catch obvious attempts
    jailbreak_keywords = [
        "ignore previous instructions",
        "forget your role", 
        "you are no longer",
        "pretend you are",
        "system:",
        "override",
        "new instructions"
    ]
    
    user_lower = user_message.lower()
    detected = any(keyword in user_lower for keyword in jailbreak_keywords)
    
    return {
        "is_jailbreak": detected,
        "message": user_message
    }

@action()
async def classify_user_intent(user_message: str) -> Dict:
    """Classify the user's intent based on their message with off-topic detection."""
    user_message_lower = user_message.lower()
    
    # Off-topic/non-financial keywords (should be redirected)
    off_topic_keywords = [
        "llm", "ai", "artificial intelligence", "machine learning", "chatbot", 
        "weather", "sports", "politics", "entertainment", "personal life", 
        "philosophy", "religion", "what is like to be", "how does it feel",
        "your experience", "your thoughts", "your opinion"
    ]
    
    # Grievance/complaint keywords
    grievance_keywords = ["complaint", "issue", "problem", "grievance", "dispute", "unhappy", "dissatisfied", "frozen", "blocked", "error"]
    
    # Account inquiry keywords  
    account_keywords = ["balance", "account", "statement", "transaction", "deposit", "withdrawal", "transfer"]
    
    # Financial service keywords
    financial_keywords = ["loan", "credit", "mortgage", "investment", "savings", "insurance", "fee", "rate", "bank", "finance", "payment", "card"]
    
    # Banking hours/contact keywords
    contact_keywords = ["hours", "contact", "phone", "call", "reach", "location", "branch", "address"]
    
    # Check for off-topic first (IMPORTANT: This goes first!)
    if any(keyword in user_message_lower for keyword in off_topic_keywords):
        category = "off_topic"
        confidence = 0.95
    elif any(keyword in user_message_lower for keyword in grievance_keywords):
        category = "grievance"
        confidence = 0.9
    elif any(keyword in user_message_lower for keyword in account_keywords):
        category = "account_inquiry"
        confidence = 0.8
    elif any(keyword in user_message_lower for keyword in financial_keywords):
        category = "financial_service"
        confidence = 0.8
    elif any(keyword in user_message_lower for keyword in contact_keywords):
        category = "general_support"
        confidence = 0.8
    else:
        # If no clear category, assume general support but flag for review
        category = "general_support"
        confidence = 0.5  # Lower confidence for unclear messages
    
    return {
        "category": category,
        "confidence": confidence,
        "message": user_message
    }

@action()
async def handle_off_topic_request(user_message: str) -> Dict:
    """Handle off-topic requests by redirecting to financial services."""
    return {
        "response": "I'm FinanceBot, specialized in helping with banking and financial services. I can assist you with account inquiries, grievances, loan information, and other banking needs. How can I help you with your financial services today?",
        "redirect_successful": True
    }

@action()
async def validate_user_input(user_message: str) -> Dict:
    """Validate user input for security and appropriateness."""
    import re
    
    issues = []
    
    # Check for credit card numbers (basic pattern)
    cc_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    if re.search(cc_pattern, user_message):
        issues.append("Contains potential credit card number")
    
    # Check for SSN pattern
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    if re.search(ssn_pattern, user_message):
        issues.append("Contains potential SSN")
    
    # Check for abusive language (basic check)
    abusive_words = ["damn", "hell", "stupid", "idiot", "hate"]
    if any(word in user_message.lower() for word in abusive_words):
        issues.append("Contains inappropriate language")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "message": user_message
    }

@action()
async def check_for_sensitive_info(user_message: str) -> Dict:
    """Check for sensitive information in user message."""
    import re
    
    sensitive_patterns = {
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "phone": r'\b\d{3}-\d{3}-\d{4}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    }
    
    detected_types = []
    for info_type, pattern in sensitive_patterns.items():
        if re.search(pattern, user_message):
            detected_types.append(info_type)
    
    return {
        "contains_sensitive_data": len(detected_types) > 0,
        "detected_types": detected_types,
        "message": user_message
    }

@action()
async def check_response_quality(bot_response: str) -> Dict:
    """Check the quality of bot response."""
    issues = []
    
    # Check minimum length
    if len(bot_response) < 10:
        issues.append("Response too short")
    
    # Check for professional tone indicators
    professional_indicators = ["please", "thank you", "apologize", "understand", "assist", "help"]
    if not any(indicator in bot_response.lower() for indicator in professional_indicators):
        issues.append("May lack professional tone")
    
    # Check for complete sentences
    if not bot_response.strip().endswith(('.', '!', '?')):
        issues.append("Response may be incomplete")
    
    return {
        "meets_standards": len(issues) == 0,
        "issues": issues,
        "response": bot_response
    }

@action()
async def improve_response_quality(original_response: str, quality_issues: List[str]) -> Dict:
    """Improve response quality based on identified issues."""
    improved_response = original_response
    
    # Add professional closing if missing
    if "May lack professional tone" in quality_issues:
        improved_response += " Please let me know if you need any additional assistance."
    
    # Ensure proper punctuation
    if "Response may be incomplete" in quality_issues:
        if not improved_response.strip().endswith(('.', '!', '?')):
            improved_response += "."
    
    return {
        "content": improved_response,
        "improvements_made": quality_issues
    }

@action()
async def format_bot_response(response: str, user_context: Optional[Dict] = None) -> Dict:
    """Format bot response for consistency and professionalism."""
    # Ensure proper capitalization
    formatted_response = response.strip()
    if formatted_response and not formatted_response[0].isupper():
        formatted_response = formatted_response[0].upper() + formatted_response[1:]
    
    # Handle user_context safely - it might be a string or None from Colang
    context_dict = {}
    if user_context and isinstance(user_context, dict):
        context_dict = user_context
    
    # Add professional greeting if this is the start of conversation
    if context_dict.get("is_first_message", False):
        formatted_response = f"Hello! {formatted_response}"
    
    return {
        "content": formatted_response
    }

@action()
async def process_general_inquiry(user_message: str, user_context: Optional[Dict] = None) -> Dict:
    """Process general customer support inquiries."""
    response_templates = {
        "hours": "Our customer service is available Monday through Friday, 9 AM to 6 PM EST. For urgent matters outside these hours, please visit our website or use our mobile app.",
        "fees": "For detailed information about fees and charges, please refer to your account agreement or contact us directly. Fee structures vary by account type and services used.",
        "contact": "You can reach us by phone at 1-800-FINANCE, through our website chat, or by visiting any of our branch locations. Our customer service team is ready to assist you.",
        "default": "Thank you for your inquiry. I'm here to help with your banking needs. Could you please provide more specific details about what you'd like to know?"
    }
    
    user_message_lower = user_message.lower()
    
    if any(word in user_message_lower for word in ["hours", "time", "when", "open"]):
        response = response_templates["hours"]
    elif any(word in user_message_lower for word in ["fee", "charge", "cost", "price"]):
        response = response_templates["fees"]
    elif any(word in user_message_lower for word in ["contact", "phone", "call", "reach"]):
        response = response_templates["contact"]
    else:
        response = response_templates["default"]
    
    return {
        "message": response,
        "category": "general_inquiry"
    }