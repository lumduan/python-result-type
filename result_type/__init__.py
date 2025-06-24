"""
Python Result Type Library

A functional programming pattern for handling operations that can succeed or fail.
Inspired by Rust's Result<T, E> with intuitive Success/Failure naming.

For Rust developers, Ok/Err aliases are also available:
    >>> from result_type import Ok, Err
    >>> result = Ok(42)  # Same as Success(42)
    >>> error = Err("oops")  # Same as Failure("oops")

Basic Usage:
    >>> from result_type import Success, Failure, safe_call
    >>>
    >>> def divide(a: float, b: float):
    ...     if b == 0:
    ...         return Failure("Division by zero")
    ...     return Success(a / b)
    >>>
    >>> result = divide(10, 2)
    >>> if result.is_success():
    ...     print(f"Result: {result.value}")
    Result: 5.0

Chaining Operations:
    >>> def multiply_by_2(x: float):
    ...     return Success(x * 2)
    >>>
    >>> result = divide(10, 2) >> multiply_by_2
    >>> print(f"Chained result: {result.value}")
    Chained result: 10.0

Safe Function Calls:
    >>> result = safe_call(lambda: 10 / 0, "Math error")
    >>> print(f"Safe call: {result.error}")
    Safe call: Math error: division by zero
"""

from .core import (
    Err,
    Failure,
    Ok,
    Result,
    ResultType,
    Success,
    err,
    failure,
    ok,
    safe_call,
    safe_call_decorator,
    success,
)

# Import async functionality (optional)
try:
    from .async_result import (
        AsyncResult,
        async_safe_call,
        async_safe_call_decorator,
        async_success,
        async_failure,
        gather_results,
        gather_results_all_settled,
        from_awaitable,
    )
    _ASYNC_AVAILABLE = True
except ImportError:
    _ASYNC_AVAILABLE = False

__version__ = "1.2.0"
__author__ = "Sarat"
__email__ = "sarat@example.com"

__all__ = [
    "Result",
    "Success",
    "Failure",
    "ResultType",
    "success",
    "failure",
    "safe_call",
    "safe_call_decorator",
    # Rust-like aliases
    "Ok",
    "Err",
    "ok",
    "err",
]

# Add async exports if available
if _ASYNC_AVAILABLE:
    __all__.extend([
        "AsyncResult",
        "async_safe_call",
        "async_safe_call_decorator",
        "async_success",
        "async_failure",
        "gather_results",
        "gather_results_all_settled",
        "from_awaitable",
    ])
