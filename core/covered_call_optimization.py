#!/usr/bin/env python3
"""
Covered call optimization - finds optimal strikes to sell calls against owned shares
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
from .simulation import monte_carlo_simulation
from .position_tracker import calculate_covered_call_pnl

def optimize_covered_calls(strikes: pd.Series,
                          deltas: pd.Series,
                          bids: pd.Series,
                          capital: float,
                          current_stock_price: float,
                          max_contracts_per_strike: int = 100,
                          n_simulations: int = 1000,
                          n_candidates: int = 50,
                          random_seed: Optional[int] = None) -> Dict:
    """
    Optimize covered call positions given capital to buy shares.
    
    For covered calls:
    1. Capital is used to buy shares (100 shares per contract)
    2. You sell call options and collect premium
    3. If calls expire ITM, shares are called away at strike
    4. If calls expire OTM, you keep shares and can sell them
    
    Args:
        strikes: Available strike prices
        deltas: Delta values (ITM probabilities)
        bids: Premium received per contract (for selling calls)
        capital: Total capital to buy shares
        current_stock_price: Current price to buy shares at
        max_contracts_per_strike: Maximum contracts per strike
        n_simulations: Number of Monte Carlo simulations
        n_candidates: Number of portfolio candidates to test
        random_seed: Optional seed for reproducibility
        
    Returns:
        Dictionary with optimal covered call positions
    """
    # Calculate how many shares we can buy with capital
    max_shares = int(capital / current_stock_price)
    max_contracts = max_shares // 100  # 100 shares per contract
    
    if max_contracts == 0:
        raise ValueError(f"Insufficient capital. Need at least ${current_stock_price * 100:.2f} for one contract")
    
    print(f"Capital: ${capital:,.2f} can buy {max_shares} shares = {max_contracts} contracts max")
    
    # Filter to reasonable strikes for covered calls (typically OTM or slightly ITM)
    # For covered calls, we usually want strikes above current price
    otm_mask = strikes >= current_stock_price
    reasonable_strikes = strikes[otm_mask]
    reasonable_deltas = deltas[otm_mask]
    reasonable_bids = bids[otm_mask]
    
    if len(reasonable_strikes) == 0:
        # If no OTM strikes, take slightly ITM
        reasonable_mask = strikes >= current_stock_price * 0.95
        reasonable_strikes = strikes[reasonable_mask]
        reasonable_deltas = deltas[reasonable_mask]
        reasonable_bids = bids[reasonable_mask]
    
    # Limit to strikes with decent premium
    min_premium = 0.50  # Minimum $0.50 premium
    good_premium_mask = reasonable_bids >= min_premium
    candidate_strikes = reasonable_strikes[good_premium_mask]
    candidate_deltas = reasonable_deltas[good_premium_mask]
    candidate_bids = reasonable_bids[good_premium_mask]
    
    if len(candidate_strikes) == 0:
        candidate_strikes = reasonable_strikes[:20]  # Take first 20 OTM
        candidate_deltas = reasonable_deltas[:20]
        candidate_bids = reasonable_bids[:20]
    
    best_result = None
    best_expected_pnl = -float('inf')
    
    # Test different portfolio combinations
    np.random.seed(random_seed)
    
    for _ in range(n_candidates):
        # Generate random portfolio
        positions = pd.Series(np.zeros(len(strikes)), index=strikes.index)
        
        # Randomly select strikes and quantities
        contracts_remaining = max_contracts
        while contracts_remaining > 0:
            # Pick a random candidate strike
            if len(candidate_strikes) == 0:
                break
            idx = np.random.choice(len(candidate_strikes))
            strike_idx = strikes[strikes == candidate_strikes.iloc[idx]].index[0]
            
            # Assign random quantity (up to remaining)
            qty = min(
                np.random.randint(1, min(10, contracts_remaining + 1)),
                contracts_remaining
            )
            positions.loc[strike_idx] = qty
            contracts_remaining -= qty
            
            if contracts_remaining == 0:
                break
        
        # Calculate covered call P&L for this portfolio
        # Simulate expiration prices
        expiration_prices = []
        for _ in range(n_simulations):
            # Use deltas as probabilities
            outcomes = np.random.random(len(strikes)) < deltas.values
            itm_strikes = strikes[outcomes]
            if len(itm_strikes) > 0:
                # Highest ITM strike
                exp_price = itm_strikes.max()
                # Add some randomness above the strike
                exp_price += np.random.random() * (strikes.iloc[min(len(strikes)-1, strikes[strikes > exp_price].index[0] if len(strikes[strikes > exp_price]) > 0 else len(strikes)-1)] - exp_price)
            else:
                # All OTM - price below lowest strike
                exp_price = strikes.min() * (0.7 + np.random.random() * 0.25)
            expiration_prices.append(exp_price)
        
        # Calculate P&L for each expiration scenario
        total_pnl = 0
        for exp_price in expiration_prices:
            pnl_result = calculate_covered_call_pnl(
                positions, strikes, bids, 
                current_stock_price, exp_price,
                contract_multiplier=100
            )
            total_pnl += pnl_result['net_pnl']
        
        expected_pnl = total_pnl / n_simulations
        
        # Track best result
        if expected_pnl > best_expected_pnl:
            best_expected_pnl = expected_pnl
            best_result = {
                'positions': positions,
                'expected_pnl': expected_pnl,
                'contracts_used': positions.sum()
            }
    
    # Convert best positions to dictionary
    best_positions = best_result['positions']
    position_dict = {
        float(strikes.iloc[i]): int(best_positions.iloc[i])
        for i in range(len(strikes)) if best_positions.iloc[i] > 0
    }
    
    # Calculate detailed metrics for best portfolio
    # Run more simulations for final result
    final_pnls = []
    for _ in range(n_simulations * 5):
        outcomes = np.random.random(len(strikes)) < deltas.values
        itm_strikes = strikes[outcomes]
        if len(itm_strikes) > 0:
            exp_price = itm_strikes.max() + np.random.random() * 2
        else:
            exp_price = strikes.min() * (0.7 + np.random.random() * 0.25)
        
        pnl_result = calculate_covered_call_pnl(
            best_positions, strikes, bids,
            current_stock_price, exp_price,
            contract_multiplier=100
        )
        final_pnls.append(pnl_result['net_pnl'])
    
    final_pnls = np.array(final_pnls)
    
    # Calculate statistics
    expected_pnl = final_pnls.mean()
    win_rate = (final_pnls > 0).mean() * 100
    var_95 = np.percentile(final_pnls, 5)
    max_gain = final_pnls.max()
    max_loss = final_pnls.min()
    
    # Calculate capital usage
    shares_needed = best_positions.sum() * 100
    capital_for_shares = shares_needed * current_stock_price
    premium_collected = (best_positions * bids * 100).sum()
    
    return {
        'optimal_positions': position_dict,
        'optimal_positions_vector': best_positions,
        'expected_pnl': expected_pnl,
        'win_rate': win_rate,
        'var_95': var_95,
        'max_gain': max_gain,
        'max_loss': max_loss,
        'contracts_sold': int(best_positions.sum()),
        'shares_needed': int(shares_needed),
        'capital_for_shares': capital_for_shares,
        'premium_collected': premium_collected,
        'net_capital_after_premium': capital_for_shares - premium_collected,
        'current_stock_price': current_stock_price,
        'return_on_capital': ((expected_pnl / capital_for_shares) * 100) if capital_for_shares > 0 else 0
    }


def optimize_covered_calls_continuous(strikes: pd.Series,
                                     deltas: pd.Series,
                                     bids: pd.Series,
                                     capital: float,
                                     current_stock_price: float,
                                     max_contracts: Optional[int] = None,
                                     n_simulations: int = 200,
                                     random_seed: Optional[int] = None) -> Dict:
    """
    Optimize covered call positions using enhanced random search.
    
    This version uses a more thorough search without scipy optimization
    to avoid pickling issues.
    """
    # Calculate maximum contracts based on capital
    max_shares = int(capital / current_stock_price)
    max_possible_contracts = max_shares // 100
    
    if max_contracts is None:
        max_contracts = max_possible_contracts
    else:
        max_contracts = min(max_contracts, max_possible_contracts)
    
    if max_contracts == 0:
        raise ValueError(f"Insufficient capital. Need at least ${current_stock_price * 100:.2f}")
    
    print(f"Max contracts available: {max_contracts}")
    
    # Filter to good strikes for covered calls
    # Focus on OTM strikes with decent premium
    otm_mask = (strikes >= current_stock_price) & (bids >= 0.25)
    good_strikes = strikes[otm_mask]
    good_deltas = deltas[otm_mask]
    good_bids = bids[otm_mask]
    
    if len(good_strikes) == 0:
        # Fall back to slightly ITM
        near_atm_mask = (strikes >= current_stock_price * 0.95) & (bids >= 0.10)
        good_strikes = strikes[near_atm_mask]
        good_deltas = deltas[near_atm_mask]
        good_bids = bids[near_atm_mask]
    
    # Limit to best candidates
    if len(good_strikes) > 20:
        # Take strikes with best premium/delta ratio
        premium_delta_ratio = good_bids / (good_deltas + 0.01)
        best_indices = premium_delta_ratio.nlargest(20).index
        good_strikes = good_strikes[best_indices]
        good_deltas = good_deltas[best_indices]
        good_bids = good_bids[best_indices]
    
    best_result = None
    best_expected_pnl = -float('inf')
    
    # Test more combinations for continuous optimization
    n_candidates = 200
    np.random.seed(random_seed)
    
    for candidate in range(n_candidates):
        # Create position vector
        positions = pd.Series(np.zeros(len(strikes)), index=strikes.index)
        
        # Strategy selection based on candidate number
        if candidate < 50:
            # Strategy 1: Concentrate on single strike
            if len(good_strikes) > 0:
                idx = np.random.choice(len(good_strikes))
                strike_idx = strikes[strikes == good_strikes.iloc[idx]].index[0]
                positions.loc[strike_idx] = max_contracts
        
        elif candidate < 100:
            # Strategy 2: Spread across 2-3 strikes
            n_strikes = min(3, len(good_strikes))
            if n_strikes > 0:
                selected_indices = np.random.choice(len(good_strikes), n_strikes, replace=False)
                contracts_per_strike = max_contracts // n_strikes
                remainder = max_contracts % n_strikes
                
                for i, idx in enumerate(selected_indices):
                    strike_idx = strikes[strikes == good_strikes.iloc[idx]].index[0]
                    positions.loc[strike_idx] = contracts_per_strike + (1 if i < remainder else 0)
        
        else:
            # Strategy 3: Random distribution weighted by premium
            if len(good_strikes) > 0:
                # Weight by premium
                weights = good_bids.values / good_bids.sum()
                contracts_remaining = max_contracts
                
                while contracts_remaining > 0 and len(good_strikes) > 0:
                    idx = np.random.choice(len(good_strikes), p=weights)
                    strike_idx = strikes[strikes == good_strikes.iloc[idx]].index[0]
                    
                    qty = min(
                        np.random.randint(1, min(10, contracts_remaining + 1)),
                        contracts_remaining
                    )
                    positions.loc[strike_idx] += qty
                    contracts_remaining -= qty
        
        # Evaluate this portfolio
        if positions.sum() > 0:
            total_pnl = 0
            for _ in range(n_simulations):
                # Simulate expiration
                outcomes = np.random.random(len(strikes)) < deltas.values
                itm_strikes = strikes[outcomes]
                if len(itm_strikes) > 0:
                    exp_price = itm_strikes.max() + np.random.random() * 2
                else:
                    exp_price = strikes.min() * (0.7 + np.random.random() * 0.25)
                
                pnl_result = calculate_covered_call_pnl(
                    positions, strikes, bids,
                    current_stock_price, exp_price,
                    contract_multiplier=100
                )
                total_pnl += pnl_result['net_pnl']
            
            expected_pnl = total_pnl / n_simulations
            
            if expected_pnl > best_expected_pnl:
                best_expected_pnl = expected_pnl
                best_result = positions.copy()
    
    # Use best result
    optimal_positions = best_result
    
    position_dict = {
        float(strikes.iloc[i]): int(optimal_positions.iloc[i])
        for i in range(len(strikes)) if optimal_positions.iloc[i] > 0
    }
    
    # Final evaluation with more simulations
    final_pnls = []
    for _ in range(n_simulations * 10):
        outcomes = np.random.random(len(strikes)) < deltas.values
        itm_strikes = strikes[outcomes]
        if len(itm_strikes) > 0:
            exp_price = itm_strikes.max() + np.random.random() * 2
        else:
            exp_price = strikes.min() * (0.7 + np.random.random() * 0.25)
        
        pnl_result = calculate_covered_call_pnl(
            optimal_positions, strikes, bids,
            current_stock_price, exp_price,
            contract_multiplier=100
        )
        final_pnls.append(pnl_result['net_pnl'])
    
    final_pnls = np.array(final_pnls)
    
    # Calculate metrics
    shares_needed = optimal_positions.sum() * 100
    capital_for_shares = shares_needed * current_stock_price
    premium_collected = (optimal_positions * bids * 100).sum()
    
    return {
        'optimal_positions': position_dict,
        'optimal_positions_vector': optimal_positions,
        'expected_pnl': final_pnls.mean(),
        'win_rate': (final_pnls > 0).mean() * 100,
        'var_95': np.percentile(final_pnls, 5),
        'max_gain': final_pnls.max(),
        'max_loss': final_pnls.min(),
        'contracts_sold': int(optimal_positions.sum()),
        'shares_needed': int(shares_needed),
        'capital_for_shares': capital_for_shares,
        'premium_collected': premium_collected,
        'net_capital_after_premium': capital_for_shares - premium_collected,
        'current_stock_price': current_stock_price,
        'return_on_capital': ((final_pnls.mean() / capital_for_shares) * 100) if capital_for_shares > 0 else 0,
        'optimization_success': True
    }