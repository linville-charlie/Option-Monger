#!/usr/bin/env python3
"""
Position tracking with binary vectors for bought/sold contracts
"""
import pandas as pd
import numpy as np
from typing import List, Union, Optional
from .simple_real_strikes import get_all_strikes


def create_position_vector(strikes: pd.Series, 
                           bought_strikes: Optional[Union[List[float], float, dict]] = None,
                           bought_indices: Optional[Union[List[int], int, dict]] = None,
                           quantities: Optional[Union[int, List[int]]] = None) -> pd.Series:
    """
    Create a position vector to represent how many contracts you bought.
    Same size as strikes/bids/deltas vectors with quantities (0, 1, 2, 3, etc.).
    
    Args:
        strikes: The strikes Series from get_all_strikes()
        bought_strikes: Strike price(s) you bought. Can be:
            - Single strike: 225.0
            - List of strikes: [220.0, 225.0, 230.0]
            - Dict with quantities: {220.0: 2, 225.0: 5, 230.0: 1}
        bought_indices: Index/indices of contracts you bought. Can be:
            - Single index: 45
            - List of indices: [45, 46, 47]
            - Dict with quantities: {45: 2, 46: 5, 47: 1}
        quantities: Quantity for each position (default 1). Can be:
            - Single quantity for all: 5
            - List matching strikes/indices: [2, 5, 1]
        
    Returns:
        pd.Series of quantities (0, 1, 2, ...), same length as strikes
        
    Examples:
        # Buy 1 contract at 225.0
        positions = create_position_vector(strikes, bought_strikes=225.0)
        
        # Buy 1 contract each at multiple strikes
        positions = create_position_vector(strikes, bought_strikes=[220.0, 225.0, 230.0])
        
        # Buy 5 contracts each at multiple strikes
        positions = create_position_vector(strikes, bought_strikes=[220.0, 225.0], quantities=5)
        
        # Buy different quantities at each strike
        positions = create_position_vector(strikes, bought_strikes=[220.0, 225.0, 230.0],
                                          quantities=[2, 5, 1])
        
        # Buy using dict (most flexible)
        positions = create_position_vector(strikes, bought_strikes={220.0: 2, 225.0: 5, 230.0: 1})
    """
    # Initialize with all zeros
    positions = pd.Series(np.zeros(len(strikes), dtype=int), 
                         index=strikes.index, 
                         name='positions')
    
    # Handle dict input for bought_strikes
    if isinstance(bought_strikes, dict):
        for strike, qty in bought_strikes.items():
            mask = strikes == strike
            if mask.any():
                positions[mask] = qty
            else:
                # Find closest strike if exact match not found
                closest_idx = np.abs(strikes - strike).argmin()
                positions.iloc[closest_idx] = qty
                print(f"Note: Exact strike ${strike:.2f} not found, using closest: ${strikes.iloc[closest_idx]:.2f}")
        return positions
    
    # Handle dict input for bought_indices
    if isinstance(bought_indices, dict):
        for idx, qty in bought_indices.items():
            if 0 <= idx < len(positions):
                positions.iloc[idx] = qty
            else:
                print(f"Warning: Index {idx} out of range (0-{len(positions)-1})")
        return positions
    
    # Handle list/single value inputs
    if bought_strikes is not None:
        if not isinstance(bought_strikes, list):
            bought_strikes = [bought_strikes]
        
        # Determine quantities for each strike
        if quantities is None:
            qtys = [1] * len(bought_strikes)  # Default to 1 contract each
        elif isinstance(quantities, int):
            qtys = [quantities] * len(bought_strikes)  # Same quantity for all
        else:
            qtys = quantities  # List of quantities
            if len(qtys) != len(bought_strikes):
                raise ValueError(f"Length of quantities ({len(qtys)}) must match strikes ({len(bought_strikes)})")
        
        for strike, qty in zip(bought_strikes, qtys):
            # Find exact match or closest strike
            mask = strikes == strike
            if mask.any():
                positions[mask] = qty
            else:
                # Find closest strike if exact match not found
                closest_idx = np.abs(strikes - strike).argmin()
                positions.iloc[closest_idx] = qty
                print(f"Note: Exact strike ${strike:.2f} not found, using closest: ${strikes.iloc[closest_idx]:.2f}")
    
    if bought_indices is not None:
        if not isinstance(bought_indices, list):
            bought_indices = [bought_indices]
        
        # Determine quantities for each index
        if quantities is None:
            qtys = [1] * len(bought_indices)
        elif isinstance(quantities, int):
            qtys = [quantities] * len(bought_indices)
        else:
            qtys = quantities
            if len(qtys) != len(bought_indices):
                raise ValueError(f"Length of quantities ({len(qtys)}) must match indices ({len(bought_indices)})")
        
        for idx, qty in zip(bought_indices, qtys):
            if 0 <= idx < len(positions):
                positions.iloc[idx] = qty
            else:
                print(f"Warning: Index {idx} out of range (0-{len(positions)-1})")
    
    return positions


