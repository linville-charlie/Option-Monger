#!/usr/bin/env python3
"""
Monte Carlo simulation using option deltas as probabilities
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional, List
import random


def simulate_expiration_price(strikes: pd.Series,
                             deltas: pd.Series,
                             positions: pd.Series,
                             random_seed: Optional[int] = None) -> float:
    """
    Simulate an expiration price using deltas as ITM probabilities.
    
    Each delta represents the probability that strike will be ITM at expiration.
    The function randomly determines which strike (if any) ends up being the 
    highest ITM strike, then generates an expiration price accordingly.
    
    Args:
        strikes: Strike prices Series
        deltas: Delta values Series (used as ITM probabilities)
        positions: Your position vector (to determine constraints)
        random_seed: Optional seed for reproducibility
        
    Returns:
        Simulated expiration price
        
    Example:
        # Positions at 220, 225, 230 with deltas 0.6, 0.5, 0.3
        expiration_price = simulate_expiration_price(strikes, deltas, positions)
        # Might return 227.35 (between 225 and 230 if 225 was highest ITM)
    """
    if random_seed is not None:
        np.random.seed(random_seed)
        random.seed(random_seed)
    
    # Get only positions we own
    owned_mask = positions > 0
    if not owned_mask.any():
        raise ValueError("No positions found")
    
    owned_strikes = strikes[owned_mask].values
    owned_deltas = deltas[owned_mask].values
    owned_indices = np.where(owned_mask)[0]
    
    # Sort by strike price
    sort_idx = np.argsort(owned_strikes)
    owned_strikes = owned_strikes[sort_idx]
    owned_deltas = owned_deltas[sort_idx]
    owned_indices = owned_indices[sort_idx]
    
    # Simulate ITM/OTM for each strike using delta as probability
    itm_results = np.random.random(len(owned_strikes)) < owned_deltas
    
    if not itm_results.any():
        # All OTM - price below lowest strike
        lowest_strike = owned_strikes[0]
        # Generate price 0-10% below lowest strike
        discount = np.random.beta(2, 5)  # Skewed toward smaller discounts
        expiration_price = lowest_strike * (1 - discount * 0.1)
    else:
        # Find highest ITM strike
        highest_itm_idx = np.where(itm_results)[0][-1]
        highest_itm_strike = owned_strikes[highest_itm_idx]
        
        # Check if there's a higher strike we own
        if highest_itm_idx < len(owned_strikes) - 1:
            # There's a higher strike - price between them
            next_strike = owned_strikes[highest_itm_idx + 1]
            # Uniform distribution between strikes
            expiration_price = np.random.uniform(highest_itm_strike, next_strike)
        else:
            # No higher strike - price up to 3% above
            # Use beta distribution skewed toward lower gains
            gain_pct = np.random.beta(2, 5) * 0.03  # Skewed toward 0-1%
            expiration_price = highest_itm_strike * (1 + gain_pct)
    
    return round(expiration_price, 2)


def monte_carlo_simulation(strikes: pd.Series,
                          deltas: pd.Series,
                          positions: pd.Series,
                          bids: pd.Series,
                          n_simulations: int = 10000,
                          random_seed: Optional[int] = None) -> dict:
    """
    Run Monte Carlo simulation for option positions using deltas as probabilities.
    
    Args:
        strikes: Strike prices
        deltas: Delta values (used as ITM probabilities)
        positions: Your position quantities
        bids: Bid prices (for P&L calculation)
        n_simulations: Number of simulations to run
        random_seed: Optional seed for reproducibility
        
    Returns:
        Dictionary with simulation results and statistics
        
    Example:
        results = monte_carlo_simulation(strikes, deltas, positions, bids, n_simulations=10000)
        print(f"Expected P&L: ${results['expected_pnl']:.2f}")
        print(f"Win rate: {results['win_rate']:.1f}%")
        print(f"95% VaR: ${results['var_95']:.2f}")
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Storage for results
    expiration_prices = []
    pnls = []
    itm_counts = []
    
    # Run simulations
    for i in range(n_simulations):
        # Simulate expiration price
        exp_price = simulate_expiration_price(
            strikes, deltas, positions, 
            random_seed=None if random_seed is None else random_seed + i
        )
        expiration_prices.append(exp_price)
        
        # Calculate P&L for this scenario
        intrinsic_values = np.maximum(exp_price - strikes, 0)
        premium_paid = positions * bids * 100
        intrinsic_received = positions * intrinsic_values * 100
        pnl = (intrinsic_received - premium_paid).sum()
        pnls.append(pnl)
        
        # Count ITM positions
        itm = (strikes <= exp_price) & (positions > 0)
        itm_counts.append(itm.sum())
    
    # Convert to arrays
    expiration_prices = np.array(expiration_prices)
    pnls = np.array(pnls)
    itm_counts = np.array(itm_counts)
    
    # Calculate statistics
    results = {
        'n_simulations': n_simulations,
        'expiration_prices': expiration_prices,
        'pnls': pnls,
        'expected_pnl': np.mean(pnls),
        'pnl_std': np.std(pnls),
        'min_pnl': np.min(pnls),
        'max_pnl': np.max(pnls),
        'median_pnl': np.median(pnls),
        'win_rate': (pnls > 0).mean() * 100,
        'avg_win': np.mean(pnls[pnls > 0]) if (pnls > 0).any() else 0,
        'avg_loss': np.mean(pnls[pnls <= 0]) if (pnls <= 0).any() else 0,
        'var_95': np.percentile(pnls, 5),  # 95% VaR
        'cvar_95': np.mean(pnls[pnls <= np.percentile(pnls, 5)]),  # Conditional VaR
        'avg_itm_positions': np.mean(itm_counts),
        'avg_expiration_price': np.mean(expiration_prices),
        'expiration_price_std': np.std(expiration_prices),
        'price_percentiles': {
            '5%': np.percentile(expiration_prices, 5),
            '25%': np.percentile(expiration_prices, 25),
            '50%': np.percentile(expiration_prices, 50),
            '75%': np.percentile(expiration_prices, 75),
            '95%': np.percentile(expiration_prices, 95),
        },
        'pnl_percentiles': {
            '5%': np.percentile(pnls, 5),
            '25%': np.percentile(pnls, 25),
            '50%': np.percentile(pnls, 50),
            '75%': np.percentile(pnls, 75),
            '95%': np.percentile(pnls, 95),
        }
    }
    
    return results


