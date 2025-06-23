#!/usr/bin/env python3
"""
Basic examples of using the python-result-type library.
"""

from result_type import Failure, Result, Success, safe_call


def example_basic_usage():
    """Demonstrate basic Success and Failure usage."""
    print("=== Basic Usage Example ===")
    
    def divide(a: float, b: float) -> Result[float, str]:
        if b == 0:
            return Failure("Division by zero")
        return Success(a / b)
    
    # Success case
    result = divide(10, 2)
    if result.is_success():
        print(f"✅ Success: {result.value}")
    
    # Failure case
    result = divide(10, 0)
    if result.is_failure():
        print(f"❌ Failure: {result.error}")
    
    print()


def example_chaining():
    """Demonstrate chaining operations."""
    print("=== Chaining Operations Example ===")
    
    def divide(a: float, b: float) -> Result[float, str]:
        if b == 0:
            return Failure("Division by zero")
        return Success(a / b)
    
    def multiply_by_2(x: float) -> Result[float, str]:
        return Success(x * 2)
    
    def subtract_1(x: float) -> Result[float, str]:
        if x < 1:
            return Failure("Result would be negative")
        return Success(x - 1)
    
    # Successful chain
    result = (
        divide(10, 2)
        .then(multiply_by_2)
        .then(subtract_1)
        .map(lambda x: x + 5)
    )
    
    if result.is_success():
        print(f"✅ Chained result: {result.value}")  # Should be 14.0
    
    # Chain with >> operator
    result2 = divide(10, 2) >> multiply_by_2 >> subtract_1
    
    if result2.is_success():
        print(f"✅ Operator chained result: {result2.value}")  # Should be 9.0
    
    # Chain that fails
    result3 = divide(10, 0) >> multiply_by_2 >> subtract_1
    
    if result3.is_failure():
        print(f"❌ Failed chain: {result3.error}")
    
    print()


def example_safe_calls():
    """Demonstrate safe function calling."""
    print("=== Safe Function Calls Example ===")
    
    # Using safe_call
    result = safe_call(lambda: 10 / 2)
    if result.is_success():
        print(f"✅ Safe division: {result.value}")
    
    # Safe call that fails
    result = safe_call(lambda: 10 / 0, "Math error")
    if result.is_failure():
        print(f"❌ Safe call error: {result.error}")
    
    print()


def example_real_world():
    """Real-world example with user validation."""
    print("=== Real-World Example: User Validation ===")
    
    def fetch_user(user_id: str) -> Result[dict, str]:
        """Simulate fetching user from database."""
        users_db = {
            "user1": {"name": "John", "age": 30, "is_active": True},
            "user2": {"name": "Jane", "age": 25, "is_active": False},
        }
        
        if user_id not in users_db:
            return Failure("User not found")
        return Success(users_db[user_id])
    
    def validate_user(user: dict) -> Result[dict, str]:
        """Validate user is active."""
        if not user.get("is_active"):
            return Failure("User is inactive")
        return Success(user)
    
    def get_user_permissions(user: dict) -> Result[list, str]:
        """Get user permissions."""
        # Simulate permissions lookup
        permissions = ["read", "write"] if user["age"] >= 25 else ["read"]
        return Success(permissions)
    
    # Successful flow
    result = (
        fetch_user("user1")
        >> validate_user
        >> get_user_permissions
    )
    
    if result.is_success():
        print(f"✅ User permissions: {result.value}")
    
    # Failed flow - inactive user
    result = (
        fetch_user("user2")
        >> validate_user
        >> get_user_permissions
    )
    
    if result.is_failure():
        print(f"❌ Validation failed: {result.error}")
    
    # Failed flow - user not found
    result = (
        fetch_user("user999")
        >> validate_user
        >> get_user_permissions
    )
    
    if result.is_failure():
        print(f"❌ User lookup failed: {result.error}")
    
    print()


def example_error_recovery():
    """Demonstrate error recovery patterns."""
    print("=== Error Recovery Example ===")
    
    def risky_operation(x: int) -> Result[int, str]:
        if x < 0:
            return Failure("Negative input")
        if x == 0:
            return Failure("Zero input")
        return Success(x * 2)
    
    def fallback_operation(error: str) -> int:
        print(f"🔄 Recovering from error: {error}")
        return 42  # Default value
    
    # Using unwrap_or for recovery
    result = risky_operation(-5)
    value = result.unwrap_or(0)
    print(f"✅ Recovered value: {value}")
    
    # Using unwrap_or_else for computed recovery
    result = risky_operation(-5)
    value = result.unwrap_or_else(fallback_operation)
    print(f"✅ Computed recovery value: {value}")
    
    print()


if __name__ == "__main__":
    example_basic_usage()
    example_chaining()
    example_safe_calls()
    example_real_world()
    example_error_recovery()
    
    print("🎉 All examples completed!")