def create_spread_vectors(strikes: pd.Series,
                         long_strikes: Optional[Union[List[float], float]] = None,
                         short_strikes: Optional[Union[List[float], float]] = None,
                         long_indices: Optional[Union[List[int], int]] = None,
                         short_indices: Optional[Union[List[int], int]] = None) -> tuple:
    """
    Create two vectors for spread positions: one for long, one for short.
    
    Returns:
        Tuple of (long_positions, short_positions) both pd.Series
        long_positions: 1s for bought contracts, 0s elsewhere
        short_positions: 1s for sold contracts, 0s elsewhere
    """
    long_positions = create_position_vector(strikes, long_strikes, long_indices)
    long_positions.name = 'long_positions'
    
    short_positions = create_position_vector(strikes, short_strikes, short_indices)
    short_positions.name = 'short_positions'
    
    return long_positions, short_positions


def create_weighted_position_vector(strikes: pd.Series,
                                   positions_dict: dict) -> pd.Series:
    """
    Create a weighted position vector where values represent quantity.
    Positive = long, Negative = short, 0 = no position.
    
    Args:
        strikes: The strikes Series
        positions_dict: Dict of {strike_price: quantity} or {index: quantity}
                       Positive quantity = long, negative = short
                       
    Example:
        # Buy 2 contracts at 225, sell 1 at 230
        positions = create_weighted_position_vector(strikes, {
            225.0: 2,   # Long 2 contracts
            230.0: -1   # Short 1 contract
        })
    """
    positions = pd.Series(np.zeros(len(strikes)), 
                         index=strikes.index, 
                         name='weighted_positions')
    
    for key, quantity in positions_dict.items():
        if isinstance(key, (int, np.integer)):
            # It's an index
            if 0 <= key < len(positions):
                positions.iloc[key] = quantity
        else:
            # It's a strike price
            mask = strikes == key
            if mask.any():
                positions[mask] = quantity
            else:
                # Find closest strike
                closest_idx = np.abs(strikes - key).argmin()
                positions.iloc[closest_idx] = quantity
                print(f"Note: Using closest strike ${strikes.iloc[closest_idx]:.2f} for ${key:.2f}")
    
    return positions


