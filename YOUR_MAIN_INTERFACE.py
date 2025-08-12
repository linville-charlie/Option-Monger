#!/usr/bin/env python3
"""
=================================================================
YOUR MAIN INTERFACE FOR OPTIONS TRADING
=================================================================

This file contains the key functions you requested:
1. Get three vectors (bids, strikes, deltas) for any ticker/expiration
2. Create position vectors with quantities 
3. Create ITM vectors for expiration scenarios
4. Calculate premiums with Hadamard multiplication

Example usage:
    from YOUR_MAIN_INTERFACE import get_option_data, create_positions, calculate_pnl
    
    # Get your three vectors
    bids, strikes, deltas = get_option_data('AAPL', '20250117')
    
    # Create position vector with quantities
    positions = create_positions(strikes, {220: 5, 225: 10, 230: 2})
    
    # Calculate P&L at expiration
    pnl = calculate_pnl(positions, bids, strikes, hit_price=227.50)
"""

# Add core directory to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from core.simple_real_strikes import get_all_strikes
from core.simulation import (
    simulate_expiration_price,
    monte_carlo_simulation,
    analyze_position_outcomes
)
# Removed long call optimization imports - only using covered calls
from core.position_tracker import (
    create_position_vector,
    create_itm_vector,
    create_exercise_vector,
    calculate_premium_paid_for_itm,
    calculate_net_pnl_vectors,
    hadamard_multiply,
    calculate_otm_sale_value,
    calculate_complete_pnl_with_otm_sale,
    calculate_share_cost_basis,
    calculate_covered_call_pnl
)
import pandas as pd
import numpy as np
from typing import Union, List, Tuple, Optional, Dict


# ==============================================================================
# MAIN FUNCTION 1: GET YOUR THREE VECTORS
# ==============================================================================

def get_option_data(ticker: str, 
                   expiration: str,
                   return_stock_price: bool = False) -> Union[Tuple[pd.Series, pd.Series, pd.Series], Tuple[pd.Series, pd.Series, pd.Series, float]]:
    """
    Get the three option data vectors for any ticker and expiration.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        expiration: Expiration date in YYYYMMDD format (e.g., '20250117')
        return_stock_price: If True, also return current stock price
    
    Returns:
        If return_stock_price=False:
            Tuple of three pandas Series (all same length and aligned):
            - bids: Call option bid prices
            - strikes: Strike prices  
            - deltas: Call option deltas
        If return_stock_price=True:
            Adds 4th element:
            - stock_price: Current stock price (float)
        
    Example:
        bids, strikes, deltas = get_option_data('AAPL', '20250117')
        print(f"Got {len(strikes)} strikes")
        
        # Or with stock price:
        bids, strikes, deltas, stock_price = get_option_data('AAPL', '20250117', return_stock_price=True)
        print(f"Current stock price: ${stock_price:.2f}")
    """
    return get_all_strikes(ticker, expiration, return_stock_price)


# ==============================================================================
# MAIN FUNCTION 2: CREATE POSITION VECTORS WITH QUANTITIES
# ==============================================================================

def create_positions(strikes: pd.Series,
                    bought_contracts: Union[Dict[float, int], List[float], float],
                    quantities: Optional[Union[int, List[int]]] = None) -> pd.Series:
    """
    Create a position vector showing how many contracts you bought at each strike.
    
    Args:
        strikes: The strikes Series from get_option_data()
        bought_contracts: Can be:
            - Dict: {220.0: 5, 225.0: 10} - buy 5 at 220, 10 at 225
            - List: [220.0, 225.0] - buy 1 each (or use quantities param)
            - Float: 225.0 - buy 1 contract
        quantities: Optional quantities if using list/float format
        
    Returns:
        pd.Series with quantities (0, 1, 2, ...) same length as strikes
        
    Example:
        # Method 1: Using dict (recommended)
        positions = create_positions(strikes, {220: 5, 225: 10, 230: 2})
        
        # Method 2: List with same quantity
        positions = create_positions(strikes, [220, 225, 230], quantities=5)
        
        # Method 3: List with different quantities
        positions = create_positions(strikes, [220, 225, 230], quantities=[5, 10, 2])
    """
    if isinstance(bought_contracts, dict):
        return create_position_vector(strikes, bought_strikes=bought_contracts)
    else:
        return create_position_vector(strikes, bought_strikes=bought_contracts, quantities=quantities)


