#!/usr/bin/env python3
import asyncio
import sys
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
    print("🧠 Context retention: The bot now remembers our conversation!")
    print("⚡ Streaming: Real-time response generation enabled!")
    print("💡 Commands:")
    print("   • 'stream on/off' - Toggle streaming mode")
    print("   • 'quit' or 'exit' - Exit the chat\n")
    
    # Store conversation history
    conversation_history = []
    streaming_enabled = True  # Default to streaming enabled
    
    while True:
        user = input("You: ")
        if user.lower() in {"quit", "exit"}:
            break
        
        # Handle special commands
        if user.lower() == "stream on":
            streaming_enabled = True
            print("✅ Streaming mode enabled")
            continue
        elif user.lower() == "stream off":
            streaming_enabled = False
            print("❌ Streaming mode disabled")
            continue
            
        if streaming_enabled:
            # Stream the response
            print("NPCI Bot: ", end="", flush=True)
            full_response = ""
            
            try:
                async for chunk in bot.stream_message(user, "interactive_user", conversation_history):
                    print(chunk, end="", flush=True)
                    full_response += chunk
                print()  # New line after streaming
                
                # Show context information
                metadata = {"context_messages": len(conversation_history) + 1}
                context_info = f" [Context: {metadata.get('context_messages', 1)} msgs, Streamed]" if metadata.get('context_messages', 1) > 1 else " [Streamed]"
                print(f"{context_info}")
                
                bot_response = full_response
                
            except Exception as e:
                print(f"\n❌ Streaming error: {e}")
                print("🔄 Falling back to non-streaming mode...")
                # Fallback to non-streaming
                res = await bot.process_message(user, "interactive_user", conversation_history)
                bot_response = res.get("response", res.get('error'))
                
                # Show context information
                metadata = res.get("metadata", {})
                context_info = f" [Context: {metadata.get('context_messages', 1)} msgs, Fallback]" if metadata.get('context_messages', 1) > 1 else " [Fallback]"
                print(f"NPCI Bot{context_info}: {bot_response}")
        else:
            # Non-streaming mode (original behavior)
            res = await bot.process_message(user, "interactive_user", conversation_history)
            bot_response = res.get("response", res.get('error'))
            
            # Show context information
            metadata = res.get("metadata", {})
            context_info = f" [Context: {metadata.get('context_messages', 1)} msgs]" if metadata.get('context_messages', 1) > 1 else ""
            
            print(f"NPCI Bot{context_info}: {bot_response}")
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": user})
        conversation_history.append({"role": "assistant", "content": bot_response})
        
        # Keep only last 20 messages (10 exchanges) to prevent memory overflow
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        print()

if __name__ == "__main__":
    asyncio.run(main())