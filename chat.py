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
    
    while True:
        user = input("You: ")
        if user.lower() in {"quit", "exit"}:
            break
        res = await bot.process_message(user, "interactive_user")
        print("NPCI Bot:", res.get("response", res.get('error')))
        print()

asyncio.run(main())