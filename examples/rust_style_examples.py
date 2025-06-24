#!/usr/bin/env python3
"""
Example demonstrating Rust-like Ok/Err aliases for Python Result Type.

This shows how Rust developers can use familiar Ok/Err syntax instead of Success/Failure.
"""

from result_type import Ok, Err, ok, err, Success, Failure


def rust_style_examples():
    """Examples using Rust-like Ok/Err syntax."""
    print("=== Rust-style Examples ===")
    
    # Basic usage with Ok/Err
    def divide_rust_style(a: float, b: float):
        if b == 0:
            return Err("Division by zero")
        return Ok(a / b)
    
    # Test successful operation
    result = divide_rust_style(10, 2)
    if result.is_success():
        print(f"Success: {result.value}")  # Success: 5.0
    
    # Test failed operation
    result = divide_rust_style(10, 0)
    if result.is_failure():
        print(f"Error: {result.error}")  # Error: Division by zero
    
    # Chain operations using Rust-style
    def multiply_by_2_rust(x):
        return Ok(x * 2)
    
    def validate_positive_rust(x):
        if x > 0:
            return Ok(x)
        return Err("Number must be positive")
    
    # Chain operations
    result = (Ok(5)
              >> multiply_by_2_rust
              >> validate_positive_rust)
    
    if result.is_success():
        print(f"Chained result: {result.value}")  # Chained result: 10
    
    # Using helper functions
    success_result = ok(42)
    error_result = err("Something went wrong")
    
    print(f"ok(42): {success_result}")
    print(f"err('...'): {error_result}")


def mixed_style_examples():
    """Examples mixing Rust and traditional styles."""
    print("\n=== Mixed Style Examples ===")
    
    def process_with_success(x):
        return Success(x + 1)
    
    def process_with_ok(x):
        return Ok(x * 3)
    
    # Mix Ok and Success in chain
    result = Ok(5) >> process_with_success >> process_with_ok
    
    if result.is_success():
        print(f"Mixed chain result: {result.value}")  # Mixed chain result: 18
    
    # Demonstrate they are the same type
    ok_result = Ok("hello")
    success_result = Success("hello")
    
    print(f"Ok and Success are equal: {ok_result == success_result}")  # True
    print(f"Ok type: {type(ok_result).__name__}")  # Success
    print(f"Success type: {type(success_result).__name__}")  # Success


def error_handling_examples():
    """Examples of error handling with Rust-style syntax."""
    print("\n=== Error Handling Examples ===")
    
    # Unwrap operations
    ok_value = Ok(42)
    err_value = Err("oops")
    
    print(f"Ok unwrap: {ok_value.unwrap()}")  # 42
    print(f"Ok unwrap_or: {ok_value.unwrap_or(0)}")  # 42
    print(f"Err unwrap_or: {err_value.unwrap_or(0)}")  # 0
    
    # Map operations
    mapped_ok = ok_value.map(lambda x: x * 2)
    mapped_err = err_value.map(lambda x: x * 2)  # No-op on error
    
    print(f"Mapped Ok: {mapped_ok}")  # Success(84)
    print(f"Mapped Err: {mapped_err}")  # Failure('oops')
    
    # Error mapping
    mapped_error = err_value.map_error(lambda e: f"Prefix: {e}")
    print(f"Mapped error: {mapped_error}")  # Failure('Prefix: oops')


if __name__ == "__main__":
    rust_style_examples()
    mixed_style_examples()
    error_handling_examples()
