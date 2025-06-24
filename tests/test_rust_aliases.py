"""
Test Rust-like aliases Ok and Err for Success and Failure.
"""

import pytest

from result_type import Err, Failure, Ok, Result, Success, err, ok


class TestRustAliases:
    """Test Rust-like aliases for Result types."""

    def test_ok_is_alias_for_success(self) -> None:
        """Test that Ok is the same as Success."""
        ok_result = Ok(42)
        success_result = Success(42)
        
        assert type(ok_result) is type(success_result)
        assert ok_result.value == success_result.value
        assert ok_result.is_success() == success_result.is_success()
        assert ok_result.is_failure() == success_result.is_failure()

    def test_err_is_alias_for_failure(self) -> None:
        """Test that Err is the same as Failure."""
        err_result = Err("error")
        failure_result = Failure("error")
        
        assert type(err_result) is type(failure_result)
        assert err_result.error == failure_result.error
        assert err_result.is_success() == failure_result.is_success()
        assert err_result.is_failure() == failure_result.is_failure()

    def test_ok_function_is_alias_for_success(self) -> None:
        """Test that ok() function is the same as success()."""
        ok_result = ok(42)
        success_result = Success(42)
        
        assert type(ok_result) is type(success_result)
        assert ok_result.value == success_result.value

    def test_err_function_is_alias_for_failure(self) -> None:
        """Test that err() function is the same as failure()."""
        err_result = err("error")
        failure_result = Failure("error")
        
        assert type(err_result) is type(failure_result)
        assert err_result.error == failure_result.error

    def test_chaining_with_rust_aliases(self) -> None:
        """Test chaining operations using Rust aliases."""
        def double(x: int) -> Result[int, str]:
            return Ok(x * 2)
        
        def check_positive(x: int) -> Result[int, str]:
            if x > 0:
                return Ok(x)
            else:
                return Err("Negative number")
        
        # Test successful chain
        result = Ok(5) >> double >> check_positive
        assert result.is_success()
        if result.is_success():
            assert result.value == 10

        # Test failed chain
        result = Ok(-1) >> double >> check_positive
        assert result.is_failure()
        if result.is_failure():
            assert "Negative number" in str(result.error)

    def test_mixed_rust_and_normal_aliases(self) -> None:
        """Test mixing Rust aliases with normal Success/Failure."""
        def process_with_success(x: int) -> Result[int, str]:
            return Success(x + 1)
        
        def process_with_ok(x: int) -> Result[int, str]:
            return Ok(x * 2)
        
        # Chain Ok -> Success -> Ok
        result = Ok(5) >> process_with_success >> process_with_ok
        assert result.is_success()
        if result.is_success():
            assert result.value == 12  # (5 + 1) * 2

    def test_unwrap_operations_with_rust_aliases(self) -> None:
        """Test unwrap operations work with Rust aliases."""
        ok_result = Ok(42)
        err_result = Err("error")
        
        # Test unwrap
        assert ok_result.unwrap() == 42
        with pytest.raises(RuntimeError):
            err_result.unwrap()
        
        # Test unwrap_or
        assert ok_result.unwrap_or(0) == 42
        assert err_result.unwrap_or(0) == 0
        
        # Test unwrap_or_else
        assert ok_result.unwrap_or_else(lambda e: 0) == 42
        assert err_result.unwrap_or_else(lambda e: len(str(e))) == 5

    def test_map_operations_with_rust_aliases(self) -> None:
        """Test map operations work with Rust aliases."""
        ok_result = Ok(42)
        err_result = Err("error")
        
        # Test map on Ok
        mapped_ok = ok_result.map(lambda x: x * 2)
        assert mapped_ok.is_success()
        if mapped_ok.is_success():
            assert mapped_ok.value == 84
        
        # Test map on Err (should be no-op)
        mapped_err = err_result.map(lambda x: x * 2)
        assert mapped_err.is_failure()
        if mapped_err.is_failure():
            assert mapped_err.error == "error"
        
        # Test map_error on Err
        mapped_err_error = err_result.map_error(lambda e: f"Prefix: {e}")
        assert mapped_err_error.is_failure()
        if mapped_err_error.is_failure():
            assert mapped_err_error.error == "Prefix: error"
        
        # Test map_error on Ok (should be no-op)
        mapped_ok_error = ok_result.map_error(lambda e: f"Prefix: {e}")
        assert mapped_ok_error.is_success()
        if mapped_ok_error.is_success():
            assert mapped_ok_error.value == 42

    def test_repr_with_rust_aliases(self) -> None:
        """Test string representation works with Rust aliases."""
        ok_result = Ok(42)
        err_result = Err("error")
        
        assert "Success(42)" in repr(ok_result)
        assert "Failure('error')" in repr(err_result)

    def test_equality_with_rust_aliases(self) -> None:
        """Test equality operations work with Rust aliases."""
        ok1 = Ok(42)
        ok2 = Ok(42)
        ok3 = Ok(43)
        success1 = Success(42)
        
        err1 = Err("error")
        err2 = Err("error")
        err3 = Err("different")
        failure1 = Failure("error")
        
        # Test Ok equality
        assert ok1 == ok2
        assert ok1 != ok3
        assert ok1 == success1  # Ok should equal Success with same value
        
        # Test Err equality
        assert err1 == err2
        assert err1 != err3
        assert err1 == failure1  # Err should equal Failure with same error
        
        # Test cross-type inequality
        assert ok1 != err1