def create_itm_vector(strikes: pd.Series, 
                     hit_strike: float,
                     option_type: str = 'C') -> pd.Series:
    """
    Create a binary vector marking which strikes are in-the-money (ITM).
    
    Args:
        strikes: The strikes Series from get_all_strikes()
        hit_strike: The strike price that was hit (underlying price at expiration)
        option_type: 'C' for calls, 'P' for puts
        
    Returns:
        pd.Series of 1s and 0s:
        - For calls: 1 if strike <= hit_strike (ITM), 0 otherwise
        - For puts: 1 if strike >= hit_strike (ITM), 0 otherwise
        
    Example:
        # Stock expires at $227.50
        itm = create_itm_vector(strikes, hit_strike=227.50)
        # Now itm[i] = 1 for all strikes <= 227.50 (ITM calls)
        
        # Calculate profit for your positions
        intrinsic_value = np.maximum(227.50 - strikes, 0)
        profit = (intrinsic_value - bids) * positions * itm
    """
    itm = pd.Series(np.zeros(len(strikes), dtype=int),
                    index=strikes.index,
                    name='itm')
    
    if option_type.upper() == 'C':
        # Calls are ITM when strike <= underlying price
        itm[strikes <= hit_strike] = 1
    else:
        # Puts are ITM when strike >= underlying price
        itm[strikes >= hit_strike] = 1
    
    return itm


def create_exercise_vector(strikes: pd.Series,
                          positions: pd.Series,
                          hit_strike: float,
                          option_type: str = 'C') -> pd.Series:
    """
    Create a vector showing which of YOUR positions would be exercised.
    Combines your position vector with ITM status.
    
    Args:
        strikes: The strikes Series
        positions: Your position vector (1s and 0s for owned contracts)
        hit_strike: The underlying price at expiration
        option_type: 'C' for calls, 'P' for puts
        
    Returns:
        pd.Series where 1 = you own this contract AND it's ITM
        
    Example:
        # You bought calls at 220, 225, 230
        positions = create_position_vector(strikes, bought_strikes=[220, 225, 230])
        
        # Stock expires at 227.50
        exercised = create_exercise_vector(strikes, positions, hit_strike=227.50)
        # exercised = 1 only for 220 and 225 (ITM), 0 for 230 (OTM)
    """
    itm = create_itm_vector(strikes, hit_strike, option_type)
    exercised = positions * itm  # 1 only where both are 1
    exercised.name = 'exercised'
    return exercised


def calculate_premium_paid_for_itm(positions: pd.Series,
                                   itm: pd.Series,
                                   bids: pd.Series,
                                   contract_multiplier: int = 100) -> pd.Series:
    """
    Calculate premium paid for ITM positions using Hadamard (element-wise) multiplication.
    
    Performs: positions ⊙ itm ⊙ (bids × 100)
    
    Works with quantities: if positions[i] = 5, calculates premium for 5 contracts.
    
    Args:
        positions: Vector of quantities (0, 1, 2, 3, ...) for each strike
        itm: Binary vector of ITM strikes (1s and 0s)
        bids: Vector of bid prices
        contract_multiplier: Options multiplier (default 100 shares per contract)
        
    Returns:
        pd.Series showing total premium paid for each ITM position
        
    Example:
        # You bought 2 contracts at 220, 5 at 225, 1 at 230
        positions = create_position_vector(strikes, bought_strikes={220: 2, 225: 5, 230: 1})
        
        # Stock expires at 227.50
        itm = create_itm_vector(strikes, hit_strike=227.50)
        
        # Calculate premium paid for ITM positions
        premium_paid = calculate_premium_paid_for_itm(positions, itm, bids)
        # Result: [0, ..., 1892, 2245, 0, ...] (2×946 for 220, 5×449 for 225, 0 for 230)
        
        total_premium_itm = premium_paid.sum()
        print(f"Total premium paid for ITM contracts: ${total_premium_itm:.2f}")
    """
    # Hadamard multiplication: positions ⊙ itm ⊙ (bids × 100)
    premium_paid = positions * itm * (bids * contract_multiplier)
    premium_paid.name = 'premium_paid_itm'
    
    return premium_paid


