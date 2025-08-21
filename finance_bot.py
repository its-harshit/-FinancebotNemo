import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.actions import action

# Load environment variables
load_dotenv()

class FinanceBot:
    def __init__(self):
        """Initialize the FinanceBot with NeMoGuardrails configuration."""
        # Load configuration from the config directory
        self.config = RailsConfig.from_path("config")
        self.rails = LLMRails(config=self.config)
        
    async def process_message(self, user_message: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Process a user message through the NeMoGuardrails system.
        
        Args:
            user_message: The user's input message
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing the bot's response and metadata
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
                    "requires_disclaimer": disclaimer
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
        """Check message compliance."""
        try:
            from config.actions import check_compliance
            result = await check_compliance(message=message)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global bot instance
finance_bot = FinanceBot()

async def main():
    """Main function to demonstrate the FinanceBot capabilities."""
    print("🤖 FinanceBot - NeMoGuardrails Demo")
    print("=" * 50)
    
    # Test 1: Basic grievance creation
    print("\n📝 Test 1: Creating a grievance")
    grievance_result = await finance_bot.create_grievance(
        user_id="user123",
        category="billing_dispute",
        description="I was charged twice for the same transaction",
        priority="high"
    )
    print(f"Grievance Result: {grievance_result}")
    
    # Test 2: Processing a user message
    print("\n💬 Test 2: Processing user message")
    user_message = "I need help with a billing dispute. I was charged twice for the same transaction."
    response = await finance_bot.process_message(user_message, "user123")
    if response.get("success") and "response" in response:
        print(f"Bot Response: {response['response']}")
    else:
        print(f"Bot Error: {response.get('error', 'Unknown error')}")
    
    # Test 3: Compliance check
    print("\n🔒 Test 3: Compliance check")
    compliance_result = await finance_bot.check_compliance(
        "I want to invest in stocks and bonds for better returns"
    )
    print(f"Compliance Result: {compliance_result}")
    
    # Test 4: Grievance status check
    if grievance_result.get("success"):
        grievance_id = grievance_result.get("grievance_id")
        print(f"\n📊 Test 4: Checking grievance status for {grievance_id}")
        status_result = await finance_bot.get_grievance_status(grievance_id)
        print(f"Status Result: {status_result}")

if __name__ == "__main__":
    asyncio.run(main())
