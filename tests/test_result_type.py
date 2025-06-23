"""
Comprehensive tests for the Result type library.
"""

import pytest
from result_type import (
    Failure,
    Result,
    Success,
    failure,
    safe_call,
    safe_call_decorator,
    success,
)


class TestSuccessType:
    """Test Success type functionality."""
    
    def test_success_creation(self):
        """Test creating Success instances."""
        result = Success(42)
        assert result.value == 42
        assert result.is_success()
        assert not result.is_failure()
    
    def test_success_helper(self):
        """Test success helper function."""
        result = success(42)
        assert isinstance(result, Success)
        assert result.value == 42
    
    def test_success_unwrap(self):
        """Test unwrapping success values."""
        result = Success(42)
        assert result.unwrap() == 42
        assert result.unwrap_or(0) == 42
        assert result.unwrap_or_else(lambda _: 0) == 42
    
    def test_success_map(self):
        """Test mapping over success values."""
        result = Success(42)
        mapped = result.map(lambda x: x * 2)
        
        assert isinstance(mapped, Success)
        assert mapped.value == 84
    
    def test_success_map_error(self):
        """Test map_error on Success (should be no-op)."""
        result = Success(42)
        mapped = result.map_error(lambda x: f"Error: {x}")
        
        assert mapped is result  # Should return self unchanged
    
    def test_success_then(self):
        """Test chaining with then method."""
        result = Success(42)
        chained = result.then(lambda x: Success(x * 2))
        
        assert isinstance(chained, Success)
        assert chained.value == 84
    
    def test_success_then_to_failure(self):
        """Test chaining that results in failure."""
        result = Success(42)
        chained = result.then(lambda x: Failure("Something went wrong"))
        
        assert isinstance(chained, Failure)
        assert chained.error == "Something went wrong"
    
    def test_success_rshift_operator(self):
        """Test >> operator for chaining."""
        result = Success(42)
        chained = result >> (lambda x: Success(x * 2))
        
        assert isinstance(chained, Success)
        assert chained.value == 84
    
    def test_success_equality(self):
        """Test Success equality."""
        result1 = Success(42)
        result2 = Success(42)
        result3 = Success(43)
        
        assert result1 == result2
        assert result1 != result3
        assert result1 != Failure("error")
    
    def test_success_repr(self):
        """Test Success string representation."""
        result = Success(42)
        assert repr(result) == "Success(42)"


class TestFailureType:
    """Test Failure type functionality."""
    
    def test_failure_creation(self):
        """Test creating Failure instances."""
        result = Failure("error message")
        assert result.error == "error message"
        assert not result.is_success()
        assert result.is_failure()
    
    def test_failure_helper(self):
        """Test failure helper function."""
        result = failure("error message")
        assert isinstance(result, Failure)
        assert result.error == "error message"
    
    def test_failure_unwrap(self):
        """Test unwrapping failure values."""
        result = Failure("error message")
        
        with pytest.raises(RuntimeError, match="Called unwrap on Failure"):
            result.unwrap()
        
        assert result.unwrap_or(42) == 42
        assert result.unwrap_or_else(lambda _: 42) == 42
    
    def test_failure_map(self):
        """Test mapping over failure values (should be no-op)."""
        result = Failure("error")
        mapped = result.map(lambda x: x * 2)
        
        assert mapped is result  # Should return self unchanged
    
    def test_failure_map_error(self):
        """Test map_error on Failure."""
        result = Failure("error")
        mapped = result.map_error(lambda x: f"Transformed: {x}")
        
        assert isinstance(mapped, Failure)
        assert mapped.error == "Transformed: error"
    
    def test_failure_then(self):
        """Test chaining with then method (should be no-op)."""
        result = Failure("error")
        chained = result.then(lambda x: Success(x * 2))
        
        assert chained is result  # Should return self unchanged
    
    def test_failure_rshift_operator(self):
        """Test >> operator for chaining (should be no-op)."""
        result = Failure("error")
        chained = result >> (lambda x: Success(x * 2))
        
        assert chained is result  # Should return self unchanged
    
    def test_failure_equality(self):
        """Test Failure equality."""
        result1 = Failure("error")
        result2 = Failure("error")
        result3 = Failure("different error")
        
        assert result1 == result2
        assert result1 != result3
        assert result1 != Success(42)
    
    def test_failure_repr(self):
        """Test Failure string representation."""
        result = Failure("error message")
        assert repr(result) == "Failure('error message')"