def calculate_net_pnl_vectors(positions: pd.Series,
                              itm: pd.Series,
                              strikes: pd.Series,
                              bids: pd.Series,
                              hit_strike: float,
                              contract_multiplier: int = 100) -> dict:
    """
    Calculate P&L vectors using Hadamard multiplication for ITM positions.
    
    Args:
        positions: Binary vector of bought contracts
        itm: Binary vector of ITM strikes  
        strikes: Vector of strike prices
        bids: Vector of bid prices
        hit_strike: Where the stock expired
        contract_multiplier: Options multiplier (default 100)
        
    Returns:
        Dictionary with various P&L vectors and totals
        
    Example:
        results = calculate_net_pnl_vectors(positions, itm, strikes, bids, 227.50)
        print(f"Total P&L: ${results['total_pnl']:.2f}")
    """
    # Premium paid for ITM positions (Hadamard: positions ⊙ itm ⊙ bids)
    premium_paid_vec = positions * itm * bids * contract_multiplier
    
    # Intrinsic value received for ITM positions
    intrinsic_per_share = np.maximum(hit_strike - strikes, 0)
    intrinsic_received_vec = positions * itm * intrinsic_per_share * contract_multiplier
    
    # Net P&L per position
    pnl_vec = intrinsic_received_vec - premium_paid_vec
    
    # Filter to only positions that matter
    active_positions = positions == 1
    itm_positions = (positions == 1) & (itm == 1)
    otm_positions = (positions == 1) & (itm == 0)
    
    results = {
        'premium_paid_vector': premium_paid_vec,
        'intrinsic_received_vector': intrinsic_received_vec,
        'pnl_vector': pnl_vec,
        'total_premium_paid_itm': premium_paid_vec.sum(),
        'total_premium_paid_all': (positions * bids * contract_multiplier).sum(),
        'total_intrinsic_received': intrinsic_received_vec.sum(),
        'total_pnl': pnl_vec.sum(),
        'itm_strikes': strikes[itm_positions].tolist(),
        'otm_strikes': strikes[otm_positions].tolist(),
        'itm_count': itm_positions.sum(),
        'otm_count': otm_positions.sum()
    }
    
    return results


def calculate_otm_share_sale_value(positions: pd.Series,
                                  itm: pd.Series,
                                  stock_price: float,
                                  contract_multiplier: int = 100) -> pd.Series:
    """
    Calculate proceeds from selling shares for OTM covered calls.
    
    For covered calls that expire OTM, you keep the shares and sell them
    immediately at the current stock price.
    
    Performs: positions ⊙ (1 - itm) × stock_price × 100
    
    Args:
        positions: Vector of covered call positions (quantities)
        itm: Binary vector of ITM strikes (1s and 0s)
        stock_price: Current stock price to sell shares at
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        pd.Series showing share sale proceeds for OTM positions
        
    Example:
        # You sold covered calls: 5 at 220, 10 at 225, 2 at 230
        positions = create_position_vector(strikes, {220: 5, 225: 10, 230: 2})
        
        # Stock closes at 227.50, so 230 strike is OTM
        itm = create_itm_vector(strikes, hit_strike=227.50)
        
        # Sell the shares from OTM 230 contracts at $227.50
        share_proceeds = calculate_otm_share_sale_value(positions, itm, stock_price=227.50)
        # Result: [0, ..., 0, 45500, ...] (2 contracts × 100 shares × $227.50 = $45,500)
        
        total_share_proceeds = share_proceeds.sum()
        print(f"Total from selling shares (OTM contracts): ${total_share_proceeds:.2f}")
    """
    # Create OTM mask (inverse of ITM)
    otm = 1 - itm  # 1 where OTM, 0 where ITM
    
    # Hadamard multiplication: positions ⊙ otm × stock_price × 100
    share_sale_value = positions * otm * stock_price * contract_multiplier
    share_sale_value.name = 'otm_share_sale_value'
    
    return share_sale_value


# Keep old function for backward compatibility
def calculate_otm_sale_value(positions: pd.Series,
                            itm: pd.Series,
                            sale_price: float,
                            contract_multiplier: int = 100) -> pd.Series:
    """Legacy function - use calculate_otm_share_sale_value instead"""
    return calculate_otm_share_sale_value(positions, itm, sale_price, contract_multiplier)


