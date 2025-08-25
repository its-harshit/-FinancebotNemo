#!/usr/bin/env python3
import asyncio
from finance_bot import NPCIGrievanceBot

async def main():
    bot = NPCIGrievanceBot()
    print("🏛️ Interactive NPCI Grievance Bot chat. Type 'quit' to exit.\n")
    print("💡 I can help you with:")
    print("   • UPI payment issues and failed transactions")
    print("   • RuPay card problems")
    print("   • NACH mandate and auto-debit issues")
    print("   • IMPS transfer problems") 
    print("   • FASTag and toll payment issues")
    print("   • BBPS bill payment problems")
    print("   • General NPCI service queries\n")
    print("🧠 Context retention: The bot now remembers our conversation!\n")
    
    # Store conversation history
    conversation_history = []
    
    while True:
        user = input("You: ")
        if user.lower() in {"quit", "exit"}:
            break
            
        # Process with conversation history
        res = await bot.process_message(user, "interactive_user", conversation_history)
        bot_response = res.get("response", res.get('error'))
        
        # Show context information
        metadata = res.get("metadata", {})
        context_info = f" [Context: {metadata.get('context_messages', 1)} msgs]" if metadata.get('context_messages', 1) > 1 else ""
        
        print(f"NPCI Bot{context_info}:", bot_response)
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": user})
        conversation_history.append({"role": "assistant", "content": bot_response})
        
        # Keep only last 20 messages (10 exchanges) to prevent memory overflow
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        print()

asyncio.run(main())