# ==============================================================================
# MAIN FUNCTION 3: CREATE ITM VECTOR FOR EXPIRATION
# ==============================================================================

def create_itm_mask(strikes: pd.Series, 
                   expiration_price: float,
                   option_type: str = 'C') -> pd.Series:
    """
    Create a binary vector showing which strikes are in-the-money at expiration.
    
    Args:
        strikes: The strikes Series from get_option_data()
        expiration_price: The stock price at expiration
        option_type: 'C' for calls, 'P' for puts
        
    Returns:
        pd.Series of 1s and 0s (1 = ITM, 0 = OTM)
        
    Example:
        # Stock expires at $227.50
        itm = create_itm_mask(strikes, 227.50)
        
        # See which strikes are ITM
        itm_strikes = strikes[itm == 1]
        print(f"ITM strikes: {itm_strikes.tolist()}")
    """
    return create_itm_vector(strikes, expiration_price, option_type)


# ==============================================================================
# MAIN FUNCTION 4: CALCULATE PREMIUM WITH HADAMARD MULTIPLICATION
# ==============================================================================

def calculate_premium_for_itm_positions(positions: pd.Series,
                                       strikes: pd.Series,
                                       bids: pd.Series,
                                       expiration_price: float,
                                       contract_multiplier: int = 100) -> pd.Series:
    """
    Calculate premium paid for positions that ended up ITM.
    Uses Hadamard multiplication: positions ⊙ itm ⊙ (bids × 100)
    
    Args:
        positions: Your position vector (quantities at each strike)
        strikes: The strikes Series
        bids: The bid prices Series
        expiration_price: Where the stock expired
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        pd.Series showing premium paid for each ITM position
        
    Example:
        # You bought 5 at 220, 10 at 225, 2 at 230
        positions = create_positions(strikes, {220: 5, 225: 10, 230: 2})
        
        # Stock expires at 227.50 (220 and 225 are ITM, 230 is OTM)
        premium_itm = calculate_premium_for_itm_positions(
            positions, strikes, bids, 227.50
        )
        
        total_premium_itm = premium_itm.sum()
        print(f"Total premium for ITM positions: ${total_premium_itm:.2f}")
    """
    itm = create_itm_vector(strikes, expiration_price, 'C')
    return calculate_premium_paid_for_itm(positions, itm, bids, contract_multiplier)


# ==============================================================================
# MAIN FUNCTION 5: CALCULATE COMPLETE P&L
# ==============================================================================

def calculate_pnl(positions: pd.Series,
                 bids: pd.Series,
                 strikes: pd.Series,
                 hit_price: float,
                 contract_multiplier: int = 100) -> Dict:
    """
    Calculate complete P&L for your positions at expiration.
    
    Args:
        positions: Your position vector (quantities)
        bids: Bid prices
        strikes: Strike prices
        hit_price: Stock price at expiration
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        Dictionary with P&L breakdown
        
    Example:
        positions = create_positions(strikes, {220: 5, 225: 10})
        results = calculate_pnl(positions, bids, strikes, 227.50)
        
        print(f"Total P&L: ${results['total_pnl']:.2f}")
        print(f"ITM contracts: {results['itm_count']}")
        print(f"Premium paid: ${results['total_premium_paid_all']:.2f}")
    """
    itm = create_itm_vector(strikes, hit_price, 'C')
    return calculate_net_pnl_vectors(positions, itm, strikes, bids, hit_price, contract_multiplier)


# ==============================================================================
# MAIN FUNCTION 8: CALCULATE SHARE COST BASIS
# ==============================================================================