def calculate_complete_pnl_with_otm_sale(positions: pd.Series,
                                        bids: pd.Series,
                                        strikes: pd.Series,
                                        hit_price: float,
                                        otm_sale_price: float = 0,
                                        contract_multiplier: int = 100) -> dict:
    """
    Calculate complete P&L including selling OTM contracts before expiration.
    
    Args:
        positions: Your position vector (quantities)
        bids: Original bid prices when you bought
        strikes: Strike prices
        hit_price: Stock price at expiration
        otm_sale_price: Price per contract for selling OTM options (0 = hold to expiry)
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        Dictionary with complete P&L breakdown including OTM sales
        
    Example:
        # Bought options
        positions = create_positions(strikes, {220: 5, 225: 10, 230: 2})
        
        # Stock at 227.50, sell OTM 230s for $0.30 each
        results = calculate_complete_pnl_with_otm_sale(
            positions, bids, strikes, 
            hit_price=227.50, 
            otm_sale_price=0.30
        )
        
        print(f"Premium paid: ${results['total_premium_paid']:.2f}")
        print(f"ITM intrinsic received: ${results['itm_intrinsic_received']:.2f}")
        print(f"OTM sale proceeds: ${results['otm_sale_proceeds']:.2f}")
        print(f"Total P&L: ${results['total_pnl_with_sale']:.2f}")
    """
    # Create ITM mask
    itm = create_itm_vector(strikes, hit_price, 'C')
    
    # Premium paid for all positions
    premium_paid = positions * bids * contract_multiplier
    total_premium = premium_paid.sum()
    
    # Intrinsic value for ITM positions
    intrinsic_per_share = np.maximum(hit_price - strikes, 0)
    itm_intrinsic = positions * itm * intrinsic_per_share * contract_multiplier
    total_itm_intrinsic = itm_intrinsic.sum()
    
    # Sale proceeds for OTM positions
    otm_sale = calculate_otm_sale_value(positions, itm, otm_sale_price, contract_multiplier)
    total_otm_sale = otm_sale.sum()
    
    # Total P&L
    total_received = total_itm_intrinsic + total_otm_sale
    total_pnl = total_received - total_premium
    
    # Breakdown by position
    otm = 1 - itm
    itm_positions = (positions > 0) & (itm == 1)
    otm_positions = (positions > 0) & (otm == 1)
    
    results = {
        'hit_price': hit_price,
        'otm_sale_price': otm_sale_price,
        'total_positions': positions[positions > 0].sum(),
        'itm_count': (positions * itm)[positions > 0].sum(),
        'otm_count': (positions * otm)[positions > 0].sum(),
        'itm_strikes': strikes[itm_positions].tolist(),
        'otm_strikes': strikes[otm_positions].tolist(),
        'total_premium_paid': total_premium,
        'itm_intrinsic_received': total_itm_intrinsic,
        'otm_sale_proceeds': total_otm_sale,
        'total_received': total_received,
        'total_pnl_without_sale': total_itm_intrinsic - total_premium,
        'total_pnl_with_sale': total_pnl,
        'pnl_improvement_from_sale': total_otm_sale
    }
    
    return results


