"""
Async support for Python Result Type Library

Provides async/await compatible Result operations for modern Python applications.
Includes AsyncResult wrapper and async utility functions.

Example:
    >>> import asyncio
    >>> from result_type.async_result import async_safe_call, AsyncResult
    >>> 
    >>> async def fetch_data(url: str) -> Result[dict, str]:
    ...     # Simulated async operation
    ...     await asyncio.sleep(0.1)
    ...     if url.startswith("https://"):
    ...         return Success({"data": "fetched"})
    ...     return Failure("Invalid URL")
    >>> 
    >>> async def process_data(data: dict) -> Result[str, str]:
    ...     await asyncio.sleep(0.1)
    ...     return Success(f"Processed: {data}")
    >>> 
    >>> # Chain async operations
    >>> async def main():
    ...     result = await AsyncResult(fetch_data("https://api.example.com")).then_async(process_data)
    ...     print(await result.resolve())
"""

import asyncio
from typing import Any, Awaitable, Callable, Generic, TypeVar, Union, Optional, List, Generator
from .core import Result, Success, Failure, T, E, U


class AsyncResult(Generic[T, E]):
    """
    Wrapper for async Result operations.
    
    Allows chaining of async operations that return Results,
    making it easy to work with async functions in a functional style.
    """
    
    def __init__(self, result: Union[Result[T, E], Awaitable[Result[T, E]]]):
        """
        Create an AsyncResult from a Result or awaitable Result.
        
        Args:
            result: Either a Result or an awaitable that yields a Result
        """
        self._result = result
    
    async def resolve(self) -> Result[T, E]:
        """
        Resolve the async operation to get the actual Result.
        
        Returns:
            The resolved Result[T, E]
        """
        if asyncio.iscoroutine(self._result) or hasattr(self._result, '__await__'):
            return await self._result
        return self._result
    
    def then_async(self, func: Callable[[T], Awaitable[Result[U, E]]]) -> 'AsyncResult[U, E]':
        """
        Chain an async operation that can fail.
        
        If the current result is Success, applies the async func to the value.
        If the current result is Failure, returns the failure unchanged.
        
        Args:
            func: Async function that takes success value and returns awaitable Result
            
        Returns:
            New AsyncResult with transformed value or original failure
        """
        async def _chain() -> Result[U, E]:
            result = await self.resolve()
            
            if isinstance(result, Success):
                try:
                    new_result = await func(result.value)
                    return new_result
                except Exception as e:
                    return Failure(str(e))  # type: ignore
            else:
                return result  # type: ignore
        
        return AsyncResult(_chain())
    
    def then_sync(self, func: Callable[[T], Result[U, E]]) -> 'AsyncResult[U, E]':
        """
        Chain a synchronous operation that can fail.
        
        Args:
            func: Sync function that takes success value and returns Result
            
        Returns:
            New AsyncResult with transformed value or original failure
        """
        async def _chain() -> Result[U, E]:
            result = await self.resolve()
            
            if isinstance(result, Success):
                try:
                    new_result = func(result.value)
                    return new_result
                except Exception as e:
                    return Failure(str(e))  # type: ignore
            else:
                return result  # type: ignore
        
        return AsyncResult(_chain())
    
    def map_async(self, func: Callable[[T], Awaitable[U]]) -> 'AsyncResult[U, E]':
        """
        Transform the success value using an async function.
        
        Args:
            func: Async function that transforms the success value
            
        Returns:
            New AsyncResult with transformed value or original failure
        """
        async def _map() -> Result[U, E]:
            result = await self.resolve()
            
            if isinstance(result, Success):
                try:
                    new_value = await func(result.value)
                    return Success(new_value)
                except Exception as e:
                    return Failure(str(e))  # type: ignore
            else:
                return result  # type: ignore
        
        return AsyncResult(_map())
    
    def map_sync(self, func: Callable[[T], U]) -> 'AsyncResult[U, E]':
        """
        Transform the success value using a sync function.
        
        Args:
            func: Sync function that transforms the success value
            
        Returns:
            New AsyncResult with transformed value or original failure
        """
        async def _map() -> Result[U, E]:
            result = await self.resolve()
            
            if isinstance(result, Success):
                try:
                    new_value = func(result.value)
                    return Success(new_value)
                except Exception as e:
                    return Failure(str(e))  # type: ignore
            else:
                return result  # type: ignore
        
        return AsyncResult(_map())
    
    async def map_error_async(self, func: Callable[[E], Awaitable[Any]]) -> 'AsyncResult[T, Any]':
        """
        Transform the failure value using an async function.
        
        Args:
            func: Async function that transforms the error value
            
        Returns:
            New AsyncResult with original value or transformed error
        """
        result = await self.resolve()
        
        if isinstance(result, Failure):
            try:
                new_error = await func(result.error)
                return AsyncResult(Failure(new_error))
            except Exception as e:
                return AsyncResult(Failure(str(e)))
        else:
            return AsyncResult(result)  # type: ignore
    
    async def unwrap_async(self) -> T:
        """
        Async version of unwrap - get the success value or raise exception.
        
        Returns:
            The success value
            
        Raises:
            RuntimeError: If the result is a Failure
        """
        result = await self.resolve()
        return result.unwrap()
    
    async def unwrap_or_async(self, default: T) -> T:
        """
        Async version of unwrap_or - get success value or return default.
        
        Args:
            default: Default value to return if result is Failure
            
        Returns:
            Success value or default
        """
        result = await self.resolve()
        return result.unwrap_or(default)
    
    async def unwrap_or_else_async(self, func: Callable[[E], Union[T, Awaitable[T]]]) -> T:
        """
        Async version of unwrap_or_else - compute value from error.
        
        Args:
            func: Function to compute value from error (can be sync or async)
            
        Returns:
            Success value or computed value from error
        """
        result = await self.resolve()
        
        if isinstance(result, Success):
            return result.value
        else:
            try:
                computed = func(result.error)
                if asyncio.iscoroutine(computed) or hasattr(computed, '__await__'):
                    return await computed
                return computed
            except Exception as e:
                raise RuntimeError(f"Error in unwrap_or_else_async: {e}")
    
    def __await__(self) -> Generator[Any, None, Result[T, E]]:
        """Allow AsyncResult to be awaited directly."""
        return self.resolve().__await__()


