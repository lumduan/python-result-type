"""
Python Result Type Library

A functional programming pattern for handling operations that can succeed or fail,
inspired by Rust's Result<T, E> and similar to PyMonad's Either but with
more intuitive naming (Success/Failure instead of Right/Left).

Example:
    >>> from result_type import Success, Failure, safe_call
    >>> 
    >>> def divide(a: float, b: float) -> Result[float, str]:
    ...     if b == 0:
    ...         return Failure("Division by zero")
    ...     return Success(a / b)
    >>> 
    >>> def multiply_by_2(x: float) -> Result[float, str]:
    ...     return Success(x * 2)
    >>> 
    >>> # Chain operations
    >>> result = divide(10, 2) >> multiply_by_2
    >>> if result.is_success():
    ...     print(f"Result: {result.value}")
    ... else:
    ...     print(f"Error: {result.error}")
    Result: 10.0
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar, Union

# Type variables for generic typing
T = TypeVar('T')  # Success value type
E = TypeVar('E')  # Error/Failure type
U = TypeVar('U')  # Return type for transformations


class Result(Generic[T, E], ABC):
    """
    Abstract base class for Result type.
    
    A Result represents the outcome of an operation that can either succeed
    with a value of type T, or fail with an error of type E.
    """
    
    @abstractmethod
    def is_success(self) -> bool:
        """Check if this Result is a Success."""
        pass
    
    @abstractmethod
    def is_failure(self) -> bool:
        """Check if this Result is a Failure."""
        pass
    
    @abstractmethod
    def then(self, func: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """
        Chain operations that can fail.
        
        If this Result is Success, applies func to the value.
        If this Result is Failure, returns the failure unchanged.
        
        Args:
            func: Function that takes success value and returns a new Result
            
        Returns:
            New Result with transformed value or original failure
        """
        pass
    
    @abstractmethod
    def map(self, func: Callable[[T], U]) -> 'Result[U, E]':
        """
        Transform the success value without changing failure behavior.
        
        If this Result is Success, applies func to the value and wraps in Success.
        If this Result is Failure, returns the failure unchanged.
        
        Args:
            func: Function that transforms the success value
            
        Returns:
            New Result with transformed value or original failure
        """
        pass
    
    @abstractmethod
    def map_error(self, func: Callable[[E], Any]) -> 'Result[T, Any]':
        """
        Transform the failure value without changing success behavior.
        
        If this Result is Failure, applies func to the error value.
        If this Result is Success, returns the success unchanged.
        
        Args:
            func: Function that transforms the error value
            
        Returns:
            New Result with original value or transformed error
        """
        pass
    
    @abstractmethod
    def unwrap(self) -> T:
        """
        Extract the success value or raise an exception.
        
        Returns:
            The success value if this is Success
            
        Raises:
            RuntimeError: If this is a Failure
        """
        pass
    
    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """
        Extract the success value or return a default.
        
        Args:
            default: Value to return if this is Failure
            
        Returns:
            The success value or the default value
        """
        pass
    
    @abstractmethod
    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """
        Extract the success value or compute from error.
        
        Args:
            func: Function that computes a value from the error
            
        Returns:
            The success value or computed value from error
        """
        pass
    
    def __rshift__(self, func: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """
        Operator overload for >> to enable chaining syntax.
        
        This allows: result >> function instead of result.then(function)
        
        Args:
            func: Function that takes success value and returns a new Result
            
        Returns:
            New Result with transformed value or original failure
        """
        return self.then(func)
    

class Success(Result[T, E]):
    """
    Represents a successful result containing a value.
    """
    
    def __init__(self, value: T):
        self.value = value
    
    def is_success(self) -> bool:
        return True
    
    def is_failure(self) -> bool:
        return False
    
    def then(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Apply function to success value, returning new Result."""
        try:
            return func(self.value)
        except Exception as e:
            # If function throws, convert to Failure
            return Failure(e)  # type: ignore
    
    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        """Transform success value, wrapping result in Success."""
        try:
            return Success(func(self.value))
        except Exception as e:
            # If function throws, convert to Failure
            return Failure(e)  # type: ignore
    
    def map_error(self, func: Callable[[E], Any]) -> Result[T, Any]:
        """No-op for Success - returns self unchanged."""
        return self
    
    def unwrap(self) -> T:
        """Return the success value."""
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """Return the success value (ignoring default)."""
        return self.value
    
    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Return the success value (ignoring function)."""
        return self.value
    
    def __repr__(self) -> str:
        return f"Success({self.value!r})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Success) and self.value == other.value


class Failure(Result[T, E]):
    """
    Represents a failed result containing an error.
    """
    
    def __init__(self, error: E):
        self.error = error
    
    def is_success(self) -> bool:
        return False
    
    def is_failure(self) -> bool:
        return True
    
    def then(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """No-op for Failure - returns self unchanged."""
        return self  # type: ignore
    
    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        """No-op for Failure - returns self unchanged."""
        return self  # type: ignore
    
    def map_error(self, func: Callable[[E], Any]) -> Result[T, Any]:
        """Transform error value, wrapping result in Failure."""
        try:
            return Failure(func(self.error))
        except Exception as e:
            # If function throws, return new failure with exception
            return Failure(str(e))
    
    def unwrap(self) -> T:
        """Raise exception with error information."""
        raise RuntimeError(f"Called unwrap on Failure: {self.error}")
    
    def unwrap_or(self, default: T) -> T:
        """Return the default value."""
        return default
    
    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Compute value from error using provided function."""
        try:
            return func(self.error)
        except Exception as e:
            # If function throws, we need to handle it somehow
            # Since we must return T, we'll re-raise
            raise RuntimeError(f"Error in unwrap_or_else: {e}")
    
    def __repr__(self) -> str:
        return f"Failure({self.error!r})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Failure) and self.error == other.error


# Type alias for convenience
ResultType = Union[Success[T, E], Failure[T, E]]


# Helper functions for creating Results
def success(value: T) -> Success[T, Any]:
    """Create a Success result."""
    return Success(value)


def failure(error: E) -> Failure[Any, E]:
    """Create a Failure result."""
    return Failure(error)


def safe_call(func: Callable[[], T], error_msg: str | None = None) -> Result[T, str]:
    """
    Safely call a function that might raise an exception.
    
    Args:
        func: Function to call safely
        error_msg: Custom error message prefix
        
    Returns:
        Success with return value or Failure with error message
    """
    try:
        result = func()
        return Success(result)
    except Exception as e:
        error_text = f"{error_msg}: {e}" if error_msg else str(e)
        return Failure(error_text)


def safe_call_decorator(error_msg: str | None = None):
    """
    Decorator for safely calling functions that might raise exceptions.
    
    Usage:
        @safe_call_decorator("Database error")
        def risky_operation():
            # might throw exception
            return some_value
    """
    def decorator(func: Callable[[], T]) -> Callable[[], Result[T, str]]:
        def wrapper() -> Result[T, str]:
            return safe_call(func, error_msg)
        return wrapper
    return decorator