def calculate_share_cost_basis(positions: pd.Series,
                              initial_share_price: float,
                              contract_multiplier: int = 100) -> pd.Series:
    """
    Calculate the cost basis for shares underlying your option positions.
    
    Formula: positions × initial_share_price × 100
    
    This calculates how much you paid for the shares when you initially bought them
    (for covered calls) or would pay if exercised (for long calls).
    
    Args:
        positions: Vector of contract quantities for each strike
        initial_share_price: Price you paid per share when buying
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        pd.Series showing total cost basis for shares at each strike
        
    Example:
        # You bought shares at $200 to cover these calls
        positions = create_position_vector(strikes, {220: 5, 225: 10, 230: 2})
        
        # Calculate cost basis
        cost_basis = calculate_share_cost_basis(positions, initial_share_price=200.0)
        # Result: [0, ..., 100000, ..., 200000, ..., 40000, ...]
        # 220: 5 contracts × 100 shares × $200 = $100,000
        # 225: 10 contracts × 100 shares × $200 = $200,000
        # 230: 2 contracts × 100 shares × $200 = $40,000
        
        total_cost = cost_basis.sum()
        print(f"Total cost basis for shares: ${total_cost:,.2f}")
    """
    # Scalar multiplication: positions × initial_share_price × 100
    cost_basis = positions * initial_share_price * contract_multiplier
    cost_basis.name = 'share_cost_basis'
    
    return cost_basis


def calculate_covered_call_pnl(positions: pd.Series,
                              strikes: pd.Series,
                              bids: pd.Series,
                              initial_share_price: float,
                              expiration_price: float,
                              contract_multiplier: int = 100) -> dict:
    """
    Calculate complete P&L for covered call positions.
    
    Args:
        positions: Your covered call positions (calls sold)
        strikes: Strike prices
        bids: Premium collected per contract
        initial_share_price: What you paid for the shares
        expiration_price: Stock price at expiration
        contract_multiplier: Shares per contract (default 100)
        
    Returns:
        Dictionary with complete P&L breakdown
        
    Example:
        positions = create_positions(strikes, {220: 5, 225: 10})
        results = calculate_covered_call_pnl(
            positions, strikes, bids,
            initial_share_price=200.0,
            expiration_price=227.50
        )
    """
    # Cost basis for shares
    share_cost = calculate_share_cost_basis(positions, initial_share_price, contract_multiplier)
    total_share_cost = share_cost.sum()
    
    # Premium collected from selling calls
    premium_collected = (positions * bids * contract_multiplier).sum()
    
    # ITM/OTM determination
    itm = create_itm_vector(strikes, expiration_price, 'C')
    
    # ITM: shares called away at strike
    itm_proceeds = (positions * itm * strikes * contract_multiplier).sum()
    
    # OTM: sell shares at market
    otm_proceeds = calculate_otm_share_sale_value(positions, itm, expiration_price, contract_multiplier).sum()
    
    # Total proceeds
    total_proceeds = itm_proceeds + otm_proceeds + premium_collected
    
    # P&L
    net_pnl = total_proceeds - total_share_cost
    
    results = {
        'initial_share_price': initial_share_price,
        'expiration_price': expiration_price,
        'total_positions': positions[positions > 0].sum(),
        'total_share_cost': total_share_cost,
        'premium_collected': premium_collected,
        'itm_proceeds': itm_proceeds,
        'otm_proceeds': otm_proceeds,
        'total_proceeds': total_proceeds,
        'net_pnl': net_pnl,
        'return_pct': (net_pnl / total_share_cost * 100) if total_share_cost > 0 else 0
    }
    
    return results


def hadamard_multiply(*vectors) -> pd.Series:
    """
    Perform Hadamard (element-wise) multiplication on multiple vectors.
    
    Args:
        *vectors: Any number of pd.Series vectors of the same length
        
    Returns:
        pd.Series result of element-wise multiplication
        
    Example:
        result = hadamard_multiply(positions, itm, bids * 100)
        # Equivalent to: positions ⊙ itm ⊙ (bids × 100)
    """
    if not vectors:
        raise ValueError("At least one vector required")
    
    result = vectors[0].copy()
    for vec in vectors[1:]:
        result = result * vec
    
    return result