# Async utility functions

async def async_safe_call(
    func: Callable[[], Awaitable[T]], 
    error_msg: Optional[str] = None
) -> Result[T, str]:
    """
    Safely call an async function that might raise an exception.
    
    Args:
        func: Async function to call safely
        error_msg: Custom error message prefix
        
    Returns:
        Success with return value or Failure with error message
    """
    try:
        result = await func()
        return Success(result)
    except Exception as e:
        error_text = f"{error_msg}: {e}" if error_msg else str(e)
        return Failure(error_text)


def async_safe_call_decorator(error_msg: Optional[str] = None) -> Callable[[Callable[[], Awaitable[T]]], Callable[[], Awaitable[Result[T, str]]]]:
    """
    Decorator for safely calling async functions that might raise exceptions.
    
    Usage:
        @async_safe_call_decorator("API error")
        async def fetch_data():
            # might throw exception
            return await some_async_operation()
    """
    def decorator(func: Callable[[], Awaitable[T]]) -> Callable[[], Awaitable[Result[T, str]]]:
        async def wrapper() -> Result[T, str]:
            return await async_safe_call(func, error_msg)
        return wrapper
    return decorator


async def gather_results(*async_results: AsyncResult[T, E]) -> Result[List[T], E]:
    """
    Gather multiple AsyncResults and return Success with list of values,
    or the first Failure encountered.
    
    Args:
        *async_results: Multiple AsyncResult instances
        
    Returns:
        Success with list of all values, or first Failure
    """
    results = await asyncio.gather(
        *[ar.resolve() for ar in async_results],
        return_exceptions=True
    )
    
    values = []
    for result in results:
        if isinstance(result, Exception):
            return Failure(str(result))  # type: ignore
        elif isinstance(result, Failure):
            return result
        elif isinstance(result, Success):
            values.append(result.value)
    
    return Success(values)


async def gather_results_all_settled(*async_results: AsyncResult[T, E]) -> List[Result[T, E]]:
    """
    Gather multiple AsyncResults and return all results (both successes and failures).
    
    Args:
        *async_results: Multiple AsyncResult instances
        
    Returns:
        List of all Results, preserving order
    """
    return await asyncio.gather(
        *[ar.resolve() for ar in async_results],
        return_exceptions=False
    )


# Helper functions for creating AsyncResults

def async_success(value: T) -> AsyncResult[T, Any]:
    """Create an AsyncResult with a Success value."""
    return AsyncResult(Success(value))


def async_failure(error: E) -> AsyncResult[Any, E]:
    """Create an AsyncResult with a Failure error."""
    return AsyncResult(Failure(error))


async def from_awaitable(awaitable: Awaitable[T], error_msg: Optional[str] = None) -> AsyncResult[T, str]:
    """
    Convert an awaitable to an AsyncResult, handling exceptions.
    
    Args:
        awaitable: Any awaitable object
        error_msg: Custom error message prefix for exceptions
        
    Returns:
        AsyncResult wrapping the awaitable result
    """
    try:
        result = await awaitable
        return AsyncResult(Success(result))
    except Exception as e:
        error_text = f"{error_msg}: {e}" if error_msg else str(e)
        return AsyncResult(Failure(error_text))
