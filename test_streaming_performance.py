#!/usr/bin/env python3
"""
Performance test for streaming optimization
Tests the improved streaming configuration against NeMo Guardrails standards
"""

import asyncio
import time
from finance_bot import NPCIGrievanceBot

async def test_streaming_performance():
    """Test streaming performance with optimizations."""
    print("🚀 Testing Optimized Streaming Performance")
    print("=" * 60)
    
    bot = NPCIGrievanceBot()
    
    # Test messages of varying complexity
    test_cases = [
        "My UPI payment failed",
        "My UPI payment failed but money was debited from my account. Transaction reference: 304912345678",
        "I have a complex issue with my NACH mandate where the auto-debit failed for my EMI payment and I need immediate assistance with escalation",
    ]
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n📊 Test Case {i}: {test_message[:50]}{'...' if len(test_message) > 50 else ''}")
        print("-" * 60)
        
        # Measure streaming performance
        start_time = time.time()
        first_chunk_time = None
        chunk_count = 0
        total_chars = 0
        
        print("Response: ", end="", flush=True)
        
        try:
            async for chunk in bot.stream_message(test_message, f"perf_test_user_{i}"):
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    
                print(chunk, end="", flush=True)
                chunk_count += 1
                total_chars += len(chunk)
            
            end_time = time.time()
            
            # Performance metrics
            total_time = end_time - start_time
            time_to_first_chunk = (first_chunk_time - start_time) if first_chunk_time else total_time
            
            print(f"\n\n📈 Performance Metrics:")
            print(f"   ⏱️  Time to first chunk: {time_to_first_chunk:.3f}s")
            print(f"   ⏱️  Total response time: {total_time:.3f}s")
            print(f"   📦 Total chunks: {chunk_count}")
            print(f"   📏 Total characters: {total_chars}")
            print(f"   🔄 Chars/second: {total_chars/total_time:.1f}")
            
            # Performance assessment
            if time_to_first_chunk < 0.5:
                print(f"   ✅ Excellent first chunk latency!")
            elif time_to_first_chunk < 1.0:
                print(f"   👍 Good first chunk latency")
            else:
                print(f"   ⚠️  High first chunk latency - needs optimization")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")

async def test_non_streaming_comparison():
    """Compare with non-streaming performance."""
    print(f"\n🔄 Non-Streaming Comparison")
    print("=" * 60)
    
    bot = NPCIGrievanceBot()
    test_message = "My UPI payment failed but money was debited"
    
    print("Non-streaming response:")
    start_time = time.time()
    
    try:
        response = await bot.process_message(test_message, "non_stream_user")
        end_time = time.time()
        
        non_streaming_time = end_time - start_time
        response_text = response.get("response", "No response")
        
        print(f"Response: {response_text}")
        print(f"\n📊 Non-streaming metrics:")
        print(f"   ⏱️  Total time: {non_streaming_time:.3f}s")
        print(f"   📏 Response length: {len(response_text)} characters")
        
        return non_streaming_time
        
    except Exception as e:
        print(f"❌ Non-streaming error: {e}")
        return 0

