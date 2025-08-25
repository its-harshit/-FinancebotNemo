import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.actions import action

# Load environment variables
load_dotenv()

class NPCIGrievanceBot:
    def __init__(self):
        """Initialize the NPCI Grievance Bot with NeMoGuardrails configuration."""
        # Load configuration from the config directory
        self.config = RailsConfig.from_path("config")
        self.rails = LLMRails(config=self.config)
        
    async def process_message(self, user_message: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Process a user message through the NPCI Grievance Bot system.
        
        Args:
            user_message: The user's input message about NPCI services
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing the bot's response and NPCI service metadata
        """
        try:
            # Process the message through NeMoGuardrails
            raw = await self.rails.generate_async(
                messages=[{"role": "user", "content": user_message}]
            )

            # Depending on NeMoGuardrails version, generate_async may return
            # a dict or an object with .content
            if isinstance(raw, dict):
                bot_msg = raw.get("content", "")
                intent_val = raw.get("intent", "unknown")
                sensitive = raw.get("sensitive_detected", False)
                disclaimer = raw.get("requires_disclaimer", False)
            else:
                bot_msg = getattr(raw, "content", "")
                intent_val = getattr(raw, "intent", "unknown")
                sensitive = getattr(raw, "sensitive_detected", False)
                disclaimer = getattr(raw, "requires_disclaimer", False)

            return {
                "success": True,
                "response": bot_msg,
                "user_id": user_id,
                "intent": intent_val,
                "metadata": {
                    "compliance_checked": True,
                    "sensitive_info_detected": sensitive,
                    "requires_disclaimer": disclaimer,
                    "service_type": "NPCI",
                    "bot_type": "npci_grievance_bot"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id
            }
    
    async def create_grievance(self, user_id: str, category: str, description: str, priority: str = "medium") -> Dict[str, Any]:
        """Create a new grievance ticket."""
        try:
            # Import the action directly for better error handling
            from config.actions import create_grievance
            result = await create_grievance(
                user_id=user_id,
                category=category,
                description=description,
                priority=priority
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_grievance_status(self, grievance_id: str) -> Dict[str, Any]:
        """Get the status of a grievance."""
        try:
            from config.actions import get_grievance_status
            result = await get_grievance_status(grievance_id=grievance_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def check_compliance(self, message: str) -> Dict[str, Any]:
        """Check message compliance with NPCI policies."""
        try:
            from config.actions import check_compliance
            result = await check_compliance(message=message)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def handle_upi_issue(self, issue_type: str, transaction_ref: str = "", description: str = "") -> Dict[str, Any]:
        """Handle UPI-specific issues and provide resolution guidance."""
        try:
            from config.actions import handle_upi_grievance
            result = await handle_upi_grievance(
                issue_type=issue_type,
                transaction_ref=transaction_ref,
                description=description
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def handle_mandate_issue(self, mandate_type: str, issue_description: str = "") -> Dict[str, Any]:
        """Handle NPCI mandate-related issues."""
        try:
            from config.actions import handle_mandate_issues
            result = await handle_mandate_issues(
                mandate_type=mandate_type,
                issue_description=issue_description
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_npci_faq(self, query_type: str) -> Dict[str, Any]:
        """Get answers to NPCI FAQ questions."""
        try:
            from config.actions import provide_npci_faq
            result = await provide_npci_faq(query_type=query_type)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global bot instance
npci_bot = NPCIGrievanceBot()

async def main():
    """Main function to demonstrate the NPCI Grievance Bot capabilities."""
    print("🏛️ NPCI Grievance Bot - NeMoGuardrails Demo")
    print("=" * 60)
    
    # Test 1: UPI grievance creation
    print("\n📝 Test 1: Creating a UPI grievance")
    grievance_result = await npci_bot.create_grievance(
        user_id="user123",
        category="upi_transaction_failure",
        description="UPI payment failed but money was debited from my account",
        priority="high"
    )
    print(f"UPI Grievance Result: {grievance_result}")
    
    # Test 2: Processing UPI message
    print("\n💬 Test 2: Processing UPI user message")
    user_message = "My UPI payment failed but money was debited. Transaction ref: 304912345678"
    response = await npci_bot.process_message(user_message, "user123")
    if response.get("success") and "response" in response:
        print(f"Bot Response: {response['response']}")
    else:
        print(f"Bot Error: {response.get('error', 'Unknown error')}")
    
    # Test 3: UPI specific issue handling
    print("\n🔧 Test 3: UPI issue handling")
    upi_result = await npci_bot.handle_upi_issue(
        issue_type="money_debited",
        transaction_ref="304912345678",
        description="Money debited but payment failed"
    )
    print(f"UPI Resolution: {upi_result}")
    
    # Test 4: NPCI FAQ
    print("\n❓ Test 4: NPCI FAQ")
    faq_result = await npci_bot.get_npci_faq("upi_safety")
    print(f"FAQ Result: {faq_result}")
    
    # Test 5: Mandate issue handling
    print("\n📋 Test 5: Mandate issue handling")
    mandate_result = await npci_bot.handle_mandate_issue(
        mandate_type="e_NACH",
        issue_description="Auto debit failed for EMI payment"
    )
    print(f"Mandate Resolution: {mandate_result}")
    
    # Test 6: Grievance status check
    if grievance_result.get("success"):
        grievance_id = grievance_result.get("grievance_id")
        print(f"\n📊 Test 6: Checking grievance status for {grievance_id}")
        status_result = await npci_bot.get_grievance_status(grievance_id)
        print(f"Status Result: {status_result}")

if __name__ == "__main__":
    asyncio.run(main())