def calculate_expiration_value(strikes: pd.Series,
                              bids: pd.Series,
                              positions: pd.Series,
                              hit_strike: float,
                              option_type: str = 'C') -> dict:
    """
    Calculate P&L at expiration given where the stock closed.
    
    Args:
        strikes, bids: The strike and bid vectors
        positions: Your position vector (positive = long, negative = short)
        hit_strike: The underlying price at expiration
        option_type: 'C' for calls, 'P' for puts
        
    Returns:
        Dictionary with P&L breakdown
    """
    # Calculate intrinsic value at expiration
    if option_type.upper() == 'C':
        intrinsic_values = np.maximum(hit_strike - strikes, 0)
    else:
        intrinsic_values = np.maximum(strikes - hit_strike, 0)
    
    # P&L for each position
    # Long positions: receive intrinsic value, paid bid
    # Short positions: pay intrinsic value, received bid
    position_pnl = positions * (intrinsic_values - bids)
    
    # Separate long and short
    long_mask = positions > 0
    short_mask = positions < 0
    
    results = {
        'hit_strike': hit_strike,
        'total_positions': positions[positions != 0].sum(),
        'itm_positions': ((positions != 0) & (intrinsic_values > 0)).sum(),
        'long_pnl': position_pnl[long_mask].sum() if long_mask.any() else 0,
        'short_pnl': position_pnl[short_mask].sum() if short_mask.any() else 0,
        'total_pnl': position_pnl.sum(),
        'max_intrinsic': intrinsic_values[positions != 0].max() if (positions != 0).any() else 0,
        'exercised_strikes': strikes[(positions != 0) & (intrinsic_values > 0)].tolist()
    }
    
    return results


def calculate_position_metrics(bids: pd.Series, 
                              strikes: pd.Series, 
                              deltas: pd.Series,
                              positions: pd.Series) -> dict:
    """
    Calculate metrics for your position vector.
    
    Args:
        bids, strikes, deltas: The three main vectors
        positions: Your position vector (binary or weighted)
        
    Returns:
        Dictionary with position metrics
    """
    # For binary positions (1s and 0s)
    if set(positions.unique()).issubset({0, 1, -1}):
        long_mask = positions == 1
        short_mask = positions == -1
        
        metrics = {
            'total_long_contracts': long_mask.sum(),
            'total_short_contracts': short_mask.sum(),
            'net_contracts': long_mask.sum() - short_mask.sum(),
            'long_strikes': strikes[long_mask].tolist(),
            'short_strikes': strikes[short_mask].tolist(),
            'total_long_premium': bids[long_mask].sum(),
            'total_short_premium': bids[short_mask].sum(),
            'net_debit': bids[long_mask].sum() - bids[short_mask].sum(),
            'net_delta': deltas[long_mask].sum() - deltas[short_mask].sum(),
        }
    else:
        # For weighted positions
        long_mask = positions > 0
        short_mask = positions < 0
        
        metrics = {
            'total_long_contracts': positions[long_mask].sum(),
            'total_short_contracts': abs(positions[short_mask].sum()),
            'net_contracts': positions.sum(),
            'long_strikes': strikes[long_mask].tolist(),
            'short_strikes': strikes[short_mask].tolist(),
            'total_long_premium': (bids * positions)[long_mask].sum(),
            'total_short_premium': abs((bids * positions)[short_mask].sum()),
            'net_debit': (bids * positions).sum(),
            'net_delta': (deltas * positions).sum(),
        }
    
    return metrics


