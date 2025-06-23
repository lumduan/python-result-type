#!/usr/bin/env python3
"""
Async examples for the python-result-type library.
"""

import asyncio
from result_type import Success, Failure, Result
from result_type.async_result import (
    AsyncResult, 
    async_safe_call, 
    async_safe_call_decorator,
    gather_results,
    from_awaitable
)


async def example_basic_async():
    """Demonstrate basic async Result usage."""
    print("=== Basic Async Usage Example ===")
    
    async def fetch_user(user_id: int) -> Result[dict, str]:
        """Simulate fetching user data from API."""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        if user_id <= 0:
            return Failure("Invalid user ID")
        if user_id == 404:
            return Failure("User not found")
        
        return Success({
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com"
        })
    
    # Successful case
    result = await fetch_user(123)
    if result.is_success():
        print(f"✅ Found user: {result.value['name']}")
    
    # Failure case
    result = await fetch_user(404)
    if result.is_failure():
        print(f"❌ Error: {result.error}")
    
    print()


async def example_async_chaining():
    """Demonstrate chaining async operations."""
    print("=== Async Chaining Example ===")
    
    async def fetch_user(user_id: int) -> Result[dict, str]:
        await asyncio.sleep(0.1)
        if user_id <= 0:
            return Failure("Invalid user ID")
        return Success({"id": user_id, "name": f"User {user_id}"})
    
    async def fetch_user_posts(user: dict) -> Result[list, str]:
        await asyncio.sleep(0.1)
        if user["id"] == 999:
            return Failure("Posts service unavailable")
        return Success([f"Post {i} by {user['name']}" for i in range(1, 4)])
    
    async def format_user_summary(posts: list) -> Result[str, str]:
        await asyncio.sleep(0.05)
        if not posts:
            return Failure("No posts to summarize")
        return Success(f"User has {len(posts)} posts: {', '.join(posts[:2])}...")
    
    # Successful chain
    async_result = AsyncResult(fetch_user(123))
    result = await (async_result
                    .then_async(fetch_user_posts)
                    .then_async(format_user_summary))
    
    final_result = await result.resolve()
    if final_result.is_success():
        print(f"✅ Summary: {final_result.value}")
    else:
        print(f"❌ Error: {final_result.error}")
    
    # Failed chain (user not found)
    async_result = AsyncResult(fetch_user(-1))
    result = await (async_result
                    .then_async(fetch_user_posts)
                    .then_async(format_user_summary))
    
    final_result = await result.resolve()
    if final_result.is_failure():
        print(f"❌ Chain failed: {final_result.error}")
    
    print()


async def example_async_safe_call():
    """Demonstrate async safe_call functionality."""
    print("=== Async Safe Call Example ===")
    
    async def risky_operation():
        """Operation that might fail."""
        await asyncio.sleep(0.1)
        import random
        if random.random() < 0.5:
            raise ValueError("Random failure occurred")
        return "Operation successful!"
    
    # Using async_safe_call
    result = await async_safe_call(risky_operation, "API Error")
    if result.is_success():
        print(f"✅ Success: {result.value}")
    else:
        print(f"❌ Caught error: {result.error}")
    
    # Using decorator
    @async_safe_call_decorator("Database Error")
    async def database_operation():
        await asyncio.sleep(0.1)
        # Simulate a database error
        raise ConnectionError("Database connection failed")
    
    result = await database_operation()
    if result.is_failure():
        print(f"❌ Database error: {result.error}")
    
    print()


async def example_gather_results():
    """Demonstrate gathering multiple async results."""
    print("=== Gather Results Example ===")
    
    async def fetch_data(source: str, delay: float) -> Result[str, str]:
        await asyncio.sleep(delay)
        if source == "error_source":
            return Failure(f"Failed to fetch from {source}")
        return Success(f"Data from {source}")
    
    # Create multiple async operations
    async_results = [
        AsyncResult(fetch_data("source1", 0.1)),
        AsyncResult(fetch_data("source2", 0.2)),
        AsyncResult(fetch_data("source3", 0.15)),
    ]
    
    # Gather all results - stops at first failure
    combined_result = await gather_results(*async_results)
    if combined_result.is_success():
        print(f"✅ All succeeded: {combined_result.value}")
    else:
        print(f"❌ First failure: {combined_result.error}")
    
    # Test with one failure
    async_results_with_failure = [
        AsyncResult(fetch_data("source1", 0.1)),
        AsyncResult(fetch_data("error_source", 0.2)),
        AsyncResult(fetch_data("source3", 0.15)),
    ]
    
    combined_result = await gather_results(*async_results_with_failure)
    if combined_result.is_failure():
        print(f"❌ Failed as expected: {combined_result.error}")
    
    print()


async def example_mixed_sync_async():
    """Demonstrate mixing sync and async operations."""
    print("=== Mixed Sync/Async Example ===")
    
    async def fetch_raw_data(source: str) -> Result[str, str]:
        await asyncio.sleep(0.1)
        return Success(f"raw_data_from_{source}")
    
    def process_data_sync(data: str) -> Result[dict, str]:
        # Synchronous processing
        if "error" in data:
            return Failure("Processing failed")
        return Success({"processed": data.upper(), "length": len(data)})
    
    async def save_data_async(processed_data: dict) -> Result[str, str]:
        await asyncio.sleep(0.1)
        return Success(f"Saved: {processed_data['processed']}")
    
    # Mix sync and async operations
    async_result = AsyncResult(fetch_raw_data("api"))
    result = await (async_result
                    .then_sync(process_data_sync)  # Sync operation
                    .then_async(save_data_async))  # Async operation
    
    final_result = await result.resolve()
    if final_result.is_success():
        print(f"✅ Pipeline completed: {final_result.value}")
    else:
        print(f"❌ Pipeline failed: {final_result.error}")
    
    print()


async def example_from_awaitable():
    """Demonstrate converting regular awaitables to AsyncResult."""
    print("=== From Awaitable Example ===")
    
    async def regular_async_function():
        await asyncio.sleep(0.1)
        return {"status": "completed", "data": [1, 2, 3]}
    
    async def failing_async_function():
        await asyncio.sleep(0.1)
        raise ValueError("Something went wrong")
    
    # Convert successful awaitable
    async_result = await from_awaitable(regular_async_function())
    result = await async_result.resolve()
    if result.is_success():
        print(f"✅ Converted success: {result.value}")
    
    # Convert failing awaitable
    async_result = await from_awaitable(failing_async_function(), "External API")
    result = await async_result.resolve()
    if result.is_failure():
        print(f"❌ Converted failure: {result.error}")
    
    print()


async def main():
    """Run all async examples."""
    print("🚀 Python Result Type - Async Examples\n")
    
    await example_basic_async()
    await example_async_chaining()
    await example_async_safe_call()
    await example_gather_results()
    await example_mixed_sync_async()
    await example_from_awaitable()
    
    print("✨ All async examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