def calculate_initial_share_cost(positions: pd.Series,
                                purchase_price: float,
                                contract_multiplier: int = 100) -> pd.Series:
    """
    Calculate the cost basis for shares underlying your positions.
    
    Formula: positions × purchase_price × 100
    
    Args:
        positions: Your position vector (quantities at each strike)
        purchase_price: Price per share when you bought them
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        pd.Series showing total cost for shares at each position
        
    Example:
        # You have these positions
        positions = create_positions(strikes, {220: 5, 225: 10, 230: 2})
        
        # You bought the underlying shares at $200 each
        cost_basis = calculate_initial_share_cost(positions, purchase_price=200.0)
        
        # Results:
        # 220 strike: 5 contracts × 100 shares × $200 = $100,000
        # 225 strike: 10 contracts × 100 shares × $200 = $200,000
        # 230 strike: 2 contracts × 100 shares × $200 = $40,000
        
        total_cost = cost_basis.sum()
        print(f"Total invested in shares: ${total_cost:,.2f}")
    """
    from core.position_tracker import calculate_share_cost_basis
    return calculate_share_cost_basis(positions, purchase_price, contract_multiplier)


# ==============================================================================
# MAIN FUNCTION 9: COMPLETE COVERED CALL P&L
# ==============================================================================

def calculate_covered_call_total_pnl(positions: pd.Series,
                                    strikes: pd.Series,
                                    bids: pd.Series,
                                    initial_share_price: float,
                                    expiration_price: float,
                                    contract_multiplier: int = 100) -> Dict:
    """
    Calculate complete P&L for covered call positions including share cost basis.
    
    Args:
        positions: Your covered call positions (calls sold)
        strikes: Strike prices
        bids: Premium collected per contract
        initial_share_price: What you paid per share initially
        expiration_price: Stock price at expiration
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        Dictionary with complete P&L breakdown
        
    Example:
        positions = create_positions(strikes, {220: 5, 225: 10})
        
        results = calculate_covered_call_total_pnl(
            positions, strikes, bids,
            initial_share_price=200.0,  # Bought shares at $200
            expiration_price=227.50      # Stock expires at $227.50
        )
        
        print(f"Share cost: ${results['total_share_cost']:,.2f}")
        print(f"Premium collected: ${results['premium_collected']:,.2f}")
        print(f"Total proceeds: ${results['total_proceeds']:,.2f}")
        print(f"Net P&L: ${results['net_pnl']:,.2f}")
        print(f"Return: {results['return_pct']:.2f}%")
    """
    from core.position_tracker import calculate_covered_call_pnl
    return calculate_covered_call_pnl(
        positions, strikes, bids, initial_share_price, expiration_price, contract_multiplier
    )


# ==============================================================================
# MAIN FUNCTION 10: MONTE CARLO SIMULATION
# ==============================================================================

def simulate_option_expiration(strikes: pd.Series,
                              deltas: pd.Series,
                              positions: pd.Series,
                              random_seed: Optional[int] = None) -> float:
    """
    Simulate a single expiration price using deltas as ITM probabilities.
    
    Each delta is treated as the probability that strike will be ITM.
    The function uses these probabilities to determine which strikes end up ITM,
    then generates a realistic expiration price.
    
    Args:
        strikes: Strike prices
        deltas: Delta values (used as ITM probabilities)
        positions: Your positions (to determine price constraints)
        random_seed: Optional seed for reproducibility
        
    Returns:
        Simulated expiration price
        
    Example:
        # Single simulation
        exp_price = simulate_option_expiration(strikes, deltas, positions)
        print(f"Simulated expiration: ${exp_price:.2f}")
        
        # Check which positions ended ITM
        itm = strikes <= exp_price
        print(f"ITM positions: {strikes[itm & (positions > 0)].tolist()}")
    """
    return simulate_expiration_price(strikes, deltas, positions, random_seed)