def demo_position_tracking():
    """Demonstrate position tracking with the vectors"""
    
    print("POSITION TRACKING DEMONSTRATION")
    print("="*70)
    
    # Get the base vectors
    print("\n1. Getting option data...")
    bids, strikes, deltas = get_all_strikes('AAPL', '20250117', use_live_data=False)
    print(f"   Got {len(strikes)} strikes")
    
    # Example 1: Simple long position
    print("\n2. Example: Buy single call at $225 strike")
    positions = create_position_vector(strikes, bought_strikes=225.0)
    print(f"   Position vector sum: {positions.sum()} (bought {positions.sum()} contracts)")
    idx = positions[positions == 1].index[0]
    print(f"   Bought: Strike ${strikes.iloc[idx]:.2f} @ ${bids.iloc[idx]:.2f} (Δ={deltas.iloc[idx]:.4f})")
    
    # Example 2: Multiple positions
    print("\n3. Example: Buy multiple calls")
    positions = create_position_vector(strikes, bought_strikes=[220.0, 225.0, 230.0])
    print(f"   Position vector sum: {positions.sum()} (bought {positions.sum()} contracts)")
    for idx in positions[positions == 1].index:
        print(f"   Bought: Strike ${strikes.iloc[idx]:.2f} @ ${bids.iloc[idx]:.2f}")
    
    # Example 3: Vertical spread
    print("\n4. Example: Vertical Spread (Buy 220, Sell 230)")
    long_pos, short_pos = create_spread_vectors(strikes, 
                                                long_strikes=220.0,
                                                short_strikes=230.0)
    net_positions = long_pos - short_pos  # Net position: +1 for long, -1 for short
    print(f"   Long positions: {long_pos.sum()} contracts")
    print(f"   Short positions: {short_pos.sum()} contracts")
    
    # Calculate spread metrics
    metrics = calculate_position_metrics(bids, strikes, deltas, net_positions)
    print(f"   Net debit: ${metrics['net_debit']:.2f}")
    print(f"   Net delta: {metrics['net_delta']:.4f}")
    
    # Example 4: Buy by delta
    print("\n5. Example: Buy all options with delta between 0.4 and 0.6")
    delta_mask = (deltas >= 0.4) & (deltas <= 0.6)
    positions = pd.Series(delta_mask.astype(int), name='positions')
    print(f"   Bought {positions.sum()} contracts")
    print(f"   Strikes: {strikes[positions == 1].tolist()[:5]}...")  # Show first 5
    
    # Example 5: Weighted positions
    print("\n6. Example: Iron Condor (weighted positions)")
    # Buy 1 put at 210, Sell 1 put at 215
    # Sell 1 call at 235, Buy 1 call at 240
    weighted = create_weighted_position_vector(strikes, {
        210.0: 1,   # Long put (simulated as call for demo)
        215.0: -1,  # Short put
        235.0: -1,  # Short call
        240.0: 1    # Long call
    })
    print(f"   Total positions: {weighted[weighted != 0].to_dict()}")
    metrics = calculate_position_metrics(bids, strikes, deltas, weighted)
    print(f"   Net debit: ${metrics['net_debit']:.2f}")
    print(f"   Net delta: {metrics['net_delta']:.4f}")
    
    return positions


def show_usage():
    """Show how to use position vectors in your strategy"""
    
    print("\n" + "="*70)
    print("HOW TO USE IN YOUR STRATEGY")
    print("="*70)
    
    print("""
# Get your base vectors
from .simple_real_strikes import get_all_strikes
from position_tracker import create_position_vector

bids, strikes, deltas = get_all_strikes('AAPL', '20250117')

# Create position vector for contracts you bought
positions = create_position_vector(strikes, bought_strikes=[220.0, 225.0])

# Now you have FOUR aligned vectors:
# - strikes[i]: strike price
# - bids[i]: bid price
# - deltas[i]: delta
# - positions[i]: 1 if you bought this contract, 0 otherwise

# Calculate your position cost
total_cost = (bids * positions).sum()
print(f"Total cost: ${total_cost:.2f}")

# Calculate your position delta
total_delta = (deltas * positions).sum()
print(f"Total delta: {total_delta:.4f}")

# Find which contracts you own
my_strikes = strikes[positions == 1]
print(f"You own strikes: {my_strikes.tolist()}")
""")


if __name__ == "__main__":
    # Run demonstration
    positions = demo_position_tracking()
    
    # Show usage
    show_usage()
    
    print("\n" + "="*70)
    print("POSITION VECTOR CREATED SUCCESSFULLY!")
    print("="*70)
    print("You now have a fourth vector that tracks your positions.")
    print("It's the same size and alignment as your other three vectors.")