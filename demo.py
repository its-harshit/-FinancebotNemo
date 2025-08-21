#!/usr/bin/env python3
"""
FinanceBot - NeMoGuardrails Demo Application
A comprehensive demonstration of custom capabilities for a finance company bot.
"""

import asyncio
import os
import sys
from typing import Dict, Any
from finance_bot import FinanceBot

class FinanceBotDemo:
    def __init__(self):
        """Initialize the demo application."""
        self.bot = FinanceBot()
        self.current_user = "demo_user"
        
    async def run_demo(self):
        """Run the main demo application."""
        print("🤖 FinanceBot - NeMoGuardrails Custom Capabilities Demo")
        print("=" * 60)
        print("This demo showcases the full custom capabilities of NeMoGuardrails")
        print("for a finance company bot handling user grievances and support.")
        print()
        
        while True:
            await self.show_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                await self.demo_grievance_management()
            elif choice == "2":
                await self.demo_compliance_checking()
            elif choice == "3":
                await self.demo_message_processing()
            elif choice == "4":
                await self.demo_security_features()
            elif choice == "5":
                await self.demo_account_operations()
            elif choice == "6":
                await self.demo_comprehensive_workflow()
            elif choice == "7":
                await self.run_automated_tests()
            elif choice == "8":
                print("\n👋 Thank you for trying FinanceBot! Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    
    async def show_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 60)
        print("📋 MAIN MENU")
        print("=" * 60)
        print("1. 🎫 Grievance Management Demo")
        print("2. 🔒 Compliance Checking Demo")
        print("3. 💬 Message Processing Demo")
        print("4. 🛡️  Security Features Demo")
        print("5. 💳 Account Operations Demo")
        print("6. 🔄 Comprehensive Workflow Demo")
        print("7. 🧪 Run Automated Tests")
        print("8. 🚪 Exit")
        print("=" * 60)
    
    async def demo_grievance_management(self):
        """Demonstrate grievance management capabilities."""
        print("\n🎫 GRIEVANCE MANAGEMENT DEMO")
        print("-" * 40)
        
        # Create a grievance
        print("Creating a new grievance...")
        grievance_result = await self.bot.create_grievance(
            user_id=self.current_user,
            category="billing_dispute",
            description="I was charged twice for the same transaction on my credit card",
            priority="high"
        )
        
        if grievance_result["success"]:
            grievance_id = grievance_result["grievance_id"]
            print(f"✅ Grievance created successfully: {grievance_id}")
            
            # Check status
            print("\nChecking grievance status...")
            status_result = await self.bot.get_grievance_status(grievance_id)
            if status_result["success"]:
                grievance = status_result["grievance"]
                print(f"📊 Status: {grievance['status']}")
                print(f"📊 Priority: {grievance['priority']}")
                print(f"📊 Category: {grievance['category']}")
                print(f"📊 Created: {grievance['created_at']}")
            
            # Demonstrate escalation
            print("\nEscalating grievance...")
            from config.actions import escalate_grievance
            escalation_result = await escalate_grievance(
                grievance_id=grievance_id,
                reason="Customer reports double charge - urgent financial impact"
            )
            if escalation_result["success"]:
                print("✅ Grievance escalated to high priority")
                
                # Check updated status
                updated_status = await self.bot.get_grievance_status(grievance_id)
                if updated_status["success"]:
                    print(f"📊 New Priority: {updated_status['grievance']['priority']}")
                    print(f"📊 Escalation Reason: {updated_status['grievance']['escalation_reason']}")
        else:
            print(f"❌ Failed to create grievance: {grievance_result.get('error')}")
    
    async def demo_compliance_checking(self):
        """Demonstrate compliance checking capabilities."""
        print("\n🔒 COMPLIANCE CHECKING DEMO")
        print("-" * 40)
        
        test_messages = [
            "I need help with my account balance",
            "My credit card number is 1234-5678-9012-3456",
            "Should I invest in stocks for retirement?",
            "What's my SSN? It's 123-45-6789",
            "I want to discuss my portfolio returns"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Message {i}: {message}")
            compliance_result = await self.bot.check_compliance(message)
            
            if compliance_result["success"]:
                print(f"   ✅ Compliant: {compliance_result['compliant']}")
                if compliance_result['issues']:
                    print(f"   ⚠️  Issues: {', '.join(compliance_result['issues'])}")
                print(f"   📋 Requires Disclaimer: {compliance_result['requires_disclaimer']}")
            else:
                print(f"   ❌ Error: {compliance_result.get('error')}")
    
    async def demo_message_processing(self):
        """Demonstrate message processing with different intents."""
        print("\n💬 MESSAGE PROCESSING DEMO")
        print("-" * 40)
        
        test_cases = [
            ("I have a complaint about poor customer service", "Grievance"),
            ("What's the status of my account?", "Account Inquiry"),
            ("How do I reset my password?", "General Support"),
            ("I want to invest in bonds for retirement", "Investment Advice"),
            ("My account was frozen without notice", "Urgent Issue")
        ]
        
        for message, expected_type in test_cases:
            print(f"\n📝 {expected_type}: {message}")
            response = await self.bot.process_message(message, self.current_user)
            
            if response["success"]:
                print(f"   🤖 Response: {response['response'][:100]}...")
                print(f"   🎯 Intent: {response.get('intent', 'unknown')}")
                print(f"   🔒 Compliance Checked: {response['metadata']['compliance_checked']}")
                print(f"   ⚠️  Sensitive Info Detected: {response['metadata']['sensitive_info_detected']}")
                print(f"   📋 Requires Disclaimer: {response['metadata']['requires_disclaimer']}")
            else:
                print(f"   ❌ Error: {response.get('error')}")
    
    async def demo_security_features(self):
        """Demonstrate security and sensitive information detection."""
        print("\n🛡️ SECURITY FEATURES DEMO")
        print("-" * 40)
        
        security_test_cases = [
            ("My SSN is 123-45-6789", "SSN Detection"),
            ("Credit card: 1234-5678-9012-3456", "Credit Card Detection"),
            ("My password is secret123", "Password Detection"),
            ("PIN number is 1234", "PIN Detection"),
            ("Normal message without sensitive data", "Clean Message")
        ]
        
        for message, test_type in security_test_cases:
            print(f"\n🔍 {test_type}: {message}")
            
            # Check compliance
            compliance = await self.bot.check_compliance(message)
            print(f"   🔒 Compliant: {compliance['compliant']}")
            if compliance['issues']:
                print(f"   ⚠️  Security Issues: {', '.join(compliance['issues'])}")
            
            # Process message
            response = await self.bot.process_message(message, self.current_user)
            if response["success"]:
                print(f"   🤖 Response: {response['response'][:80]}...")
            else:
                print(f"   ❌ Message Rejected: {response.get('error')}")
    
    async def demo_account_operations(self):
        """Demonstrate account-related operations."""
        print("\n💳 ACCOUNT OPERATIONS DEMO")
        print("-" * 40)
        
        from config.actions import get_account_info, calculate_response_time
        
        # Test account retrieval
        print("Testing account information retrieval...")
        account_result = await get_account_info("ACC001")
        if account_result["success"]:
            account = account_result["account"]
            print(f"   ✅ Account: {account['name']}")
            print(f"   ✅ Status: {account['status']}")
            print(f"   ✅ Balance: {account['balance']} (masked for security)")
        else:
            print(f"   ❌ Error: {account_result['error']}")
        
        # Test nonexistent account
        print("\nTesting nonexistent account...")
        nonexistent_result = await get_account_info("NONEXISTENT")
        if not nonexistent_result["success"]:
            print(f"   ✅ Properly handled: {nonexistent_result['error']}")
        
        # Test response time calculation
        print("\nTesting response time calculation...")
        # First create a grievance
        grievance_result = await self.bot.create_grievance(
            user_id=self.current_user,
            category="test",
            description="Test for response time calculation",
            priority="low"
        )
        
        if grievance_result["success"]:
            time_result = await calculate_response_time(grievance_result["grievance_id"])
            if time_result["success"]:
                print(f"   ✅ Response Time: {time_result['response_time_hours']} hours")
                print(f"   ✅ Within SLA: {time_result['within_sla']}")
    
    async def demo_comprehensive_workflow(self):
        """Demonstrate a complete customer service workflow."""
        print("\n🔄 COMPREHENSIVE WORKFLOW DEMO")
        print("-" * 40)
        
        print("Simulating a complete customer interaction...")
        
        # Step 1: Customer reports an issue
        print("\n1️⃣ Customer reports billing issue...")
        user_message = "I was charged twice for the same transaction and I'm very upset about this billing error."
        response = await self.bot.process_message(user_message, self.current_user)
        
        if response["success"]:
            print(f"   🤖 Bot Response: {response['response'][:100]}...")
        
        # Step 2: Create grievance
        print("\n2️⃣ Creating grievance ticket...")
        grievance_result = await self.bot.create_grievance(
            user_id=self.current_user,
            category="billing_error",
            description="Double charge on transaction - customer very upset",
            priority="high"
        )
        
        if grievance_result["success"]:
            grievance_id = grievance_result["grievance_id"]
            print(f"   ✅ Grievance ID: {grievance_id}")
        
        # Step 3: Customer asks about investment
        print("\n3️⃣ Customer asks about investment advice...")
        investment_message = "While we're at it, should I invest in stocks for better returns?"
        investment_response = await self.bot.process_message(investment_message, self.current_user)
        
        if investment_response["success"]:
            print(f"   🤖 Bot Response: {investment_response['response'][:100]}...")
            print(f"   📋 Disclaimer Added: {investment_response['metadata']['requires_disclaimer']}")
        
        # Step 4: Check grievance status
        print("\n4️⃣ Checking grievance status...")
        if grievance_result["success"]:
            status = await self.bot.get_grievance_status(grievance_id)
            if status["success"]:
                print(f"   📊 Status: {status['grievance']['status']}")
                print(f"   📊 Priority: {status['grievance']['priority']}")
        
        print("\n✅ Complete workflow demonstrated successfully!")
    
    async def run_automated_tests(self):
        """Run automated tests to verify functionality."""
        print("\n🧪 RUNNING AUTOMATED TESTS")
        print("-" * 40)
        
        # Import and run tests
        try:
            from test_finance_bot import TestFinanceBot
            import pytest
            
            print("Running comprehensive test suite...")
            # Note: In a real scenario, you'd run pytest properly
            # For demo purposes, we'll run a few key tests manually
            
            test_bot = TestFinanceBot()
            
            # Test grievance creation
            print("Testing grievance creation...")
            result = await test_bot.test_grievance_creation(test_bot.bot())
            print("   ✅ Grievance creation test passed")
            
            # Test compliance checking
            print("Testing compliance checking...")
            result = await test_bot.test_compliance_check_clean_message(test_bot.bot())
            print("   ✅ Compliance checking test passed")
            
            print("\n✅ All automated tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            print("Note: Full test suite requires pytest to be run separately")

async def main():
    """Main entry point for the demo application."""
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set.")
        print("   Some features may not work properly.")
        print("   Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        print()
    
    demo = FinanceBotDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