def run_monte_carlo_analysis(strikes: pd.Series,
                            deltas: pd.Series,
                            positions: pd.Series,
                            bids: pd.Series,
                            n_simulations: int = 10000,
                            random_seed: Optional[int] = None) -> Dict:
    """
    Run Monte Carlo simulation for your option positions.
    
    Uses deltas as probabilities to simulate thousands of possible outcomes
    and calculate expected P&L, risk metrics, and probabilities.
    
    Args:
        strikes: Strike prices
        deltas: Delta values (used as ITM probabilities)
        positions: Your position quantities
        bids: Bid prices (for P&L calculation)
        n_simulations: Number of simulations (default 10,000)
        random_seed: Optional seed for reproducibility
        
    Returns:
        Dictionary with comprehensive simulation results
        
    Example:
        positions = create_positions(strikes, {220: 5, 225: 10, 230: 2})
        
        # Run 10,000 simulations
        results = run_monte_carlo_analysis(
            strikes, deltas, positions, bids,
            n_simulations=10000
        )
        
        print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
        print(f"Win rate: {results['win_rate']:.1f}%")
        print(f"95% VaR: ${results['var_95']:,.2f}")
        print(f"Max possible gain: ${results['max_pnl']:,.2f}")
        print(f"Max possible loss: ${results['min_pnl']:,.2f}")
    """
    return monte_carlo_simulation(strikes, deltas, positions, bids, n_simulations, random_seed)


# ==============================================================================
# MAIN FUNCTION 11: PORTFOLIO OPTIMIZATION
# ==============================================================================

def optimize_option_portfolio(strikes: pd.Series,
                            deltas: pd.Series,
                            bids: pd.Series,
                            capital: float,
                            max_contracts_per_strike: int = 100,
                            n_simulations: int = 1000,
                            n_candidates: int = 100,
                            random_seed: Optional[int] = None) -> Dict:
    """
    Find the optimal option portfolio to maximize expected profit.
    
    Uses Monte Carlo simulation with delta-based probabilities to test
    different portfolio combinations and find the best allocation.
    
    Args:
        strikes: Available strike prices
        deltas: Delta values (used as ITM probabilities)
        bids: Bid prices per contract
        capital: Total capital available to invest
        max_contracts_per_strike: Max contracts per strike (default 100)
        n_simulations: Simulations per portfolio (default 1000)
        n_candidates: Portfolio combinations to test (default 100)
        random_seed: Optional seed for reproducibility
        
    Returns:
        Dictionary with optimal portfolio and analysis
        
    Example:
        # Find best portfolio with $10,000
        results = optimize_option_portfolio(
            strikes, deltas, bids,
            capital=10000,
            n_simulations=1000,
            n_candidates=100
        )
        
        print(f"Optimal positions: {results['optimal_positions']}")
        print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
        print(f"Win rate: {results['win_rate']:.1f}%")
        print(f"Capital used: ${results['capital_used']:,.2f}")
        
        # Create the optimal positions
        positions = create_positions(strikes, results['optimal_positions'])
    """
    return optimize_portfolio(
        strikes, deltas, bids, capital,
        max_contracts_per_strike, n_simulations, n_candidates, random_seed
    )


def optimize_specific_strikes(strikes: pd.Series,
                            deltas: pd.Series,
                            bids: pd.Series,
                            capital: float,
                            target_strikes: List[float],
                            max_contracts_per_strike: int = 50,
                            n_simulations: int = 1000,
                            random_seed: Optional[int] = None) -> Dict:
    """
    Find optimal allocation for specific strikes you're interested in.
    
    Tests all quantity combinations for your chosen strikes to find
    the allocation with highest expected profit.
    
    Args:
        strikes: All available strikes
        deltas: Delta values
        bids: Bid prices
        capital: Available capital
        target_strikes: Specific strikes to consider (e.g., [220, 225, 230])
        max_contracts_per_strike: Maximum per strike
        n_simulations: Simulations per combination
        random_seed: Optional seed
        
    Returns:
        Dictionary with optimal allocation
        
    Example:
        # Find best allocation for 220, 225, 230 strikes
        results = optimize_specific_strikes(
            strikes, deltas, bids,
            capital=10000,
            target_strikes=[220.0, 225.0, 230.0]
        )
        
        print(f"Best allocation: {results['optimal_allocation']}")
        print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
        
        # Top 5 allocations tested
        for i, alt in enumerate(results['top_5_allocations']):
            print(f"{i+1}. {alt['allocation']} -> ${alt['expected_pnl']:.2f}")
    """
    return exhaustive_optimize(
        strikes, deltas, bids, capital, target_strikes,
        max_contracts_per_strike, n_simulations, random_seed
    )


