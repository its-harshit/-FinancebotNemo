from typing import Dict, List, Optional
from datetime import datetime
import json
from nemoguardrails.actions import action

# Mock database for demonstration
grievances_db = []
accounts_db = {
    "ACC001": {"name": "John Doe", "balance": 5000, "status": "active"},
    "ACC002": {"name": "Jane Smith", "balance": 2500, "status": "active"},
    "ACC003": {"name": "Bob Wilson", "balance": 0, "status": "suspended"}
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
async def check_compliance(message: str) -> Dict:
    """Check if the message complies with financial regulations."""
    compliance_issues = []
    
    # Check for sensitive financial terms
    sensitive_terms = ["credit card", "ssn", "social security", "password", "pin"]
    for term in sensitive_terms:
        if term.lower() in message.lower():
            compliance_issues.append(f"Contains sensitive term: {term}")
    
    # Check for investment advice (requires disclaimers)
    investment_terms = ["invest", "stock", "bond", "portfolio", "return"]
    has_investment_advice = any(term in message.lower() for term in investment_terms)
    
    return {
        "compliant": len(compliance_issues) == 0,
        "issues": compliance_issues,
        "requires_disclaimer": has_investment_advice
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
