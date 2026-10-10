"""Unit tests for hierarchical group-generate bypass adder model."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from hggcba.model_hierarchical_gb_adder import (
    AddResult,
    add_hierarchical_gb,
    run_random_vectors,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.mark.parametrize(
    "a,b,cin,width,block_size",
    [
        (0, 0, 0, 8, 2),
        (0, 0, 1, 8, 4),
        (255, 1, 0, 8, 2),
        (255, 255, 1, 8, 4),
        (0xAAAA, 0x5555, 0, 16, 4),
        (0x00FF, 0xFF00, 1, 16, 8),
    ],
)
def test_directed_cases(a: int, b: int, cin: int, width: int, block_size: int) -> None:
    """Validate directed vectors against integer-add reference."""

    expected: int = a + b + cin
    mask: int = (1 << width) - 1
    got: AddResult = add_hierarchical_gb(
        a=a,
        b=b,
        cin=cin,
        width=width,
        block_size=block_size,
    )
    assert got.sum_value == (expected & mask)
    assert got.carry_out == ((expected >> width) & 1)


@pytest.mark.parametrize("width", [4, 8, 16, 32, 64])
@pytest.mark.parametrize("block_size", [2, 4, 8])
def test_random_matrix(width: int, block_size: int) -> None:
    """Validate deterministic random vectors across width/block combinations."""

    if block_size > width:
        pytest.skip("Block size larger than width is not applicable.")
    mismatches: int = run_random_vectors(
        width=width,
        block_size=block_size,
        vectors=250,
        seed=20260422 + width * 10 + block_size,
    )
    assert mismatches == 0


def test_invalid_inputs_raise_value_error() -> None:
    """Ensure invalid arguments fail with explicit validation errors."""

    with pytest.raises(ValueError):
        add_hierarchical_gb(a=1, b=2, cin=0, width=0, block_size=2)
    with pytest.raises(ValueError):
        add_hierarchical_gb(a=1, b=2, cin=0, width=8, block_size=0)
    with pytest.raises(ValueError):
        add_hierarchical_gb(a=1, b=2, cin=2, width=8, block_size=2)
