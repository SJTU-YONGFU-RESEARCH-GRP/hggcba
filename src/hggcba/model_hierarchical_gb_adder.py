"""Hierarchical group-generate carry-bypass adder executable model."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class AddResult:
    """Stores adder outputs for one input vector.

    Attributes:
        sum_value: Sum truncated to the configured width.
        carry_out: Final carry output bit.
    """

    sum_value: int
    carry_out: int


def _validate_inputs(a: int, b: int, cin: int, width: int, block_size: int) -> None:
    """Validate input ranges and adder parameters.

    Args:
        a: First addend.
        b: Second addend.
        cin: Carry-in bit.
        width: Total adder width in bits.
        block_size: Number of bits per block.

    Raises:
        ValueError: If any argument is out of the supported range.
    """

    if width <= 0:
        raise ValueError("width must be positive.")
    if block_size <= 0:
        raise ValueError("block_size must be positive.")
    if cin not in (0, 1):
        raise ValueError("cin must be 0 or 1.")
    max_value: int = (1 << width) - 1
    if not (0 <= a <= max_value):
        raise ValueError("a is out of range for width.")
    if not (0 <= b <= max_value):
        raise ValueError("b is out of range for width.")


def _block_group_generate(p_bits: int, g_bits: int, block_width: int) -> int:
    """Compute block group-generate term independent of carry-in.

    Args:
        p_bits: Propagate bits packed in LSB-first order.
        g_bits: Generate bits packed in LSB-first order.
        block_width: Number of valid bits in this block.

    Returns:
        Group-generate bit for the block.
    """

    group_generate: int = 0
    for bit_index in range(block_width):
        generate_i: int = (g_bits >> bit_index) & 1
        propagate_i: int = (p_bits >> bit_index) & 1
        group_generate = generate_i | (propagate_i & group_generate)
    return group_generate


def _ripple_sum_with_carry(
    p_bits: int,
    g_bits: int,
    block_width: int,
    carry_in: int,
) -> tuple[int, int]:
    """Compute block sum bits and carry-out with local ripple recursion.

    Args:
        p_bits: Propagate bits packed in LSB-first order.
        g_bits: Generate bits packed in LSB-first order.
        block_width: Number of valid bits in this block.
        carry_in: Carry input to this block.

    Returns:
        Tuple of (block_sum, carry_out).
    """

    carry: int = carry_in
    block_sum: int = 0
    for bit_index in range(block_width):
        propagate_i: int = (p_bits >> bit_index) & 1
        generate_i: int = (g_bits >> bit_index) & 1
        block_sum |= (propagate_i ^ carry) << bit_index
        carry = generate_i | (propagate_i & carry)
    return block_sum, carry


def add_hierarchical_gb(
    a: int,
    b: int,
    cin: int,
    width: int,
    block_size: int,
) -> AddResult:
    """Compute exact addition using block group-generate and bypass policy.

    Each block computes a group-generate term `Gk` and block-propagate term `Pk`.
    Carry-out uses `Cout = Gk | (Pk & Cin)`, while sum bits are resolved by local
    ripple recursion with the actual incoming carry.

    Args:
        a: First addend.
        b: Second addend.
        cin: Carry-in bit.
        width: Adder width in bits.
        block_size: Number of bits per block.

    Returns:
        Exact sum and carry-out for the configured width.
    """

    _validate_inputs(a=a, b=b, cin=cin, width=width, block_size=block_size)
    carry: int = cin
    sum_value: int = 0
    for block_start in range(0, width, block_size):
        block_width: int = min(block_size, width - block_start)
        block_mask: int = (1 << block_width) - 1
        a_block: int = (a >> block_start) & block_mask
        b_block: int = (b >> block_start) & block_mask
        p_bits: int = a_block ^ b_block
        g_bits: int = a_block & b_block

        block_sum, _ = _ripple_sum_with_carry(
            p_bits=p_bits,
            g_bits=g_bits,
            block_width=block_width,
            carry_in=carry,
        )
        block_propagate: int = 1 if p_bits == block_mask else 0
        block_generate: int = _block_group_generate(
            p_bits=p_bits,
            g_bits=g_bits,
            block_width=block_width,
        )
        carry = block_generate | (block_propagate & carry)
        sum_value |= block_sum << block_start

    return AddResult(sum_value=sum_value, carry_out=carry)


def run_random_vectors(width: int, block_size: int, vectors: int, seed: int) -> int:
    """Run deterministic random vectors and return mismatch count.

    Args:
        width: Adder width in bits.
        block_size: Number of bits per block.
        vectors: Number of vectors to run.
        seed: Deterministic random seed.

    Returns:
        Number of mismatches against integer addition.
    """

    rng: Random = Random(seed)
    mask: int = (1 << width) - 1
    mismatches: int = 0
    for _ in range(vectors):
        a: int = rng.getrandbits(width)
        b: int = rng.getrandbits(width)
        cin: int = rng.getrandbits(1)
        expected: int = a + b + cin
        expected_sum: int = expected & mask
        expected_cout: int = (expected >> width) & 1
        got: AddResult = add_hierarchical_gb(
            a=a,
            b=b,
            cin=cin,
            width=width,
            block_size=block_size,
        )
        if got.sum_value != expected_sum or got.carry_out != expected_cout:
            mismatches += 1
    return mismatches