# ==============================================================================
# MAIN FUNCTION 12: CONTINUOUS POSITION OPTIMIZATION
# ==============================================================================

def optimize_positions_vector(strikes: pd.Series,
                            deltas: pd.Series,
                            bids: pd.Series,
                            capital: float,
                            initial_positions: Optional[pd.Series] = None,
                            max_contracts: int = 100,
                            n_simulations: int = 200,
                            method: str = 'differential_evolution') -> Dict:
    """
    Optimize position quantities using continuous optimization.
    
    This function directly optimizes the position vector using scipy optimizers
    to find the quantities that maximize expected P&L.
    
    Args:
        strikes: Strike prices
        deltas: Delta values (used as ITM probabilities)
        bids: Bid prices
        capital: Available capital
        initial_positions: Starting positions (optional)
        max_contracts: Maximum contracts per strike
        n_simulations: Simulations per evaluation
        method: 'differential_evolution' (global) or 'SLSQP' (local)
        
    Returns:
        Dictionary with optimized positions
        
    Example:
        # Optimize positions with $10,000
        results = optimize_positions_vector(
            strikes, deltas, bids,
            capital=10000,
            n_simulations=200
        )
        
        print(f"Optimized positions: {results['optimal_positions']}")
        print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
        print(f"Capital used: ${results['capital_used']:,.2f}")
        
        # Get the position vector
        positions = results['optimal_positions_vector']
    """
    return optimize_positions_continuous(
        strikes, deltas, bids, capital,
        initial_positions, max_contracts, n_simulations, method
    )


def optimize_for_target_profit(strikes: pd.Series,
                              deltas: pd.Series,
                              bids: pd.Series,
                              capital: float,
                              target_profit: float,
                              tolerance: float = 100,
                              max_contracts: int = 100,
                              n_simulations: int = 200) -> Dict:
    """
    Find positions to achieve a target expected profit.
    
    Optimizes the position vector to get as close as possible to
    your target expected P&L while minimizing capital usage.
    
    Args:
        strikes: Strike prices
        deltas: Delta values
        bids: Bid prices
        capital: Maximum available capital
        target_profit: Desired expected P&L
        tolerance: Acceptable deviation from target
        max_contracts: Maximum per strike
        n_simulations: Simulations per evaluation
        
    Returns:
        Dictionary with optimized positions
        
    Example:
        # Find positions to achieve $5,000 expected profit
        results = optimize_for_target_profit(
            strikes, deltas, bids,
            capital=20000,
            target_profit=5000,
            tolerance=100
        )
        
        print(f"Positions: {results['optimal_positions']}")
        print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
        print(f"Target was: ${results['target_pnl']:,.2f}")
        print(f"Within tolerance: {results['within_tolerance']}")
    """
    return optimize_target_pnl(
        strikes, deltas, bids, capital, target_profit,
        max_contracts, n_simulations, tolerance
    )


# ==============================================================================
# MAIN FUNCTION 13: SIMPLIFIED ONE-STEP OPTIMIZATION
# ==============================================================================

