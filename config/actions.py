from typing import Dict, List, Optional
from datetime import datetime
import json
import requests
from nemoguardrails.actions import action
import os

# Mock database for demonstration
grievances_db = []

# NPCI Service Information Database
npci_services_db = {
    "UPI": {
        "description": "Unified Payments Interface - Instant payment system",
        "common_issues": ["failed_transaction", "money_debited_but_payment_failed", "upi_id_issues", "transaction_limit_exceeded"]
    },
    "RuPay": {
        "description": "India's domestic payment network for cards",
        "common_issues": ["card_not_working", "transaction_declined", "international_usage", "reward_points"]
    },
    "NACH": {
        "description": "National Automated Clearing House for bulk payments",
        "common_issues": ["mandate_failure", "payment_bounce", "mandate_cancellation", "auto_debit_issues"]
    },
    "IMPS": {
        "description": "Immediate Payment Service for instant money transfer",
        "common_issues": ["transfer_failed", "beneficiary_not_added", "transaction_limit", "service_unavailable"]
    },
    "NETC": {
        "description": "National Electronic Toll Collection (FASTag)",
        "common_issues": ["fastag_not_working", "double_deduction", "balance_issues", "blacklist_issues"]
    },
    "BBPS": {
        "description": "Bharat Bill Payment System",
        "common_issues": ["bill_payment_failed", "duplicate_payment", "biller_not_available", "receipt_issues"]
    }
}

# NPCI Mandate Types
mandate_types = {
    "e_NACH": "Electronic National Automated Clearing House",
    "UPI_AutoPay": "UPI Recurring Payments",
    "SI": "Standing Instructions"
}