def analyze_position_outcomes(strikes: pd.Series,
                             deltas: pd.Series,
                             positions: pd.Series,
                             bids: pd.Series,
                             n_simulations: int = 1000) -> pd.DataFrame:
    """
    Analyze possible outcomes for each position using delta-based simulation.
    
    Returns a DataFrame showing probability of each strike being ITM and
    expected value calculations.
    
    Args:
        strikes: Strike prices
        deltas: Delta values
        positions: Position quantities
        bids: Bid prices
        n_simulations: Number of simulations
        
    Returns:
        DataFrame with outcome analysis for each position
    """
    # Run simulation
    sim_results = monte_carlo_simulation(
        strikes, deltas, positions, bids, n_simulations
    )
    
    # Analyze each position
    owned_mask = positions > 0
    analysis_data = []
    
    for idx in np.where(owned_mask)[0]:
        strike = strikes.iloc[idx]
        delta = deltas.iloc[idx]
        qty = positions.iloc[idx]
        bid = bids.iloc[idx]
        
        # Count how often this strike was ITM
        itm_count = np.sum(sim_results['expiration_prices'] >= strike)
        itm_prob = itm_count / n_simulations
        
        # Calculate expected value for this position
        premium_paid = qty * bid * 100
        
        # Average intrinsic value when ITM
        itm_prices = sim_results['expiration_prices'][sim_results['expiration_prices'] >= strike]
        if len(itm_prices) > 0:
            avg_intrinsic = np.mean(np.maximum(itm_prices - strike, 0)) * qty * 100
        else:
            avg_intrinsic = 0
        
        expected_value = (itm_prob * avg_intrinsic) - premium_paid
        
        analysis_data.append({
            'strike': strike,
            'quantity': qty,
            'delta': delta,
            'bid': bid,
            'premium_paid': premium_paid,
            'simulated_itm_prob': itm_prob,
            'delta_vs_simulated': delta - itm_prob,
            'avg_intrinsic_when_itm': avg_intrinsic,
            'expected_value': expected_value,
            'roi_pct': (expected_value / premium_paid * 100) if premium_paid > 0 else 0
        })
    
    return pd.DataFrame(analysis_data)