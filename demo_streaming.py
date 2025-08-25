#!/usr/bin/env python3
"""
NPCI Grievance Bot - Streaming Demo
Demonstrates the new streaming capabilities added to the bot.
"""

import asyncio
import time
from finance_bot import NPCIGrievanceBot

async def demo_streaming_basic():
    """Demo basic streaming functionality."""
    print("🔄 Demo 1: Basic Streaming")
    print("=" * 50)
    
    bot = NPCIGrievanceBot()
    test_message = "My UPI payment failed but money was debited from my account. Transaction reference: 304912345678"
    
    print(f"User: {test_message}")
    print("\nNPCI Bot (Streaming): ", end="", flush=True)
    
    start_time = time.time()
    chunks_received = []
    first_chunk_time = None
    
    try:
        async for chunk in bot.stream_message(test_message, "demo_user"):
            if first_chunk_time is None:
                first_chunk_time = time.time()
            print(chunk, end="", flush=True)
            chunks_received.append(chunk)
        
        end_time = time.time()
        
        print(f"\n\n📊 Streaming Statistics:")
        print(f"   • Total chunks received: {len(chunks_received)}")
        print(f"   • Time to first chunk: {(first_chunk_time - start_time):.2f}s")
        print(f"   • Total response time: {(end_time - start_time):.2f}s")
        print(f"   • Total response length: {sum(len(chunk) for chunk in chunks_received)} characters")
        
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")

async def demo_streaming_vs_non_streaming():
    """Compare streaming vs non-streaming performance."""
    print("\n🆚 Demo 2: Streaming vs Non-Streaming Comparison")
    print("=" * 50)
    
    bot = NPCIGrievanceBot()
    test_message = "I need help with NACH mandate issues. My auto-debit failed."
    
    print(f"User: {test_message}\n")
    
    # Non-streaming
    print("🐌 Non-Streaming Response:")
    start_time = time.time()
    
    try:
        response = await bot.process_message(test_message, "demo_user_non_stream")
        end_time = time.time()
        
        non_streaming_time = end_time - start_time
        non_streaming_response = response.get("response", "No response")
        
        print(f"Response: {non_streaming_response}")
        print(f"⏱️  Non-streaming time: {non_streaming_time:.2f}s")
        print(f"📏 Response length: {len(non_streaming_response)} characters")
        
    except Exception as e:
        print(f"❌ Non-streaming error: {e}")
        non_streaming_time = 0
        non_streaming_response = ""
    
    print("\n⚡ Streaming Response:")
    start_time = time.time()
    chunks_received = []
    first_chunk_time = None
    
    try:
        async for chunk in bot.stream_message(test_message, "demo_user_stream"):
            if first_chunk_time is None:
                first_chunk_time = time.time()
            print(chunk, end="", flush=True)
            chunks_received.append(chunk)
        
        end_time = time.time()
        streaming_time = end_time - start_time
        streaming_response = "".join(chunks_received)
        
        print(f"\n⏱️  Streaming time: {streaming_time:.2f}s")
        print(f"⏱️  Time to first chunk: {(first_chunk_time - start_time):.2f}s")
        print(f"📏 Response length: {len(streaming_response)} characters")
        
        # Performance comparison
        if non_streaming_time > 0:
            time_saved = max(0, non_streaming_time - (first_chunk_time - start_time))
            print(f"\n🏆 Performance Gain:")
            print(f"   • User sees response {time_saved:.2f}s faster with streaming")
            print(f"   • {len(chunks_received)} chunks delivered progressively")
        
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")