def find_best_options(ticker: str,
                     expiration: str,
                     capital: float,
                     max_contracts_per_strike: int = 50,
                     n_simulations: int = 200,
                     optimization_method: str = 'auto') -> Dict:
    """
    Find optimal covered call positions for any ticker.
    
    This function ONLY handles covered calls:
    - Your capital buys shares (100 shares per contract)
    - Finds optimal strikes to sell calls against your shares
    - Returns expected P&L including premium collection
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        expiration: Expiration date in YYYYMMDD format (e.g., '20250117')
        capital: Amount of capital to buy shares with
        max_contracts_per_strike: Maximum contracts per strike (default 50)
        n_simulations: Simulations for Monte Carlo (default 200)
        optimization_method: 'auto', 'fast', or 'thorough' (default 'auto')
        
    Returns:
        Dictionary with:
        - optimal_positions: Dict of {strike: quantity} for calls to sell
        - expected_pnl: Expected profit/loss from covered call strategy
        - shares_needed: Number of shares to buy
        - capital_for_shares: Cost to buy the shares
        - premium_collected: Premium from selling calls
        - win_rate: Probability of profit
        - recommendation: Text summary of strategy
        
    Example:
        # Find best covered calls for AAPL with $100,000
        results = find_best_options('AAPL', '20250117', 100000)
        
        print(results['recommendation'])
        print(f"Buy {results['shares_needed']} shares")
        print(f"Sell calls: {results['optimal_positions']}")
        print(f"Expected P&L: ${results['expected_pnl']:,.2f}")
    """
    # Step 1: Get option data with stock price
    print(f"Fetching {ticker} options for {expiration}...")
    # Get option data and actual stock price
    from core.simple_real_strikes import get_all_strikes
    bids, strikes, deltas, current_stock_price = get_all_strikes(
        ticker, expiration, use_live_data, return_stock_price=True
    )
    
    if len(strikes) == 0:
        raise ValueError(f"No option data found for {ticker} {expiration}")
    
    print(f"Current stock price: ${current_stock_price:.2f}")
    
    # Import covered call optimization
    from core.covered_call_optimization import (
        optimize_covered_calls,
        optimize_covered_calls_continuous
    )
    
    # Check if we have enough capital for at least one contract
    min_capital_needed = current_stock_price * 100
    if capital < min_capital_needed:
        raise ValueError(f"Insufficient capital for covered calls. Need at least ${min_capital_needed:,.2f} to buy 100 shares")
    
    # Determine optimization approach
    if optimization_method == 'auto':
        if capital < min_capital_needed * 5:  # Less than 5 contracts worth
            method = 'fast'
            use_continuous = False
        elif capital < min_capital_needed * 20:  # Less than 20 contracts
            method = 'balanced'
            use_continuous = True
        else:
            method = 'thorough'
            use_continuous = True
    else:
        method = optimization_method
        use_continuous = method != 'fast'
    
    print(f"Optimizing covered calls portfolio (method: {method})...")
    
    # Step 2: Run covered call optimization
    if use_continuous:
        opt_results = optimize_covered_calls_continuous(
            strikes, deltas, bids,
            capital=capital,
            current_stock_price=current_stock_price,
            n_simulations=n_simulations,
            random_seed=42
        )
    else:
        opt_results = optimize_covered_calls(
            strikes, deltas, bids,
            capital=capital,
            current_stock_price=current_stock_price,
            max_contracts_per_strike=max_contracts_per_strike,
            n_simulations=n_simulations,
            n_candidates=30 if method == 'fast' else 100,
            random_seed=42
        )
    
    # Step 3: Prepare detailed results
    position_details = []
    for strike, qty in opt_results['optimal_positions'].items():
        idx = np.abs(strikes - strike).argmin()
        position_details.append({
            'strike': strike,
            'quantity': qty,
            'delta': deltas.iloc[idx],
            'bid': bids.iloc[idx],
            'premium_per_contract': bids.iloc[idx] * 100,
            'itm_probability': deltas.iloc[idx] * 100  # Delta as ITM probability
        })
    
    # Sort by strike
    position_details.sort(key=lambda x: x['strike'])
    
    # Generate recommendation text
    n_positions = len(opt_results['optimal_positions'])
    total_contracts = sum(opt_results['optimal_positions'].values())
    
    # Covered call recommendation
    recommendation = f"""
Optimal Covered Call Strategy for {ticker} expiring {expiration}:

1. BUY SHARES:
   - Buy {opt_results['shares_needed']} shares at ${current_stock_price:.2f}
   - Total cost: ${opt_results['capital_for_shares']:,.2f}

2. SELL CALLS:
   - Sell {opt_results['contracts_sold']} call contracts
   - Premium collected: ${opt_results['premium_collected']:,.2f}
   - Net capital after premium: ${opt_results['net_capital_after_premium']:,.2f}

3. EXPECTED RESULTS:
   - Expected P&L: ${opt_results['expected_pnl']:,.2f}
   - Win Rate: {opt_results['win_rate']:.1f}%
   - Return on Capital: {opt_results['return_on_capital']:.2f}%
   - Max Gain: ${opt_results.get('max_gain', 0):,.2f}
   - 95% VaR: ${opt_results.get('var_95', 0):,.2f}

4. CALL POSITIONS TO SELL:
"""
    for detail in position_details:
        recommendation += f"   • Sell {detail['quantity']} calls at ${detail['strike']:.2f} strike"
        recommendation += f" (Delta={detail['delta']:.2f}, {detail['itm_probability']:.1f}% ITM probability, "
        recommendation += f"collect ${detail['premium_per_contract']:.2f}/contract)\n"
    
    recommendation += "\nNote: This is a covered call strategy. You must own the shares before selling these calls."
    
    # Return covered call results
    return {
        'ticker': ticker,
        'expiration': expiration,
        'strategy': 'covered_calls',
        'optimal_positions': opt_results['optimal_positions'],
        'expected_pnl': opt_results['expected_pnl'],
        'win_rate': opt_results['win_rate'],
        'var_95': opt_results.get('var_95', None),
        'max_gain': opt_results.get('max_gain', None),
        'max_loss': opt_results.get('max_loss', None),
        'shares_needed': opt_results['shares_needed'],
        'capital_for_shares': opt_results['capital_for_shares'],
        'premium_collected': opt_results['premium_collected'],
        'net_capital_after_premium': opt_results['net_capital_after_premium'],
        'return_on_capital': opt_results['return_on_capital'],
        'current_stock_price': current_stock_price,
        'position_details': position_details,
        'recommendation': recommendation,
        'strikes': strikes,
        'bids': bids,
        'deltas': deltas,
        'optimization_method': method,
        'n_positions': n_positions,
        'contracts_sold': opt_results['contracts_sold']
    }


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

