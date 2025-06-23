#!/usr/bin/env python3
"""
Simple async demo for the python-result-type library.
"""

import asyncio
from result_type import Success, Failure, Result
from result_type.async_result import AsyncResult, async_safe_call


async def simple_demo():
    """Simple demonstration of async Result functionality."""
    print("🚀 Async Result Type Demo\n")
    
    # Example 1: Basic async operation
    async def fetch_data(source: str) -> Result[dict, str]:
        await asyncio.sleep(0.1)
        if source == "good":
            return Success({"data": "fetched successfully", "source": source})
        return Failure(f"Failed to fetch from {source}")
    
    print("1. Basic async operation:")
    result = await fetch_data("good")
    if isinstance(result, Success):
        print(f"   ✅ {result.value}")
    
    result = await fetch_data("bad")
    if isinstance(result, Failure):
        print(f"   ❌ {result.error}")
    
    print()
    
    # Example 2: Chaining operations
    print("2. Chaining async operations:")
    
    async def process_data(data: dict) -> Result[str, str]:
        await asyncio.sleep(0.1)
        return Success(f"Processed: {data['data']}")
    
    def format_result(processed: str) -> Result[str, str]:
        return Success(f"📋 Final result: {processed}")
    
    # Chain operations
    chain_result = (AsyncResult(fetch_data("good"))
                   .then_async(process_data)
                   .then_sync(format_result))
    
    final = await chain_result.resolve()
    if isinstance(final, Success):
        print(f"   ✅ {final.value}")
    
    print()
    
    # Example 3: Safe async call
    print("3. Safe async call:")
    
    async def risky_operation():
        await asyncio.sleep(0.1)
        raise ValueError("Something went wrong!")
    
    safe_result = await async_safe_call(risky_operation, "Operation failed")
    if isinstance(safe_result, Failure):
        print(f"   ❌ Safely caught: {safe_result.error}")
    
    print("\n✨ Demo completed!")


if __name__ == "__main__":
    asyncio.run(simple_demo())
