#!/usr/bin/env python3
import asyncio
from finance_bot import FinanceBot

async def main():
    bot = FinanceBot()
    print("💬 Interactive FinanceBot chat.  Type 'quit' to exit.\n")
    while True:
        user = input("You: ")
        if user.lower() in {"quit", "exit"}:
            break
        res = await bot.process_message(user, "interactive_user")
        print("Bot:", res.get("response", res.get('error')))
asyncio.run(main())