# ==============================================================================
# MAIN FUNCTION 6: CALCULATE OTM SALE VALUE
# ==============================================================================

def calculate_otm_share_sale_proceeds(positions: pd.Series,
                                     strikes: pd.Series,
                                     stock_price: float,
                                     contract_multiplier: int = 100) -> pd.Series:
    """
    Calculate proceeds from selling shares for OTM covered call positions.
    
    For covered calls that expire OTM, you keep your shares and sell them
    immediately at the current stock price.
    
    Uses Hadamard multiplication: positions ⊙ (1 - itm) × stock_price × 100
    
    Args:
        positions: Your covered call position vector (quantities)
        strikes: The strikes Series
        stock_price: Current stock price (both for ITM determination and share sale)
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        pd.Series showing share sale proceeds for each OTM position
        
    Example:
        # You sold covered calls: 5 at 220, 10 at 225, 2 at 230
        positions = create_positions(strikes, {220: 5, 225: 10, 230: 2})
        
        # Stock closes at 227.50
        # 220 and 225 are ITM (shares get called away)
        # 230 is OTM (you keep shares and sell them)
        share_proceeds = calculate_otm_share_sale_proceeds(
            positions, strikes, 
            stock_price=227.50
        )
        
        # 2 contracts × 100 shares × $227.50 = $45,500 from 230 strike
        total_proceeds = share_proceeds.sum()
        print(f"Total from selling shares (OTM positions): ${total_proceeds:.2f}")
    """
    from core.position_tracker import calculate_otm_share_sale_value
    itm = create_itm_vector(strikes, stock_price, 'C')
    return calculate_otm_share_sale_value(positions, itm, stock_price, contract_multiplier)


