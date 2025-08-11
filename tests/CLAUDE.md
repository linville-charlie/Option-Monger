# Claude Development Notes - Tests Directory

## Purpose
Test files demonstrating and validating key functionality, especially vector operations and alignment.

## Key Test Files

### `test_quantities.py`
**Tests**: Position vectors with quantities (not just binary)
- Creating positions with different quantities
- Dict notation: `{220: 5, 225: 10}`
- List with quantities: `quantities=[2, 5, 1]`
- P&L calculation with quantities
- Large position scenarios (100+ contracts)

**Key Validation**:
```python
# Quantities work in all calculations
positions = create_position_vector(strikes, {220: 10, 225: 5})
premium_total = (positions * bids * 100).sum()
```

### `test_hadamard.py`
**Tests**: Hadamard (element-wise) multiplication
- `positions ⊙ itm ⊙ (bids × 100)`
- Premium calculation for ITM positions only
- Verification of mathematical correctness
- Multiple methods produce same result

**Key Formula**:
```python
# Three equivalent methods
result1 = positions * itm * (bids * 100)
result2 = calculate_premium_paid_for_itm(positions, itm, bids)
result3 = hadamard_multiply(positions, itm, bids * 100)
assert np.allclose(result1, result2, result3)
```

### `test_itm_vector.py`
**Tests**: ITM vector creation and usage
- Creating binary ITM vectors
- Combining with position vectors
- P&L calculation at expiration
- Multiple expiration scenarios

**Key Concepts**:
```python
# ITM vector marks strikes <= hit_price
itm = create_itm_vector(strikes, hit_strike=227.50)
# Combine with positions
exercised = positions * itm  # Only ITM positions
```

### `test_position_vector.py`
**Tests**: Position vector creation and alignment
- Binary position vectors (original version)
- Vector alignment verification
- Combined DataFrame operations
- Cost and delta calculations

**Alignment Proof**:
```python
# All vectors perfectly aligned
assert len(positions) == len(strikes) == len(bids) == len(deltas)
assert positions.index.equals(strikes.index)
```

### `test_index_alignment.py`
**Tests**: Index alignment across all vectors
- Proves indices match across vectors
- Boolean mask operations
- Iterating through vectors together
- Spread calculations

**Key Validation**:
```python
# Same index = same contract
for i in range(len(strikes)):
    # strikes[i], bids[i], deltas[i], positions[i] 
    # all refer to the SAME option contract
```

### `test_real_strikes.py`
**Tests**: Real strike fetching from IBKR
- Gets actual strikes from IB Gateway
- Shows real increments (not $0.50)
- Fallback to demo data
- Strike increment detection

**Findings**:
- AAPL: 104 strikes, $5 increments
- Real strikes differ from requested $0.50
- Demo mode provides $0.50 as fallback

## Test Patterns

### Pattern 1: Vector Creation
```python
# Get base vectors
bids, strikes, deltas = get_all_strikes('AAPL', '20250117', use_live_data=False)

# Create position vector
positions = create_position_vector(strikes, bought_strikes=[220, 225, 230])

# Verify alignment
assert len(positions) == len(strikes)
```

### Pattern 2: P&L Calculation
```python
# Setup
hit_price = 227.50
itm = create_itm_vector(strikes, hit_strike=hit_price)

# Calculate components
premium_paid = positions * bids * 100
intrinsic_received = positions * itm * np.maximum(hit_price - strikes, 0) * 100
pnl = intrinsic_received - premium_paid
```

### Pattern 3: Spread Testing
```python
# Create spread
long_pos = create_position_vector(strikes, bought_strikes=220)
short_pos = create_position_vector(strikes, bought_strikes=230)
net_positions = long_pos - short_pos

# Calculate spread P&L
spread_pnl = net_positions * (intrinsic - bids) * 100
```

## Running Tests

```bash
# Test individual features
python tests/test_quantities.py      # Position quantities
python tests/test_hadamard.py        # Hadamard multiplication
python tests/test_itm_vector.py      # ITM detection
python tests/test_position_vector.py # Position creation
python tests/test_index_alignment.py # Vector alignment

# All tests use demo data by default
# No IB Gateway required for testing
```

## Key Validations

1. **Vector Length**: All vectors same length
2. **Index Alignment**: Same index = same contract
3. **Quantity Support**: 0, 1, 2, 3, ... (not just binary)
4. **Hadamard Works**: Element-wise multiplication correct
5. **ITM Detection**: Correctly marks strikes ≤ hit price
6. **P&L Accuracy**: Premium and intrinsic calculations correct

## Common Assertions

```python
# Length equality
assert len(bids) == len(strikes) == len(deltas) == len(positions)

# Index alignment
assert bids.index.equals(strikes.index)

# Quantities work
assert positions.sum() == total_contracts_bought

# ITM marking
assert all(strikes[itm == 1] <= hit_price)

# P&L components
assert total_pnl == intrinsic_received - premium_paid
```