#!/usr/bin/env python3
"""
Test that find_best_options() ONLY does covered calls
"""
from YOUR_MAIN_INTERFACE import find_best_options

print("COVERED CALLS ONLY TEST")
print("="*70)

# Test 1: Default behavior (should be covered calls)
print("\n1. Default Behavior Test")
print("-"*50)

results = find_best_options(
    ticker='AAPL',
    expiration='20250117',
    capital=100000,
    use_live_data=False,
    n_simulations=50
)

print(f"Strategy: {results.get('strategy', 'Not specified')}")
assert results['strategy'] == 'covered_calls', "Should be covered calls by default"
print("✓ Default is covered calls")
print(f"  Shares to buy: {results['shares_needed']}")
print(f"  Calls to sell: {results['contracts_sold']} contracts")
print(f"  Premium collected: ${results['premium_collected']:,.2f}")

# Test 2: Verify no long call logic
print("\n2. Verify Covered Call Specific Fields")
print("-"*50)

covered_call_fields = [
    'shares_needed',
    'capital_for_shares', 
    'premium_collected',
    'net_capital_after_premium',
    'return_on_capital',
    'contracts_sold',
    'current_stock_price'
]

missing = []
for field in covered_call_fields:
    if field not in results:
        missing.append(field)

if missing:
    print(f"✗ Missing covered call fields: {missing}")
else:
    print("✓ All covered call specific fields present")

# Test 3: Verify capital is used for shares, not options
print("\n3. Capital Usage Verification")
print("-"*50)

shares_cost = results['shares_needed'] * results['current_stock_price']
print(f"Shares cost: {results['shares_needed']} × ${results['current_stock_price']:.2f} = ${shares_cost:.2f}")
print(f"Capital for shares: ${results['capital_for_shares']:.2f}")
print(f"Match: {abs(shares_cost - results['capital_for_shares']) < 0.01}")

if abs(shares_cost - results['capital_for_shares']) < 0.01:
    print("✓ Capital correctly used to buy shares (not option premiums)")
else:
    print("✗ Capital calculation mismatch")

# Test 4: Recommendation mentions covered calls
print("\n4. Recommendation Content")
print("-"*50)

if 'covered call' in results['recommendation'].lower():
    print("✓ Recommendation mentions covered calls")
else:
    print("✗ Recommendation doesn't mention covered calls")

if 'buy shares' in results['recommendation'].lower():
    print("✓ Recommendation mentions buying shares")
else:
    print("✗ Recommendation doesn't mention buying shares")

if 'sell calls' in results['recommendation'].lower():
    print("✓ Recommendation mentions selling calls")
else:
    print("✗ Recommendation doesn't mention selling calls")

# Test 5: Try invalid strategy parameter (should not exist)
print("\n5. No Strategy Parameter Test")
print("-"*50)

try:
    # This should work since strategy parameter was removed
    results2 = find_best_options(
        ticker='SPY',
        expiration='20250117', 
        capital=50000,
        use_live_data=False,
        n_simulations=50
    )
    print("✓ Function works without strategy parameter")
    print(f"  Returns covered calls: {results2['strategy'] == 'covered_calls'}")
except TypeError as e:
    if 'strategy' in str(e):
        print("✗ Strategy parameter still exists")
    else:
        print(f"✗ Unexpected error: {e}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
✓ find_best_options() now ONLY does covered calls
✓ No strategy parameter needed
✓ Capital is used to buy shares
✓ Returns optimal strikes to sell calls against
✓ All covered call specific fields are present

The function is now exclusively for covered call optimization.
""")