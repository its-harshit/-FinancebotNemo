import asyncio
import os
from typing import Dict, Any, List, AsyncIterator
from dotenv import load_dotenv
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.actions import action
from nemoguardrails.streaming import StreamingHandler

# Load environment variables
load_dotenv()

class NPCIGrievanceBot:
    def __init__(self):
        """Initialize the NPCI Grievance Bot with NeMoGuardrails configuration."""
        # Load configuration from the config directory
        self.config = RailsConfig.from_path("config")
        self.rails = LLMRails(config=self.config)
        
    async def process_message(self, user_message: str, user_id: str = "default_user", conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process a user message through the NPCI Grievance Bot system with context retention.
        
        Args:
            user_message: The user's input message about NPCI services
            user_id: Unique identifier for the user
            conversation_history: Previous messages in the conversation
            
        Returns:
            Dictionary containing the bot's response and NPCI service metadata
        """
        try:
            # Build message history for context
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                # Limit to last 10 messages for context (prevent token overflow)
                recent_history = conversation_history[-10:]
                messages.extend(recent_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Process through NeMoGuardrails with full context
            raw = await self.rails.generate_async(messages=messages)

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
                    "bot_type": "npci_grievance_bot",
                    "context_messages": len(messages),
                    "has_conversation_history": conversation_history is not None and len(conversation_history) > 0
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
    
    async def stream_message(self, user_message: str, user_id: str = "default_user", conversation_history: List[Dict] = None) -> AsyncIterator[str]:
        """
        Stream a user message response through the NPCI Grievance Bot system using optimized NeMo streaming.
        
        Args:
            user_message: The user's input message about NPCI services
            user_id: Unique identifier for the user
            conversation_history: Previous messages in the conversation
            
        Yields:
            String chunks of the bot's response as they are generated
        """
        try:
            # Build message history for context
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                # Limit to last 8 messages for context (optimized for streaming performance)
                recent_history = conversation_history[-8:]
                messages.extend(recent_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Use NeMo Guardrails standard streaming API
            async for chunk in self.rails.stream_async(messages=messages):
                # Only yield non-empty chunks
                if chunk and chunk.strip():
                    yield chunk
                
        except Exception as e:
            # Yield error message as a single chunk
            yield f"I apologize, but I encountered an error processing your request: {str(e)}"
    
    async def stream_message_with_handler(self, user_message: str, user_id: str = "default_user", conversation_history: List[Dict] = None) -> tuple[AsyncIterator[str], Dict[str, Any]]:
        """
        Stream a user message response with full response handling.
        
        Args:
            user_message: The user's input message about NPCI services
            user_id: Unique identifier for the user
            conversation_history: Previous messages in the conversation
            
        Returns:
            Tuple of (streaming_iterator, final_response_dict)
        """
        try:
            # Build message history for context
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                recent_history = conversation_history[-10:]
                messages.extend(recent_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Create streaming handler
            streaming_handler = StreamingHandler()
            
            # Start the generation task
            async def get_final_response():
                return await self.rails.generate_async(
                    messages=messages, 
                    streaming_handler=streaming_handler
                )
            
            # Create task for final response
            response_task = asyncio.create_task(get_final_response())
            
            # Create async iterator for chunks
            async def chunk_iterator():
                async for chunk in streaming_handler:
                    yield chunk
            
            # Wait for final response
            final_response = await response_task
            
            # Process final response similar to process_message
            if isinstance(final_response, dict):
                bot_msg = final_response.get("content", "")
                intent_val = final_response.get("intent", "unknown")
                sensitive = final_response.get("sensitive_detected", False)
                disclaimer = final_response.get("requires_disclaimer", False)
            else:
                bot_msg = getattr(final_response, "content", "")
                intent_val = getattr(final_response, "intent", "unknown")
                sensitive = getattr(final_response, "sensitive_detected", False)
                disclaimer = getattr(final_response, "requires_disclaimer", False)

            response_dict = {
                "success": True,
                "response": bot_msg,
                "user_id": user_id,
                "intent": intent_val,
                "metadata": {
                    "compliance_checked": True,
                    "sensitive_info_detected": sensitive,
                    "requires_disclaimer": disclaimer,
                    "service_type": "NPCI",
                    "bot_type": "npci_grievance_bot",
                    "context_messages": len(messages),
                    "has_conversation_history": conversation_history is not None and len(conversation_history) > 0,
                    "streaming_enabled": True
                }
            }
            
            return chunk_iterator(), response_dict
            
        except Exception as e:
            # Return error iterator and response
            async def error_iterator():
                yield f"I apologize, but I encountered an error: {str(e)}"
            
            error_response = {
                "success": False,
                "error": str(e),
                "user_id": user_id,
                "metadata": {"streaming_enabled": True}
            }
            
            return error_iterator(), error_response

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
        print(f"Bot Response: {response['response'][:200]}...")
    else:
        print(f"Bot Error: {response.get('error', 'Unknown error')}")
    
    # Test 2b: Context retention test
    print("\n🧠 Test 2b: Context retention test")
    conversation_history = [
        {"role": "user", "content": "My UPI payment failed but money was debited"},
        {"role": "assistant", "content": "I understand your UPI payment issue. Let me help you resolve this."}
    ]
    followup_message = "It was for 500 rupees"
    context_response = await npci_bot.process_message(followup_message, "user123", conversation_history)
    if context_response.get("success"):
        metadata = context_response.get("metadata", {})
        print(f"Context Messages: {metadata.get('context_messages', 0)}")
        print(f"Has Context: {metadata.get('has_conversation_history', False)}")
        print(f"Context Response: {context_response['response'][:200]}...")
    else:
        print(f"Context Error: {context_response.get('error', 'Unknown error')}")
    
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