# ==============================================================================
# MAIN FUNCTION 7: COMPLETE P&L WITH OTM SALES
# ==============================================================================

def calculate_pnl_with_otm_sale(positions: pd.Series,
                               bids: pd.Series,
                               strikes: pd.Series,
                               hit_price: float,
                               otm_sale_price: float = 0,
                               contract_multiplier: int = 100) -> Dict:
    """
    Calculate complete P&L including selling OTM contracts before expiration.
    
    Args:
        positions: Your position vector (quantities)
        bids: Original bid prices when you bought
        strikes: Strike prices
        hit_price: Stock price at expiration
        otm_sale_price: Price per contract for selling OTM options
                       (0 = hold to expiry, don't sell)
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        Dictionary with complete P&L breakdown
        
    Example:
        positions = create_positions(strikes, {220: 5, 225: 10, 230: 2})
        
        # Stock expires at 227.50
        # Sell OTM 230s for $0.30 each before expiration
        results = calculate_pnl_with_otm_sale(
            positions, bids, strikes,
            hit_price=227.50,
            otm_sale_price=0.30
        )
        
        print(f"Premium paid: ${results['total_premium_paid']:.2f}")
        print(f"ITM intrinsic: ${results['itm_intrinsic_received']:.2f}")
        print(f"OTM sale proceeds: ${results['otm_sale_proceeds']:.2f}")
        print(f"Total P&L: ${results['total_pnl_with_sale']:.2f}")
        print(f"P&L improvement from selling OTM: ${results['pnl_improvement_from_sale']:.2f}")
    """
    return calculate_complete_pnl_with_otm_sale(
        positions, bids, strikes, hit_price, otm_sale_price, contract_multiplier
    )


def find_strike_by_delta(strikes: pd.Series, 
                        deltas: pd.Series,
                        target_delta: float) -> float:
    """Find the strike closest to a target delta."""
    idx = np.abs(deltas - target_delta).argmin()
    return strikes.iloc[idx]


def calculate_spread_cost(positions_long: pd.Series,
                         positions_short: pd.Series,
                         bids: pd.Series,
                         contract_multiplier: int = 100) -> float:
    """Calculate net debit/credit for a spread position."""
    long_cost = (positions_long * bids * contract_multiplier).sum()
    short_credit = (positions_short * bids * contract_multiplier).sum()
    return long_cost - short_credit


# ==============================================================================
# QUICK START EXAMPLE
# ==============================================================================

def quick_example():
    """
    Quick example showing all the main functions.
    """
    print("="*70)
    print("QUICK START EXAMPLE")
    print("="*70)
    
    # 1. Get your three vectors
    print("\n1. Getting option data for AAPL...")
    bids, strikes, deltas = get_option_data('AAPL', '20250117')
    print(f"   ✓ Got {len(strikes)} strikes")
    
    # 2. Create position vector with quantities
    print("\n2. Creating positions...")
    positions = create_positions(strikes, {
        220.0: 5,   # Buy 5 contracts at 220
        225.0: 10,  # Buy 10 contracts at 225
        230.0: 2    # Buy 2 contracts at 230
    })
    print(f"   ✓ Total contracts: {positions.sum()}")
    
    # 3. Calculate P&L at expiration
    print("\n3. Calculating P&L if stock expires at $227.50...")
    results = calculate_pnl(positions, bids, strikes, hit_price=227.50)
    
    print(f"   Premium paid: ${results['total_premium_paid_all']:,.2f}")
    print(f"   Intrinsic received: ${results['total_intrinsic_received']:,.2f}")
    print(f"   Net P&L: ${results['total_pnl']:,.2f}")
    print(f"   ITM positions: {results['itm_count']} out of {positions[positions > 0].count()}")
    
    print("\n" + "="*70)
    print("You now have all the functions you need!")
    print("Import this file and use the functions above in your strategy.")
    print("="*70)


if __name__ == "__main__":
    quick_example()