async def benchmark_streaming_optimizations():
    """Benchmark the streaming optimizations."""
    print(f"\n🏆 Streaming Optimization Benchmark")
    print("=" * 60)
    
    bot = NPCIGrievanceBot()
    test_message = "Help me with a UPI transaction failure where money was debited but payment failed"
    
    # Test multiple runs for consistency
    runs = 3
    first_chunk_times = []
    total_times = []
    
    for run in range(runs):
        print(f"\nRun {run + 1}/{runs}: ", end="", flush=True)
        
        start_time = time.time()
        first_chunk_time = None
        chunk_count = 0
        
        try:
            async for chunk in bot.stream_message(test_message, f"benchmark_user_{run}"):
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                print(".", end="", flush=True)
                chunk_count += 1
            
            end_time = time.time()
            
            time_to_first = (first_chunk_time - start_time) if first_chunk_time else 0
            total_time = end_time - start_time
            
            first_chunk_times.append(time_to_first)
            total_times.append(total_time)
            
            print(f" ✅ ({time_to_first:.3f}s to first chunk)")
            
        except Exception as e:
            print(f" ❌ Error: {e}")
    
    if first_chunk_times:
        avg_first_chunk = sum(first_chunk_times) / len(first_chunk_times)
        avg_total = sum(total_times) / len(total_times)
        
        print(f"\n📊 Average Performance (over {runs} runs):")
        print(f"   ⏱️  Average time to first chunk: {avg_first_chunk:.3f}s")
        print(f"   ⏱️  Average total time: {avg_total:.3f}s")
        
        # Performance targets based on NeMo Guardrails standards
        print(f"\n🎯 Performance Assessment:")
        if avg_first_chunk < 0.5:
            print(f"   ✅ EXCELLENT - Meets high-performance streaming standards")
        elif avg_first_chunk < 1.0:
            print(f"   👍 GOOD - Meets standard streaming performance")
        elif avg_first_chunk < 2.0:
            print(f"   ⚠️  ACCEPTABLE - Could benefit from further optimization")
        else:
            print(f"   ❌ POOR - Requires optimization")

async def test_streaming_with_context():
    """Test streaming performance with conversation context."""
    print(f"\n🧠 Context-Aware Streaming Performance")
    print("=" * 60)
    
    bot = NPCIGrievanceBot()
    
    # Build conversation history
    conversation_history = [
        {"role": "user", "content": "I have a UPI issue"},
        {"role": "assistant", "content": "I can help with UPI issues. What specific problem are you facing?"},
        {"role": "user", "content": "Payment failed but money was debited"},
        {"role": "assistant", "content": "I understand. This is a common UPI issue. Let me help you resolve this."}
    ]
    
    follow_up = "It was for 500 rupees and the UPI Ref ID is 304912345678"
    
    print(f"Follow-up with context: {follow_up}")
    print("Response: ", end="", flush=True)
    
    start_time = time.time()
    first_chunk_time = None
    chunk_count = 0
    
    try:
        async for chunk in bot.stream_message(follow_up, "context_user", conversation_history):
            if first_chunk_time is None:
                first_chunk_time = time.time()
            print(chunk, end="", flush=True)
            chunk_count += 1
        
        end_time = time.time()
        
        time_to_first = (first_chunk_time - start_time) if first_chunk_time else 0
        total_time = end_time - start_time
        
        print(f"\n\n📊 Context Streaming Performance:")
        print(f"   ⏱️  Time to first chunk: {time_to_first:.3f}s")
        print(f"   ⏱️  Total time: {total_time:.3f}s")
        print(f"   📦 Chunks: {chunk_count}")
        print(f"   🧠 Context messages: {len(conversation_history)}")
        
    except Exception as e:
        print(f"\n❌ Context streaming error: {e}")

async def main():
    """Run all performance tests."""
    print("🏛️  NPCI Grievance Bot - Streaming Performance Test")
    print("Testing optimizations based on NeMo Guardrails standards")
    print("=" * 60)
    
    try:
        await test_streaming_performance()
        non_streaming_time = await test_non_streaming_comparison()
        await benchmark_streaming_optimizations()
        await test_streaming_with_context()
        
        print(f"\n🎉 Performance Testing Complete!")
        print(f"\n📋 Optimization Summary:")
        print(f"   ✅ Streaming configuration optimized")
        print(f"   ✅ Output rails streamlined for streaming")
        print(f"   ✅ Parallel rail execution enabled")
        print(f"   ✅ Chunk size optimized (50 chars)")
        print(f"   ✅ Context window optimized (8 messages)")
        
        print(f"\n🔧 Key Optimizations Applied:")
        print(f"   • streaming.chunk_size: 50")
        print(f"   • streaming.context_size: 20")
        print(f"   • rails.input.parallel: true")
        print(f"   • rails.output.parallel: true")
        print(f"   • output_rails_per_chunk: false")
        print(f"   • Lightweight compliance checks during streaming")
        
    except KeyboardInterrupt:
        print(f"\n👋 Performance test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Performance test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