# Legacy accounts database - not used for NPCI services
accounts_db = {}

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
async def create_grievance(user_id: str, category: str, description: str, priority: str = "medium", service_type: str = "general") -> Dict:
    """Create a new NPCI grievance ticket for the user."""
    grievance_id = f"NPCI{len(grievances_db) + 1:06d}"
    
    # NPCI-specific grievance categories
    valid_categories = [
        "upi_transaction_failure", "upi_money_debited", "upi_id_issues", "upi_limit_exceeded",
        "rupay_card_not_working", "rupay_transaction_declined", "rupay_reward_issues",
        "nach_mandate_failure", "nach_payment_bounce", "nach_auto_debit_issues",
        "imps_transfer_failed", "imps_beneficiary_issues", "imps_limit_issues",
        "netc_fastag_issues", "netc_double_deduction", "netc_balance_issues",
        "bbps_payment_failed", "bbps_duplicate_payment", "bbps_receipt_issues",
        "general_npci_query", "technical_issues", "other"
    ]
    
    # Default to general if invalid category
    if category not in valid_categories:
        category = "general_npci_query"
    
    grievance = {
        "id": grievance_id,
        "user_id": user_id,
        "category": category,
        "service_type": service_type,
        "description": description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "assigned_to": "NPCI_Support_Team",
        "expected_resolution": "7-10 working days",
        "escalation_level": 1
    }
    grievances_db.append(grievance)
    
    return {
        "success": True,
        "grievance_id": grievance_id,
        "service_type": service_type,
        "expected_resolution": "7-10 working days",
        "message": f"NPCI grievance created successfully with ID: {grievance_id}. Expected resolution: 7-10 working days.",
        "next_steps": "Please save this grievance ID for future reference. You can also contact your bank with this ID."
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
    """Classify the user's intent based on their message with NPCI service focus."""
    user_message_lower = user_message.lower()
    
    # Off-topic/non-NPCI keywords (should be redirected)
    # Using word boundaries to prevent false matches
    import re
    off_topic_patterns = [
        r'\bllm\b', r'\bai\b', r'\bartificial intelligence\b', r'\bmachine learning\b', r'\bchatbot\b', 
        r'\bweather\b', r'\bsports\b', r'\bpolitics\b', r'\bentertainment\b', r'\bpersonal life\b', 
        r'\bphilosophy\b', r'\breligion\b', r'\bwhat is like to be\b', r'\bhow does it feel\b',
        r'\byour experience\b', r'\byour thoughts\b', r'\byour opinion\b', r'\bloan\b', r'\bcredit card bill\b', 
        r'\binvestment\b', r'\binsurance\b', r'\bmutual fund\b', r'\bstock\b', r'\bforex\b'
    ]
    
    # UPI-related keywords
    upi_keywords = ["upi", "unified payment", "payment failed", "money debited", "upi id", "upi pin", "phonepe", "gpay", "paytm", "bhim"]
    
    # RuPay-related keywords  
    rupay_keywords = ["rupay", "debit card", "atm card", "card not working", "card declined", "card blocked"]
    
    # NACH/Mandate keywords
    mandate_keywords = ["nach", "mandate", "auto debit", "emi", "autopay", "standing instruction", "si", "recurring payment"]
    
    # IMPS keywords
    imps_keywords = ["imps", "immediate payment", "instant transfer", "money transfer", "beneficiary"]
    
    # NETC/FASTag keywords
    netc_keywords = ["fastag", "netc", "toll", "toll payment", "blacklist", "recharge"]
    
    # BBPS keywords
    bbps_keywords = ["bbps", "bill payment", "utility bill", "electricity bill", "water bill", "gas bill"]
    
    # General grievance/complaint keywords
    grievance_keywords = ["complaint", "issue", "problem", "grievance", "dispute", "unhappy", "dissatisfied", "error", "failed", "not working"]
    
    # NPCI service inquiry keywords
    npci_service_keywords = ["npci", "what is npci", "transaction limit", "service hours", "contact", "helpline", "support"]
    
    # Check for off-topic first (IMPORTANT: This goes first!)
    if any(re.search(pattern, user_message_lower) for pattern in off_topic_patterns):
        category = "off_topic"
        confidence = 0.95
    elif any(keyword in user_message_lower for keyword in upi_keywords):
        category = "upi_related"
        confidence = 0.9
    elif any(keyword in user_message_lower for keyword in rupay_keywords):
        category = "rupay_related"
        confidence = 0.9
    elif any(keyword in user_message_lower for keyword in mandate_keywords):
        category = "mandate_related"
        confidence = 0.9
    elif any(keyword in user_message_lower for keyword in imps_keywords):
        category = "imps_related"
        confidence = 0.9
    elif any(keyword in user_message_lower for keyword in netc_keywords):
        category = "netc_related"
        confidence = 0.9
    elif any(keyword in user_message_lower for keyword in bbps_keywords):
        category = "bbps_related"
        confidence = 0.9
    elif any(keyword in user_message_lower for keyword in grievance_keywords):
        category = "general_grievance"
        confidence = 0.8
    elif any(keyword in user_message_lower for keyword in npci_service_keywords):
        category = "npci_inquiry"
        confidence = 0.8
    else:
        # If no clear category, assume general NPCI support
        category = "general_npci_support"
        confidence = 0.5  # Lower confidence for unclear messages
    
    return {
        "category": category,
        "confidence": confidence,
        "message": user_message
    }

@action()
async def handle_off_topic_request(user_message: str) -> Dict:
    """Handle off-topic requests by redirecting to NPCI services."""
    return {
        "response": "I'm NPCI Grievance Bot, specialized in helping with NPCI services like UPI, RuPay, NACH, IMPS, FASTag (NETC), and BBPS. I can assist you with payment issues, transaction problems, mandate management, and general NPCI service queries. How can I help you with your NPCI-related needs today?",
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
    """Process general NPCI service inquiries."""
    response_templates = {
        "hours": "NPCI customer support operates through participating banks and service providers. For UPI issues, contact your bank's customer service. For general NPCI queries, visit npci.org.in or call the NPCI helpline.",
        "fees": "NPCI services like UPI are generally free for person-to-person transactions. Merchant transaction fees vary by bank and payment method. Check with your bank for specific fee structures.",
        "contact": "For NPCI-related issues: Visit npci.org.in, contact your bank's customer service, or reach out to your payment app provider. Each NPCI service has dedicated support channels.",
        "upi_limits": "UPI transaction limits: ₹1 lakh per transaction for P2P, ₹2 lakh for P2M. Daily limits may vary by bank. Check with your bank for specific limits.",
        "default": "Thank you for your NPCI-related inquiry. I can help with UPI, RuPay, NACH, IMPS, FASTag, and BBPS issues. Could you please specify which NPCI service you need assistance with?"
    }
    
    user_message_lower = user_message.lower()
    
    if any(word in user_message_lower for word in ["hours", "time", "when", "support"]):
        response = response_templates["hours"]
    elif any(word in user_message_lower for word in ["fee", "charge", "cost", "price"]):
        response = response_templates["fees"]
    elif any(word in user_message_lower for word in ["contact", "phone", "call", "reach", "helpline"]):
        response = response_templates["contact"]
    elif any(word in user_message_lower for word in ["limit", "maximum", "daily", "transaction limit"]):
        response = response_templates["upi_limits"]
    else:
        response = response_templates["default"]
    
    return {
        "message": response,
        "category": "npci_general_inquiry"
    }

# NPCI-Specific Actions

@action()
async def handle_upi_grievance(issue_type: str, transaction_ref: str = "", description: str = "") -> Dict:
    """Handle UPI-specific grievances and provide resolution guidance."""
    upi_resolution_steps = {
        "failed_transaction": {
            "steps": [
                "Check if money was debited from your account",
                "Note down the UPI transaction reference ID",
                "Contact your bank's customer service with the UPI Ref ID",
                "If not resolved in 24 hours, escalate to banking ombudsman",
                "File complaint on NPCI website if needed"
            ],
            "timeline": "T+1 working day for auto-reversal, T+7 for manual resolution",
            "escalation": "Contact RBI Banking Ombudsman if not resolved in 30 days"
        },
        "money_debited": {
            "steps": [
                "Check your bank account statement for debit entry",
                "Verify recipient's account status",
                "Contact your bank with transaction details",
                "File grievance with UPI Ref ID: {transaction_ref}",
                "Monitor for auto-reversal within T+1 working day"
            ],
            "timeline": "Auto-reversal within T+1, manual resolution within T+7",
            "escalation": "NPCI dispute resolution if bank doesn't resolve"
        },
        "upi_id_issues": {
            "steps": [
                "Verify UPI ID format (name@bankname)",
                "Check if recipient UPI ID is active",
                "Try transaction with different UPI ID",
                "Contact your UPI app support team",
                "Register new UPI ID if current one is blocked"
            ],
            "timeline": "Immediate for ID verification, 1-2 days for reactivation",
            "escalation": "Contact bank if UPI ID registration fails"
        }
    }
    
    resolution = upi_resolution_steps.get(issue_type, upi_resolution_steps["failed_transaction"])
    
    # Format steps with transaction reference if provided
    formatted_steps = []
    for step in resolution["steps"]:
        if "{transaction_ref}" in step and transaction_ref:
            formatted_steps.append(step.format(transaction_ref=transaction_ref))
        else:
            formatted_steps.append(step)
    
    return {
        "resolution_steps": formatted_steps,
        "timeline": resolution["timeline"],
        "escalation_path": resolution["escalation"],
        "service_type": "UPI",
        "issue_category": issue_type,
        "reference_id": transaction_ref
    }

@action()
async def handle_mandate_issues(mandate_type: str, issue_description: str = "") -> Dict:
    """Handle NPCI mandate-related issues (e-NACH, UPI AutoPay, etc.)."""
    mandate_solutions = {
        "e_NACH": {
            "common_issues": {
                "mandate_rejection": "Verify bank account details, ensure sufficient balance, check signature match",
                "auto_debit_failure": "Confirm account has adequate balance, verify mandate is active",
                "mandate_cancellation": "Contact biller to cancel, ensure written confirmation, monitor next billing cycle"
            },
            "contact_info": "Contact your bank's NACH support team or biller's customer service"
        },
        "UPI_AutoPay": {
            "common_issues": {
                "autopay_not_working": "Check UPI app settings, verify mandate is active, ensure sufficient balance",
                "mandate_creation_failed": "Verify UPI PIN, check daily transaction limits, retry after 30 minutes",
                "unauthorised_deduction": "Immediately contact bank, file complaint with UPI Ref ID, review all active mandates"
            },
            "contact_info": "Contact your UPI app customer support or issuing bank"
        },
        "SI": {
            "common_issues": {
                "standing_instruction_bounce": "Ensure account has sufficient balance before debit date",
                "si_not_executed": "Verify SI is active, check account status, contact bank if issue persists",
                "duplicate_deduction": "Contact bank immediately, provide transaction details, file written complaint"
            },
            "contact_info": "Contact your bank's customer service for Standing Instruction issues"
        }
    }
    
    mandate_info = mandate_solutions.get(mandate_type, mandate_solutions["e_NACH"])
    
    return {
        "mandate_type": mandate_type,
        "common_solutions": mandate_info["common_issues"],
        "contact_support": mandate_info["contact_info"],
        "general_advice": "Always keep mandate confirmation receipts and monitor account statements regularly",
        "escalation": "File complaint with RBI Banking Ombudsman if bank doesn't resolve within 30 days"
    }

@action()
async def provide_npci_faq(query_type: str) -> Dict:
    """Provide answers to frequently asked questions about NPCI services."""
    npci_faqs = {
        "what_is_npci": {
            "answer": "National Payments Corporation of India (NPCI) is the umbrella organization for operating retail payments and settlement systems in India. It operates UPI, RuPay, NACH, IMPS, and other digital payment systems.",
            "services": ["UPI", "RuPay", "NACH", "IMPS", "NETC (FASTag)", "BBPS", "NFS", "RuPay Credit Cards"]
        },
        "upi_safety": {
            "answer": "UPI is safe with multiple security layers including 2-factor authentication, encrypted data transmission, and transaction limits. Never share your UPI PIN, always verify recipient details, and use authorized UPI apps only.",
            "safety_tips": ["Never share UPI PIN", "Verify recipient before sending money", "Use only bank-approved UPI apps", "Check transaction details before confirming"]
        },
        "rupay_vs_visa": {
            "answer": "RuPay is India's domestic card payment network, accepted across India with lower processing fees. It offers better integration with government schemes and digital payment initiatives compared to international networks.",
            "advantages": ["Lower merchant fees", "Government scheme integration", "Wide acceptance in India", "Enhanced security features"]
        },
        "transaction_limits": {
            "answer": "UPI limits: ₹1 lakh per transaction (P2P), ₹2 lakh (P2M). IMPS: ₹5 lakh per transaction. Limits may vary by bank and customer profile.",
            "limit_details": {
                "UPI P2P": "₹1,00,000 per transaction",
                "UPI P2M": "₹2,00,000 per transaction", 
                "IMPS": "₹5,00,000 per transaction",
                "NACH": "No upper limit (as per mandate)"
            }
        },
        "failed_transaction": {
            "answer": "Failed transactions are usually auto-reversed within T+1 working day. If money is debited but transaction failed, contact your bank with transaction reference ID immediately.",
            "steps": ["Check account statement", "Note transaction reference ID", "Contact bank customer service", "Wait for auto-reversal (T+1)", "Escalate if not resolved in 7 days"]
        }
    }
    
    faq_response = npci_faqs.get(query_type, {
        "answer": "For specific NPCI service queries, please visit npci.org.in or contact your bank's customer service.",
        "additional_info": "You can also reach out to your payment app's customer support for service-specific issues."
    })
    
    return {
        "query_type": query_type,
        "answer": faq_response.get("answer", ""),
        "additional_details": faq_response,
        "official_website": "https://www.npci.org.in",
        "customer_portal": "https://www.npci.org.in/grievance-portal"
    }