class TestChaining:
    """Test chaining operations."""
    
    def divide(self, a: float, b: float) -> Result[float, str]:
        """Helper function for testing."""
        if b == 0:
            return Failure("Division by zero")
        return Success(a / b)
    
    def multiply_by_2(self, x: float) -> Result[float, str]:
        """Helper function for testing."""
        return Success(x * 2)
    
    def subtract_1(self, x: float) -> Result[float, str]:
        """Helper function for testing."""
        if x < 1:
            return Failure("Result would be negative")
        return Success(x - 1)
    
    def test_successful_chain(self):
        """Test chaining successful operations."""
        result = (
            self.divide(10, 2)
            .then(self.multiply_by_2)
            .then(self.subtract_1)
            .map(lambda x: x + 5)
        )
        
        assert result.is_success()
        assert result.value == 14.0  # ((10/2) * 2 - 1) + 5 = 14
    
    def test_chain_with_failure(self):
        """Test chaining with failure in the middle."""
        result = (
            self.divide(10, 0)  # This fails
            .then(self.multiply_by_2)
            .then(self.subtract_1)
            .map(lambda x: x + 5)
        )
        
        assert result.is_failure()
        assert result.error == "Division by zero"
    
    def test_chain_with_rshift_operator(self):
        """Test chaining with >> operator."""
        result = (
            self.divide(10, 2) >> self.multiply_by_2 >> self.subtract_1
        )
        
        assert result.is_success()
        assert result.value == 9.0  # (10/2) * 2 - 1 = 9
    
    def test_mixed_chaining(self):
        """Test mixing .then() and >> operator."""
        result = (
            self.divide(10, 2)
            >> self.multiply_by_2
        ).map(lambda x: x + 1) >> self.subtract_1
        
        assert result.is_success()
        assert result.value == 10.0  # ((10/2) * 2 + 1) - 1 = 10


class TestSafeCalls:
    """Test safe function calling utilities."""
    
    def test_safe_call_success(self):
        """Test safe_call with successful function."""
        result = safe_call(lambda: 42 / 2)
        
        assert result.is_success()
        assert result.value == 21.0
    
    def test_safe_call_failure(self):
        """Test safe_call with failing function."""
        result = safe_call(lambda: 42 / 0)
        
        assert result.is_failure()
        assert "division by zero" in result.error
    
    def test_safe_call_with_custom_error(self):
        """Test safe_call with custom error message."""
        result = safe_call(lambda: 42 / 0, "Math error")
        
        assert result.is_failure()
        assert result.error.startswith("Math error:")
        assert "division by zero" in result.error
    
    def test_safe_call_decorator(self):
        """Test safe_call_decorator."""
        @safe_call_decorator("Computation error")
        def risky_computation():
            return 42 / 0
        
        result = risky_computation()
        
        assert result.is_failure()
        assert result.error.startswith("Computation error:")
    
    def test_safe_call_decorator_success(self):
        """Test safe_call_decorator with successful function."""
        @safe_call_decorator("Computation error")
        def safe_computation():
            return 42 * 2
        
        result = safe_computation()
        
        assert result.is_success()
        assert result.value == 84


class TestExceptionHandling:
    """Test exception handling in Result operations."""
    
    def test_map_exception_handling(self):
        """Test that exceptions in map are handled."""
        result = Success(42)
        mapped = result.map(lambda x: x / 0)  # This will raise ZeroDivisionError
        
        assert mapped.is_failure()
        assert isinstance(mapped.error, ZeroDivisionError)
    
    def test_then_exception_handling(self):
        """Test that exceptions in then are handled."""
        result = Success(42)
        chained = result.then(lambda x: Success(x / 0))  # This will raise ZeroDivisionError
        
        assert chained.is_failure()
        assert isinstance(chained.error, ZeroDivisionError)
    
    def test_map_error_exception_handling(self):
        """Test that exceptions in map_error are handled."""
        result = Failure("original error")
        mapped = result.map_error(lambda x: x / 0)  # This will raise TypeError
        
        assert mapped.is_failure()
        # Should return new failure with exception message as string
        assert "unsupported operand type" in mapped.error.lower()


class TestTypeAnnotations:
    """Test that type annotations work correctly."""
    
    def test_result_type_annotation(self):
        """Test that Result type annotations work."""
        def typed_divide(a: float, b: float) -> Result[float, str]:
            if b == 0:
                return Failure("Division by zero")
            return Success(a / b)
        
        success_result = typed_divide(10, 2)
        failure_result = typed_divide(10, 0)
        
        assert success_result.is_success()
        assert failure_result.is_failure()
    
    def test_chaining_preserves_types(self):
        """Test that chaining preserves type information."""
        def int_to_string(x: int) -> Result[str, str]:
            return Success(str(x))
        
        def string_length(s: str) -> Result[int, str]:
            return Success(len(s))
        
        result = Success(42) >> int_to_string >> string_length
        
        assert result.is_success()
        assert result.value == 2  # Length of "42"


class TestEdgeCases:
    """Test edge cases and corner scenarios."""
    
    def test_none_values(self):
        """Test handling of None values."""
        success_none = Success(None)
        failure_none = Failure(None)
        
        assert success_none.is_success()
        assert success_none.value is None
        
        assert failure_none.is_failure()
        assert failure_none.error is None
    
    def test_empty_string_values(self):
        """Test handling of empty strings."""
        success_empty = Success("")
        failure_empty = Failure("")
        
        assert success_empty.is_success()
        assert success_empty.value == ""
        
        assert failure_empty.is_failure()
        assert failure_empty.error == ""
    
    def test_complex_objects(self):
        """Test handling of complex objects."""
        class CustomObject:
            def __init__(self, value):
                self.value = value
            
            def __eq__(self, other):
                return isinstance(other, CustomObject) and self.value == other.value
        
        obj = CustomObject(42)
        result = Success(obj)
        
        assert result.is_success()
        assert result.value.value == 42
        
        # Test equality with complex objects
        other_result = Success(CustomObject(42))
        assert result == other_result


if __name__ == "__main__":
    pytest.main([__file__])
