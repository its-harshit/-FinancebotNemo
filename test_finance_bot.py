import pytest
import asyncio
from typing import Dict, Any
from finance_bot import NPCIGrievanceBot

class TestNPCIGrievanceBot:
    """Comprehensive test suite for NPCIGrievanceBot with NeMoGuardrails."""
    
    @pytest.fixture
    async def bot(self):
        """Initialize the NPCIGrievanceBot for testing."""
        return NPCIGrievanceBot()
    
    @pytest.mark.asyncio
    async def test_grievance_creation(self, bot):
        """Test grievance creation functionality."""
        result = await bot.create_grievance(
            user_id="test_user_001",
            category="billing_dispute",
            description="Double charge on my account",
            priority="high"
        )
        
        assert result["success"] is True
        assert "grievance_id" in result
        assert result["grievance_id"].startswith("GRV")
        print(f"✅ Grievance created: {result['grievance_id']}")
    
    @pytest.mark.asyncio
    async def test_grievance_status_check(self, bot):
        """Test grievance status retrieval."""
        # First create a grievance
        create_result = await bot.create_grievance(
            user_id="test_user_002",
            category="service_issue",
            description="Cannot access online banking",
            priority="medium"
        )
        
        grievance_id = create_result["grievance_id"]
        status_result = await bot.get_grievance_status(grievance_id)
        
        assert status_result["success"] is True
        assert status_result["grievance"]["id"] == grievance_id
        assert status_result["grievance"]["status"] == "open"
        print(f"✅ Grievance status retrieved for: {grievance_id}")
    
    @pytest.mark.asyncio
    async def test_compliance_check_clean_message(self, bot):
        """Test compliance check with clean message."""
        result = await bot.check_compliance(
            "I need help with my account balance"
        )
        
        assert result["success"] is True
        assert result["compliant"] is True
        assert len(result["issues"]) == 0
        assert result["requires_disclaimer"] is False
        print("✅ Clean message passed compliance check")
    
    @pytest.mark.asyncio
    async def test_compliance_check_sensitive_terms(self, bot):
        """Test compliance check with sensitive terms."""
        result = await bot.check_compliance(
            "My credit card number is 1234-5678-9012-3456"
        )
        
        assert result["success"] is True
        assert result["compliant"] is False
        assert len(result["issues"]) > 0
        assert any("credit card" in issue for issue in result["issues"])
        print("✅ Sensitive terms detected and flagged")
    
    @pytest.mark.asyncio
    async def test_compliance_check_investment_advice(self, bot):
        """Test compliance check with investment advice."""
        result = await bot.check_compliance(
            "I want to invest in stocks for better returns"
        )
        
        assert result["success"] is True
        assert result["requires_disclaimer"] is True
        print("✅ Investment advice requires disclaimer")
    
    @pytest.mark.asyncio
    async def test_message_processing_grievance(self, bot):
        """Test message processing for grievance intent."""
        response = await bot.process_message(
            "I have a complaint about my account being frozen without notice",
            "test_user_003"
        )
        
        assert response["success"] is True
        assert "response" in response
        assert len(response["response"]) > 0
        assert response["metadata"]["compliance_checked"] is True
        print("✅ Grievance message processed successfully")
    
    @pytest.mark.asyncio
    async def test_message_processing_account_inquiry(self, bot):
        """Test message processing for account inquiry."""
        response = await bot.process_message(
            "What's the status of my account?",
            "test_user_004"
        )
        
        assert response["success"] is True
        assert "response" in response
        assert len(response["response"]) > 0
        print("✅ Account inquiry message processed successfully")
    
    @pytest.mark.asyncio
    async def test_message_processing_investment_advice(self, bot):
        """Test message processing with investment advice."""
        response = await bot.process_message(
            "Should I invest in bonds for retirement?",
            "test_user_005"
        )
        
        assert response["success"] is True
        assert "response" in response
        # Check if disclaimer is included
        assert "DISCLAIMER" in response["response"] or "disclaimer" in response["response"].lower()
        print("✅ Investment advice message processed with disclaimer")
    
    @pytest.mark.asyncio
    async def test_grievance_escalation(self, bot):
        """Test grievance escalation functionality."""
        # Import the escalation action directly
        from config.actions import escalate_grievance
        
        # First create a grievance
        create_result = await bot.create_grievance(
            user_id="test_user_006",
            category="urgent_issue",
            description="Account compromised",
            priority="medium"
        )
        
        grievance_id = create_result["grievance_id"]
        
        # Escalate the grievance
        escalation_result = await escalate_grievance(
            grievance_id=grievance_id,
            reason="Security concern - immediate attention required"
        )
        
        assert escalation_result["success"] is True
        
        # Check the updated status
        status_result = await bot.get_grievance_status(grievance_id)
        assert status_result["grievance"]["priority"] == "high"
        assert "escalation_reason" in status_result["grievance"]
        print(f"✅ Grievance {grievance_id} escalated successfully")
    
    @pytest.mark.asyncio
    async def test_response_time_calculation(self, bot):
        """Test response time calculation for grievances."""
        from config.actions import calculate_response_time
        
        # Create a grievance
        create_result = await bot.create_grievance(
            user_id="test_user_007",
            category="general_inquiry",
            description="Question about fees",
            priority="low"
        )
        
        grievance_id = create_result["grievance_id"]
        
        # Calculate response time
        time_result = await calculate_response_time(grievance_id=grievance_id)
        
        assert time_result["success"] is True
        assert "response_time_hours" in time_result
        assert "within_sla" in time_result
        assert time_result["response_time_hours"] >= 0
        print(f"✅ Response time calculated: {time_result['response_time_hours']} hours")
    
    @pytest.mark.asyncio
    async def test_account_info_retrieval(self, bot):
        """Test account information retrieval with security masking."""
        from config.actions import get_account_info
        
        # Test with existing account
        result = await get_account_info(account_id="ACC001")
        
        assert result["success"] is True
        assert "account" in result
        assert result["account"]["name"] == "John Doe"
        assert result["account"]["balance"] == "***"  # Should be masked
        print("✅ Account information retrieved with security masking")
    
    @pytest.mark.asyncio
    async def test_nonexistent_account(self, bot):
        """Test handling of nonexistent account."""
        from config.actions import get_account_info
        
        result = await get_account_info(account_id="NONEXISTENT")
        
        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "Account not found"
        print("✅ Nonexistent account handled correctly")
    
    @pytest.mark.asyncio
    async def test_multiple_grievances(self, bot):
        """Test creating and managing multiple grievances."""
        grievances = []
        
        # Create multiple grievances
        for i in range(3):
            result = await bot.create_grievance(
                user_id=f"test_user_{i:03d}",
                category=f"category_{i}",
                description=f"Test grievance {i}",
                priority="medium"
            )
            grievances.append(result["grievance_id"])
        
        # Verify all grievances were created
        assert len(grievances) == 3
        assert all(grievance.startswith("GRV") for grievance in grievances)
        
        # Check status of all grievances
        for grievance_id in grievances:
            status = await bot.get_grievance_status(grievance_id)
            assert status["success"] is True
            assert status["grievance"]["status"] == "open"
        
        print(f"✅ Multiple grievances created and managed: {grievances}")