async def demo_streaming_with_context():
    """Demo streaming with conversation context."""
    print("\n🧠 Demo 3: Streaming with Conversation Context")
    print("=" * 50)
    
    bot = NPCIGrievanceBot()
    
    # Build conversation history
    conversation_history = [
        {"role": "user", "content": "I have an issue with my UPI payment"},
        {"role": "assistant", "content": "I can help you with UPI payment issues. What specific problem are you experiencing?"},
        {"role": "user", "content": "The payment failed but money was debited"},
        {"role": "assistant", "content": "I understand this is frustrating. Let me help you with this failed UPI transaction where money was debited."}
    ]
    
    print("📚 Conversation History:")
    for i, msg in enumerate(conversation_history, 1):
        role = "User" if msg["role"] == "user" else "Bot"
        print(f"   {i}. {role}: {msg['content']}")
    
    follow_up = "It was for 500 rupees and the transaction reference is 304912345678"
    print(f"\nUser (Follow-up): {follow_up}")
    print("\nNPCI Bot (Streaming with Context): ", end="", flush=True)
    
    try:
        chunks_received = []
        async for chunk in bot.stream_message(follow_up, "demo_context_user", conversation_history):
            print(chunk, end="", flush=True)
            chunks_received.append(chunk)
        
        print(f"\n\n✅ Context-aware streaming completed!")
        print(f"📊 Processed {len(conversation_history)} previous messages")
        print(f"📦 Delivered {len(chunks_received)} chunks")
        
    except Exception as e:
        print(f"\n❌ Context streaming error: {e}")

async def demo_streaming_error_handling():
    """Demo streaming error handling."""
    print("\n🛡️  Demo 4: Streaming Error Handling")
    print("=" * 50)
    
    bot = NPCIGrievanceBot()
    
    # Test with potentially problematic input
    test_cases = [
        "",  # Empty message
        "a" * 1000,  # Very long message
        "What is the weather today?",  # Off-topic (should be redirected)
        "My credit card number is 1234-5678-9012-3456"  # Sensitive info (should be blocked)
    ]
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_message[:50]}{'...' if len(test_message) > 50 else ''}")
        print("Response: ", end="", flush=True)
        
        try:
            chunks_received = []
            async for chunk in bot.stream_message(test_message, f"error_test_user_{i}"):
                print(chunk, end="", flush=True)
                chunks_received.append(chunk)
            
            print(f" ✅ ({len(chunks_received)} chunks)")
            
        except Exception as e:
            print(f" ❌ Error: {e}")

async def demo_interactive_streaming():
    """Interactive streaming demo."""
    print("\n💬 Demo 5: Interactive Streaming Chat")
    print("=" * 50)
    print("Type messages to see streaming responses. Type 'quit' to exit this demo.")
    print("Try NPCI-related queries like:")
    print("  • 'My UPI payment failed'")
    print("  • 'Help with RuPay card issues'")
    print("  • 'NACH mandate problems'\n")
    
    bot = NPCIGrievanceBot()
    conversation_history = []
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input:
            continue
        
        print("NPCI Bot: ", end="", flush=True)
        
        try:
            full_response = ""
            async for chunk in bot.stream_message(user_input, "interactive_user", conversation_history):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print()  # New line after response
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": full_response})
            
            # Keep only last 10 exchanges
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
        except Exception as e:
            print(f"Error: {e}")
        
        print()

async def main():
    """Run all streaming demos."""
    print("🏛️  NPCI Grievance Bot - Streaming Capabilities Demo")
    print("=" * 60)
    print("This demo showcases the new streaming functionality added to the bot.")
    print("Based on NVIDIA NeMo Guardrails streaming documentation.")
    print("=" * 60)
    
    try:
        await demo_streaming_basic()
        await demo_streaming_vs_non_streaming()
        await demo_streaming_with_context()
        await demo_streaming_error_handling()
        
        # Ask if user wants interactive demo
        print("\n" + "=" * 60)
        response = input("Would you like to try the interactive streaming demo? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            await demo_interactive_streaming()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n🎉 Streaming demo completed!")
    print("\n📚 Key Features Demonstrated:")
    print("   ✅ Real-time token streaming")
    print("   ✅ Context-aware streaming")
    print("   ✅ Error handling in streaming mode")
    print("   ✅ Performance comparison")
    print("   ✅ Interactive streaming chat")
    print("\n🔗 Integration ready for:")
    print("   • OpenWebUI (via webui_server.py)")
    print("   • Direct API usage")
    print("   • Interactive chat (chat.py)")

if __name__ == "__main__":
    asyncio.run(main())
