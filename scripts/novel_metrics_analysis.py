#!/usr/bin/env python3
"""
Novel Inflation Metrics: Quantitative Analysis

This script constructs several of the metrics proposed in Section 6 of
"Measuring What Matters" using publicly available data.

Metrics Constructed:
1. Time-Cost Index: Hours of median-wage work to purchase specific goods
2. Necessity vs. Discretionary CPI: Separate tracking of essential vs. optional spending
3. Asset-Adjusted Inflation: CPI augmented with financial and real asset prices
4. First-Time Buyer Affordability Index: Hours of work for housing down payment

Data Sources:
- Bureau of Labor Statistics (wages, prices, CPI components)
- Federal Reserve Economic Data (FRED)
- Case-Shiller Index (housing)
- S&P 500 (financial assets)
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14

os.makedirs('figures', exist_ok=True)

# =============================================================================
# DATA: Compiled from BLS, FRED, and other public sources
# =============================================================================

# Years for analysis
years = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024]

# Median hourly wage (all workers, nominal dollars)
# Source: BLS Current Population Survey / FRED
median_hourly_wage = {
    1990: 10.01,
    1995: 11.43,
    2000: 13.74,
    2005: 15.57,
    2010: 16.71,
    2015: 17.98,
    2020: 19.33,
    2024: 23.53  # Q3 2024 estimate
}

# Average prices for common goods (BLS Average Price Data)
# Milk (per gallon)
milk_price = {
    1990: 2.15,
    1995: 2.48,
    2000: 2.78,
    2005: 3.24,
    2010: 3.32,
    2015: 3.42,
    2020: 3.54,
    2024: 4.05
}

# Eggs (per dozen, Grade A large)
egg_price = {
    1990: 1.01,
    1995: 1.16,
    2000: 0.96,
    2005: 1.35,
    2010: 1.79,
    2015: 2.03,
    2020: 1.48,
    2024: 3.20  # Elevated due to avian flu
}

# Ground beef (per pound)
beef_price = {
    1990: 1.63,
    1995: 1.54,
    2000: 1.63,
    2005: 2.30,
    2010: 2.89,
    2015: 4.24,
    2020: 4.17,
    2024: 5.44
}

# Gasoline (per gallon, regular)
gas_price = {
    1990: 1.16,
    1995: 1.15,
    2000: 1.51,
    2005: 2.30,
    2010: 2.79,
    2015: 2.43,
    2020: 2.17,
    2024: 3.31
}

# Median home price (existing single-family)
# Source: Federal Reserve, NAR
home_price = {
    1990: 95500,
    1995: 113100,
    2000: 139000,
    2005: 219600,
    2010: 173100,
    2015: 223900,
    2020: 296500,
    2024: 412300
}

# S&P 500 index (year-end)
sp500 = {
    1990: 330,
    1995: 616,
    2000: 1320,
    2005: 1248,
    2010: 1258,
    2015: 2044,
    2020: 3756,
    2024: 5881
}

# Case-Shiller National Home Price Index (Jan 2000 = 100)
case_shiller = {
    1990: 63.0,  # Estimated backcast
    1995: 72.4,  # Estimated backcast
    2000: 100.0,
    2005: 151.3,
    2010: 126.7,
    2015: 152.5,
    2020: 199.6,
    2024: 318.0
}

# CPI-U (1982-84 = 100)
cpi_u = {
    1990: 130.7,
    1995: 152.4,
    2000: 172.2,
    2005: 195.3,
    2010: 218.1,
    2015: 237.0,
    2020: 258.8,
    2024: 314.5
}

# CPI component weights (approximate, 2024)
# Necessities: shelter, food, energy, medical care, transportation (basic)
# Discretionary: recreation, apparel, education/communication, other
necessity_weight = 0.70  # ~70% of CPI is necessities
discretionary_weight = 0.30

# Approximate necessity vs discretionary inflation rates by period
# Based on BLS component data showing necessities rose faster 2020-2024
necessity_inflation = {
    (1990, 2000): 2.8,  # Annual %
    (2000, 2010): 2.6,
    (2010, 2020): 1.9,
    (2020, 2024): 5.8   # Higher due to shelter, food, energy
}

discretionary_inflation = {
    (1990, 2000): 2.1,
    (2000, 2010): 1.8,
    (2010, 2020): 0.9,
    (2020, 2024): 3.2
}

# =============================================================================
# METRIC 1: Time-Cost Index
# Minutes of median-wage work to purchase one unit of each good
# =============================================================================

def calculate_time_cost():
    """Calculate minutes of work needed to purchase common goods."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    goods = [
        ('Gallon of Milk', milk_price, axes[0, 0]),
        ('Dozen Eggs', egg_price, axes[0, 1]),
        ('Pound of Ground Beef', beef_price, axes[1, 0]),
        ('Gallon of Gasoline', gas_price, axes[1, 1])
    ]

    results = {}

    for name, prices, ax in goods:
        minutes = []
        for year in years:
            hourly_wage = median_hourly_wage[year]
            price = prices[year]
            mins = (price / hourly_wage) * 60
            minutes.append(mins)

        results[name] = dict(zip(years, minutes))

        # Plot
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(years)))
        bars = ax.bar([str(y) for y in years], minutes, color=colors, edgecolor='black', linewidth=0.5)

        # Add value labels
        for bar, val in zip(bars, minutes):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9)

        ax.set_ylabel('Minutes of Work')
        ax.set_xlabel('Year')
        ax.set_title(f'Time-Cost: {name}', fontweight='bold')

        # Calculate change
        change_90_24 = ((minutes[-1] - minutes[0]) / minutes[0]) * 100
        ax.text(0.95, 0.95, f'{change_90_24:+.1f}% since 1990',
                transform=ax.transAxes, ha='right', va='top',
                fontsize=10, color='#c0392b' if change_90_24 > 0 else '#27ae60',
                fontweight='bold')

    plt.suptitle('Time-Cost Index: Minutes of Median-Wage Work to Purchase Common Goods\n'
                 '(Lower = More Affordable)', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('figures/fig_time_cost_index.png', dpi=150, bbox_inches='tight')
    plt.close()

    return results

# =============================================================================
# METRIC 2: Necessity vs Discretionary CPI
# Separate indices for essential vs optional spending
# =============================================================================

def calculate_necessity_discretionary():
    """
    Construct separate inflation indices for necessities vs discretionary goods.
    Uses BLS component weights and category-specific inflation rates.
    """

    # Build indices starting from 1990 = 100
    necessity_index = {1990: 100}
    discretionary_index = {1990: 100}
    overall_index = {1990: 100}

    periods = [(1990, 2000), (2000, 2010), (2010, 2020), (2020, 2024)]

    for start, end in periods:
        years_in_period = end - start
        nec_rate = necessity_inflation[(start, end)] / 100
        disc_rate = discretionary_inflation[(start, end)] / 100

        # Compound growth
        necessity_index[end] = necessity_index[start] * ((1 + nec_rate) ** years_in_period)
        discretionary_index[end] = discretionary_index[start] * ((1 + disc_rate) ** years_in_period)

        # Overall is weighted average
        overall_rate = (necessity_weight * nec_rate + discretionary_weight * disc_rate)
        overall_index[end] = overall_index[start] * ((1 + overall_rate) ** years_in_period)

    # Interpolate intermediate years
    all_years = [1990, 2000, 2010, 2020, 2024]

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(all_years, [necessity_index[y] for y in all_years],
            'o-', color='#e74c3c', linewidth=2.5, markersize=10,
            label=f'Necessities (~{necessity_weight*100:.0f}% of spending)')
    ax.plot(all_years, [discretionary_index[y] for y in all_years],
            's-', color='#3498db', linewidth=2.5, markersize=10,
            label=f'Discretionary (~{discretionary_weight*100:.0f}% of spending)')
    ax.plot(all_years, [overall_index[y] for y in all_years],
            '^--', color='#2c3e50', linewidth=2, markersize=8,
            label='Weighted Overall')

    # Shade the gap
    ax.fill_between(all_years,
                    [necessity_index[y] for y in all_years],
                    [discretionary_index[y] for y in all_years],
                    alpha=0.2, color='#e74c3c')

    # Add final values
    ax.annotate(f'{necessity_index[2024]:.0f}',
                xy=(2024, necessity_index[2024]), xytext=(2024.5, necessity_index[2024]),
                fontsize=11, fontweight='bold', color='#e74c3c')
    ax.annotate(f'{discretionary_index[2024]:.0f}',
                xy=(2024, discretionary_index[2024]), xytext=(2024.5, discretionary_index[2024]),
                fontsize=11, fontweight='bold', color='#3498db')

    # Calculate gap
    gap = necessity_index[2024] - discretionary_index[2024]
    ax.annotate(f'Gap: {gap:.0f} pts\n({(gap/discretionary_index[2024])*100:.0f}% higher)',
                xy=(2022, (necessity_index[2024] + discretionary_index[2024])/2),
                fontsize=11, ha='center', fontweight='bold', color='#c0392b')

    ax.set_xlabel('Year')
    ax.set_ylabel('Price Index (1990 = 100)')
    ax.set_title('Necessity vs. Discretionary Inflation (1990-2024)\n'
                 'Essential Spending Has Inflated Faster Than Optional Spending',
                 fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_xlim(1988, 2027)

    plt.tight_layout()
    plt.savefig('figures/fig_necessity_discretionary.png', dpi=150, bbox_inches='tight')
    plt.close()

    return necessity_index, discretionary_index

# =============================================================================
# METRIC 3: Asset-Adjusted Inflation Index
# CPI augmented with financial and housing asset prices
# =============================================================================

def calculate_asset_adjusted():
    """
    Construct inflation index that includes asset prices alongside consumption.

    Weights:
    - 70% CPI (consumption)
    - 20% Housing (Case-Shiller)
    - 10% Financial assets (S&P 500)
    """

    cpi_weight = 0.70
    housing_weight = 0.20
    equity_weight = 0.10

    # Normalize all to 2000 = 100
    cpi_norm = {y: (cpi_u[y] / cpi_u[2000]) * 100 for y in years}
    housing_norm = {y: case_shiller[y] for y in years}  # Already 2000 = 100
    equity_norm = {y: (sp500[y] / sp500[2000]) * 100 for y in years}

    # Asset-adjusted index
    asset_adjusted = {}
    for y in years:
        asset_adjusted[y] = (cpi_weight * cpi_norm[y] +
                            housing_weight * housing_norm[y] +
                            equity_weight * equity_norm[y])

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(years, [cpi_norm[y] for y in years],
            'o-', color='#2c3e50', linewidth=2.5, markersize=10,
            label='Official CPI (Consumption Only)')
    ax.plot(years, [asset_adjusted[y] for y in years],
            's-', color='#e74c3c', linewidth=2.5, markersize=10,
            label='Asset-Adjusted Index (70% CPI, 20% Housing, 10% Equities)')
    ax.plot(years, [housing_norm[y] for y in years],
            '^--', color='#27ae60', linewidth=1.5, markersize=6, alpha=0.7,
            label='Housing Only (Case-Shiller)')
    ax.plot(years, [equity_norm[y] for y in years],
            'd--', color='#9b59b6', linewidth=1.5, markersize=6, alpha=0.7,
            label='Equities Only (S&P 500)')

    # Add labels for 2024 values
    ax.annotate(f'CPI: {cpi_norm[2024]:.0f}',
                xy=(2024, cpi_norm[2024]), xytext=(2024.3, cpi_norm[2024]-10),
                fontsize=10, color='#2c3e50')
    ax.annotate(f'Asset-Adj: {asset_adjusted[2024]:.0f}',
                xy=(2024, asset_adjusted[2024]), xytext=(2024.3, asset_adjusted[2024]+5),
                fontsize=10, fontweight='bold', color='#e74c3c')

    # Calculate divergence
    divergence = asset_adjusted[2024] - cpi_norm[2024]
    pct_divergence = (divergence / cpi_norm[2024]) * 100

    ax.text(0.05, 0.95,
            f'Asset-adjusted index is {pct_divergence:.0f}% higher than CPI in 2024\n'
            f'Gap has widened significantly since 2010',
            transform=ax.transAxes, fontsize=11, va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.set_xlabel('Year')
    ax.set_ylabel('Index (2000 = 100)')
    ax.set_title('Asset-Adjusted Inflation vs. Official CPI (2000-2024)\n'
                 'Including Asset Prices Reveals Higher "Total Cost of Life" Inflation',
                 fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_ylim(0, 500)

    plt.tight_layout()
    plt.savefig('figures/fig_asset_adjusted.png', dpi=150, bbox_inches='tight')
    plt.close()

    return cpi_norm, asset_adjusted

# =============================================================================
# METRIC 4: First-Time Buyer Affordability Index
# Hours of median-wage work for 20% down payment on median home
# =============================================================================

def calculate_housing_affordability():
    """
    Calculate hours of work needed for 20% down payment on median home.
    """

    down_payment_pct = 0.20

    hours_for_down = {}
    weeks_for_down = {}

    for year in years:
        down_payment = home_price[year] * down_payment_pct
        hourly_wage = median_hourly_wage[year]
        hours = down_payment / hourly_wage
        hours_for_down[year] = hours
        weeks_for_down[year] = hours / 40  # Full-time weeks

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left panel: Hours of work
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(years)))
    bars = ax1.bar([str(y) for y in years], [hours_for_down[y] for y in years],
                   color=colors, edgecolor='black', linewidth=0.5)

    for bar, year in zip(bars, years):
        val = hours_for_down[year]
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'{val:.0f}', ha='center', va='bottom', fontsize=9)

    ax1.set_ylabel('Hours of Median-Wage Work')
    ax1.set_xlabel('Year')
    ax1.set_title('Hours of Work for 20% Down Payment\non Median Home', fontweight='bold')

    # Calculate % change
    pct_change = ((hours_for_down[2024] - hours_for_down[1990]) / hours_for_down[1990]) * 100
    ax1.text(0.95, 0.95, f'{pct_change:+.0f}% since 1990',
             transform=ax1.transAxes, ha='right', va='top',
             fontsize=12, fontweight='bold', color='#c0392b')

    # Right panel: As fraction of annual work hours
    annual_hours = 2080  # 40 hrs/week * 52 weeks
    years_of_work = {y: hours_for_down[y] / annual_hours for y in years}

    ax2.plot(years, [years_of_work[y] for y in years], 'o-',
             color='#e74c3c', linewidth=2.5, markersize=10)
    ax2.fill_between(years, [years_of_work[y] for y in years], alpha=0.3, color='#e74c3c')

    for year in years:
        ax2.annotate(f'{years_of_work[year]:.1f}',
                     xy=(year, years_of_work[year]),
                     xytext=(0, 10), textcoords='offset points',
                     ha='center', fontsize=9)

    ax2.set_ylabel('Years of Full-Time Work')
    ax2.set_xlabel('Year')
    ax2.set_title('Down Payment as Years of Work\n(at median wage, full-time)', fontweight='bold')
    ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='1 year of work')
    ax2.legend()

    plt.suptitle('First-Time Buyer Affordability: How Much Work for a Down Payment?',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('figures/fig_housing_affordability.png', dpi=150, bbox_inches='tight')
    plt.close()

    return hours_for_down, years_of_work

# =============================================================================
# METRIC 5: Grocery Basket Time-Cost Over Time
# Composite index for a basic grocery basket
# =============================================================================

def calculate_grocery_basket():
    """
    Calculate time-cost for a basic weekly grocery basket.

    Basket contents (approximate weekly needs for family of 4):
    - 2 gallons of milk
    - 2 dozen eggs
    - 3 lbs ground beef
    - (Note: simplified basket for demonstration)
    """

    basket_cost = {}
    basket_time = {}  # Minutes of work

    for year in years:
        cost = (2 * milk_price[year] +
                2 * egg_price[year] +
                3 * beef_price[year])
        basket_cost[year] = cost
        basket_time[year] = (cost / median_hourly_wage[year]) * 60

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot both dollar cost and time cost on dual axis
    ax2 = ax.twinx()

    line1 = ax.plot(years, [basket_cost[y] for y in years], 'o-',
                    color='#2c3e50', linewidth=2.5, markersize=10,
                    label='Dollar Cost')
    ax.set_ylabel('Cost in Dollars', color='#2c3e50')
    ax.tick_params(axis='y', labelcolor='#2c3e50')

    line2 = ax2.plot(years, [basket_time[y] for y in years], 's-',
                     color='#e74c3c', linewidth=2.5, markersize=10,
                     label='Minutes of Work')
    ax2.set_ylabel('Minutes of Median-Wage Work', color='#e74c3c')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')

    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='upper left')

    ax.set_xlabel('Year')
    ax.set_title('Basic Grocery Basket: Dollar Cost vs. Time Cost\n'
                 '(2 gal milk, 2 doz eggs, 3 lb ground beef)',
                 fontweight='bold')

    # Add annotations
    dollar_change = ((basket_cost[2024] - basket_cost[1990]) / basket_cost[1990]) * 100
    time_change = ((basket_time[2024] - basket_time[1990]) / basket_time[1990]) * 100

    ax.text(0.95, 0.05,
            f'Dollar cost: {dollar_change:+.0f}% since 1990\n'
            f'Time cost: {time_change:+.0f}% since 1990',
            transform=ax.transAxes, ha='right', va='bottom',
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig('figures/fig_grocery_basket.png', dpi=150, bbox_inches='tight')
    plt.close()

    return basket_cost, basket_time

# =============================================================================
# SUMMARY TABLE
# =============================================================================

def create_summary_table():
    """Create summary table of all metrics."""

    print("\n" + "="*80)
    print("NOVEL METRICS ANALYSIS: SUMMARY RESULTS")
    print("="*80)

    # Time-cost for individual goods
    print("\n1. TIME-COST INDEX (Minutes of work to purchase)")
    print("-" * 60)
    print(f"{'Good':<25} {'1990':<10} {'2024':<10} {'Change':<10}")
    print("-" * 60)

    for name, prices in [('Gallon of Milk', milk_price),
                          ('Dozen Eggs', egg_price),
                          ('Pound of Ground Beef', beef_price),
                          ('Gallon of Gasoline', gas_price)]:
        t1990 = (prices[1990] / median_hourly_wage[1990]) * 60
        t2024 = (prices[2024] / median_hourly_wage[2024]) * 60
        change = ((t2024 - t1990) / t1990) * 100
        print(f"{name:<25} {t1990:<10.1f} {t2024:<10.1f} {change:+.1f}%")

    # Housing affordability
    print("\n2. HOUSING AFFORDABILITY (Hours for 20% down payment)")
    print("-" * 60)
    h1990 = (home_price[1990] * 0.20) / median_hourly_wage[1990]
    h2024 = (home_price[2024] * 0.20) / median_hourly_wage[2024]
    print(f"1990: {h1990:,.0f} hours ({h1990/2080:.1f} years of full-time work)")
    print(f"2024: {h2024:,.0f} hours ({h2024/2080:.1f} years of full-time work)")
    print(f"Change: {((h2024-h1990)/h1990)*100:+.0f}%")

    # Asset-adjusted vs CPI
    print("\n3. ASSET-ADJUSTED INFLATION vs CPI (2000 = 100)")
    print("-" * 60)
    cpi_2024 = (cpi_u[2024] / cpi_u[2000]) * 100
    asset_adj_2024 = (0.70 * cpi_2024 +
                      0.20 * case_shiller[2024] +
                      0.10 * (sp500[2024]/sp500[2000])*100)
    print(f"Official CPI (2024): {cpi_2024:.0f}")
    print(f"Asset-Adjusted (2024): {asset_adj_2024:.0f}")
    print(f"Divergence: {((asset_adj_2024-cpi_2024)/cpi_2024)*100:+.0f}%")

    print("\n" + "="*80)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    print("Generating novel metrics analysis...")

    # Generate all figures
    time_cost_results = calculate_time_cost()
    print("  Created: figures/fig_time_cost_index.png")

    necessity_idx, discretionary_idx = calculate_necessity_discretionary()
    print("  Created: figures/fig_necessity_discretionary.png")

    cpi_norm, asset_adj = calculate_asset_adjusted()
    print("  Created: figures/fig_asset_adjusted.png")

    hours_down, years_work = calculate_housing_affordability()
    print("  Created: figures/fig_housing_affordability.png")

    basket_cost, basket_time = calculate_grocery_basket()
    print("  Created: figures/fig_grocery_basket.png")

    # Print summary
    create_summary_table()

    print("\nAnalysis complete. 5 figures generated.")