async def run_comprehensive_demo():
    """Run a comprehensive demonstration of all FinanceBot capabilities."""
    print("🚀 FinanceBot - Comprehensive NeMoGuardrails Demo")
    print("=" * 60)
    
    bot = FinanceBot()
    
    # Demo 1: Grievance Management Workflow
    print("\n📋 Demo 1: Complete Grievance Management Workflow")
    print("-" * 50)
    
    # Create grievance
    grievance_result = await bot.create_grievance(
        user_id="demo_user_001",
        category="fraud_alert",
        description="Unauthorized transaction detected on my account",
        priority="high"
    )
    print(f"✅ Grievance created: {grievance_result['grievance_id']}")
    
    # Check status
    status = await bot.get_grievance_status(grievance_result['grievance_id'])
    print(f"✅ Status: {status['grievance']['status']} | Priority: {status['grievance']['priority']}")
    
    # Demo 2: Compliance and Security
    print("\n🔒 Demo 2: Compliance and Security Features")
    print("-" * 50)
    
    test_messages = [
        "I need help with my account balance",
        "My credit card number is 1234-5678-9012-3456",
        "Should I invest in stocks for retirement?",
        "What's my SSN? It's 123-45-6789"
    ]
    
    for i, message in enumerate(test_messages, 1):
        compliance = await bot.check_compliance(message)
        print(f"Message {i}: {message[:50]}...")
        print(f"   Compliant: {compliance['compliant']}")
        print(f"   Issues: {compliance['issues']}")
        print(f"   Requires Disclaimer: {compliance['requires_disclaimer']}")
    
    # Demo 3: Message Processing with Different Intents
    print("\n💬 Demo 3: Message Processing with Different Intents")
    print("-" * 50)
    
    test_intents = [
        ("I have a complaint about poor customer service", "grievance"),
        ("What's the status of my account?", "account_inquiry"),
        ("How do I reset my password?", "general_support"),
        ("I want to invest in bonds", "investment_advice")
    ]
    
    for message, expected_intent in test_intents:
        response = await bot.process_message(message, "demo_user_002")
        print(f"Message: {message}")
        print(f"Response: {response['response'][:100]}...")
        print(f"Intent: {response.get('intent', 'unknown')}")
        print()
    
    print("🎉 Comprehensive demo completed successfully!")

async def test_streaming_functionality():
    """Test streaming functionality separately."""
    print("\n🔄 Testing Streaming Functionality...")
    bot = NPCIGrievanceBot()
    
    # Test 1: Basic streaming
    print("\n📡 Test 1: Basic streaming")
    test_message = "My UPI payment failed but money was debited"
    chunks_received = []
    
    try:
        async for chunk in bot.stream_message(test_message, "streaming_test_user"):
            chunks_received.append(chunk)
            print(f"📦 Chunk: {chunk[:50]}..." if len(chunk) > 50 else f"📦 Chunk: {chunk}")
            
        full_response = "".join(chunks_received)
        print(f"✅ Streaming test: Received {len(chunks_received)} chunks")
        print(f"📝 Full response length: {len(full_response)} characters")
        
    except Exception as e:
        print(f"⚠️  Streaming test error: {e}")
    
    # Test 2: Streaming with context
    print("\n🧠 Test 2: Streaming with context")
    conversation_history = [
        {"role": "user", "content": "I have a UPI issue"},
        {"role": "assistant", "content": "I can help you with UPI issues. What specific problem are you facing?"}
    ]
    
    try:
        chunks_received = []
        async for chunk in bot.stream_message(
            "The payment failed but money was debited", 
            "context_streaming_user", 
            conversation_history
        ):
            chunks_received.append(chunk)
            
        print(f"✅ Context streaming: Received {len(chunks_received)} chunks with conversation history")
        
    except Exception as e:
        print(f"⚠️  Context streaming error: {e}")
    
    print("🎉 Streaming tests completed!")

if __name__ == "__main__":
    # Run the comprehensive demo
    asyncio.run(run_comprehensive_demo())
    
    # Run streaming tests
    asyncio.run(test_streaming_functionality())
