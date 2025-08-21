#!/usr/bin/env python3
"""
FinanceBot Quick Start Demo
A simple demonstration that runs automatically without user interaction.
"""

import asyncio
import os
from finance_bot import FinanceBot

async def quick_demo():
    """Run a quick demonstration of FinanceBot capabilities."""
    print("🚀 FinanceBot - Quick Start Demo")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some features may not work.")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # Initialize bot
    print("🤖 Initializing FinanceBot...")
    bot = FinanceBot()
    
    # Demo 1: Grievance Creation
    print("\n📝 Demo 1: Creating a Grievance")
    print("-" * 30)
    grievance_result = await bot.create_grievance(
        user_id="demo_user",
        category="billing_dispute",
        description="I was charged twice for the same transaction",
        priority="high"
    )
    
    if grievance_result["success"]:
        print(f"✅ Grievance created: {grievance_result['grievance_id']}")
    else:
        print(f"❌ Failed: {grievance_result.get('error')}")
    
    # Demo 2: Compliance Check
    print("\n🔒 Demo 2: Compliance Checking")
    print("-" * 30)
    test_messages = [
        "I need help with my account",
        "My credit card is 1234-5678-9012-3456",
        "Should I invest in stocks?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        compliance = await bot.check_compliance(message)
        print(f"Message {i}: {message[:30]}...")
        print(f"   Compliant: {compliance['compliant']}")
        if compliance['issues']:
            print(f"   Issues: {compliance['issues']}")
        print(f"   Needs Disclaimer: {compliance['requires_disclaimer']}")
    
    # Demo 3: Message Processing
    print("\n💬 Demo 3: Message Processing")
    print("-" * 30)
    user_message = "I have a complaint about my account being frozen"
    response = await bot.process_message(user_message, "demo_user")
    
    if response["success"]:
        print(f"User: {user_message}")
        print(f"Bot: {response['response'][:100]}...")
        print(f"Intent: {response.get('intent', 'unknown')}")
    else:
        print(f"❌ Error: {response.get('error')}")
    
    # Demo 4: Account Operations
    print("\n💳 Demo 4: Account Operations")
    print("-" * 30)
    from config.actions import get_account_info
    
    account_result = await get_account_info("ACC001")
    if account_result["success"]:
        account = account_result["account"]
        print(f"✅ Account: {account['name']}")
        print(f"✅ Status: {account['status']}")
        print(f"✅ Balance: {account['balance']} (masked)")
    else:
        print(f"❌ Error: {account_result['error']}")
    
    print("\n🎉 Quick demo completed!")
    print("Run 'python demo.py' for the full interactive experience.")

if __name__ == "__main__":
    asyncio.run(quick_demo())
