#!/usr/bin/env python3
"""
Generate figures for inflation analysis report.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Create figures directory
os.makedirs('figures', exist_ok=True)

# =============================================================================
# Figure 1: CPI Methodology Changes Timeline
# =============================================================================
def create_methodology_timeline():
    fig, ax = plt.subplots(figsize=(12, 6))

    changes = [
        (1983, "OER replaces\ndirect housing costs", -0.0),
        (1995, "Boskin Commission\nfinds +1.1pp bias", 0),
        (1999, "Geometric mean\nformula (-0.28pp)", -0.28),
        (2002, "Chained CPI\nintroduced (-0.25pp)", -0.25),
        (2018, "Smartphone\nhedonic adjustment", -0.05),
        (2023, "OER structure-type\nweighting refined", 0),
    ]

    years = [c[0] for c in changes]
    effects = [c[2] for c in changes]
    labels = [c[1] for c in changes]

    colors = ['#e74c3c' if e < 0 else '#3498db' for e in effects]

    ax.barh(range(len(changes)), effects, color=colors, height=0.6, alpha=0.8)

    for i, (year, label, effect) in enumerate(changes):
        ax.text(-0.35, i, f"{year}", ha='right', va='center', fontweight='bold', fontsize=11)
        ax.text(0.02 if effect >= 0 else effect - 0.02, i, label,
                ha='left' if effect >= 0 else 'right', va='center', fontsize=9)

    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlim(-0.5, 0.15)
    ax.set_yticks([])
    ax.set_xlabel('Estimated Annual Effect on Measured Inflation (percentage points)')
    ax.set_title('CPI Methodology Changes: Direction and Magnitude\n(Negative = Lower Measured Inflation)', fontweight='bold')

    # Add note
    ax.text(0.5, -0.12,
            'Note: Cumulative effect of methodology changes since 1980 estimated at 5.1% lower prices over 31 years (BLS CPI-U-RS)',
            transform=ax.transAxes, ha='center', fontsize=9, style='italic')

    plt.tight_layout()
    plt.savefig('figures/fig1_methodology_changes.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: figures/fig1_methodology_changes.png")

# =============================================================================
# Figure 2: Inflation by Income Quintile
# =============================================================================
def create_income_quintile_chart():
    fig, ax = plt.subplots(figsize=(10, 6))

    quintiles = ['Lowest\n20%', 'Second\n20%', 'Middle\n20%', 'Fourth\n20%', 'Highest\n20%']
    cumulative_inflation = [64, 62, 60, 58, 57]  # 2005-2023 approximate

    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, 5))

    bars = ax.bar(quintiles, cumulative_inflation, color=colors, edgecolor='black', linewidth=0.5)

    # Add value labels
    for bar, val in zip(bars, cumulative_inflation):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val}%', ha='center', va='bottom', fontweight='bold')

    # Add average line
    avg = 60
    ax.axhline(y=avg, color='#2c3e50', linestyle='--', linewidth=2, label=f'Average: {avg}%')

    ax.set_ylabel('Cumulative Price Increase (%)')
    ax.set_xlabel('Income Quintile')
    ax.set_title('Cumulative Inflation by Income Quintile (2005-2023)\nLower-Income Households Experience Higher Inflation', fontweight='bold')
    ax.set_ylim(50, 70)
    ax.legend(loc='upper right')

    # Add gap annotation
    ax.annotate('', xy=(0, 64), xytext=(4, 57),
                arrowprops=dict(arrowstyle='<->', color='#e74c3c', lw=2))
    ax.text(2, 67, '7 pp gap\n(~12% faster)', ha='center', fontsize=10, color='#e74c3c', fontweight='bold')

    plt.tight_layout()
    plt.savefig('figures/fig2_income_quintile_inflation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: figures/fig2_income_quintile_inflation.png")

# =============================================================================
# Figure 3: Truflation vs Official CPI
# =============================================================================
def create_truflation_comparison():
    fig, ax = plt.subplots(figsize=(12, 6))

    # Approximate data based on research
    months = ['Jan\n2021', 'Jul\n2021', 'Jan\n2022', 'Jul\n2022', 'Jan\n2023',
              'Jul\n2023', 'Jan\n2024', 'Jul\n2024', 'Jan\n2025', 'Nov\n2025']

    cpi = [1.4, 5.4, 7.5, 9.0, 6.4, 3.2, 3.1, 2.9, 3.0, 2.7]
    truflation = [1.8, 6.5, 8.5, 11.5, 5.5, 2.5, 2.2, 1.8, 1.5, 1.4]

    x = np.arange(len(months))

    ax.plot(x, cpi, 'o-', color='#2c3e50', linewidth=2.5, markersize=8, label='Official CPI')
    ax.plot(x, truflation, 's--', color='#e74c3c', linewidth=2.5, markersize=8, label='Truflation')

    # Shade divergence areas
    ax.fill_between(x, cpi, truflation, where=[t > c for t, c in zip(truflation, cpi)],
                    alpha=0.3, color='#e74c3c', label='Truflation > CPI')
    ax.fill_between(x, cpi, truflation, where=[t < c for t, c in zip(truflation, cpi)],
                    alpha=0.3, color='#3498db', label='CPI > Truflation')

    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.set_ylabel('Year-over-Year Inflation Rate (%)')
    ax.set_xlabel('Month')
    ax.set_title('Official CPI vs. Truflation: Timing and Magnitude Divergence\n(Truflation updates daily; CPI updates monthly)', fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 13)

    # Annotate peak divergence
    ax.annotate('Peak divergence:\n+2.5 pp', xy=(3, 11.5), xytext=(4.5, 12),
                arrowprops=dict(arrowstyle='->', color='#e74c3c'),
                fontsize=10, color='#e74c3c')

    # Annotate current divergence
    ax.annotate('Current divergence:\n-1.3 pp', xy=(9, 1.4), xytext=(7.5, 0.5),
                arrowprops=dict(arrowstyle='->', color='#3498db'),
                fontsize=10, color='#3498db')

    plt.tight_layout()
    plt.savefig('figures/fig3_truflation_vs_cpi.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: figures/fig3_truflation_vs_cpi.png")

# =============================================================================
# Figure 4: Inflation by Race/Ethnicity
# =============================================================================
def create_race_inflation_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left panel: Peak inflation disparity (2021-2022)
    groups = ['White', 'Black', 'Hispanic', 'AAPI']
    peak_gap = [0, 1.0, 1.5, -0.3]  # Gap vs national average at peak
    colors = ['#3498db', '#e74c3c', '#e67e22', '#9b59b6']

    bars = ax1.bar(groups, peak_gap, color=colors, edgecolor='black', linewidth=0.5)
    ax1.axhline(y=0, color='black', linewidth=1)
    ax1.set_ylabel('Deviation from National Average (pp)')
    ax1.set_title('Peak Inflation Gap by Race/Ethnicity\n(2021-2022)', fontweight='bold')
    ax1.set_ylim(-1, 2)

    for bar, val in zip(bars, peak_gap):
        offset = 0.1 if val >= 0 else -0.2
        ax1.text(bar.get_x() + bar.get_width()/2, val + offset,
                f'{val:+.1f} pp', ha='center', va='bottom' if val >= 0 else 'top', fontweight='bold')

    # Right panel: Financial stress during high inflation
    stress_groups = ['White\nAmericans', 'Black\nAmericans']
    stress_pct = [38, 55]
    stress_colors = ['#3498db', '#e74c3c']

    bars2 = ax2.bar(stress_groups, stress_pct, color=stress_colors, edgecolor='black', linewidth=0.5)
    ax2.set_ylabel('Percent Reporting Serious Financial Problems')
    ax2.set_title('Financial Stress During High Inflation\n(Harvard Poll)', fontweight='bold')
    ax2.set_ylim(0, 70)

    for bar, val in zip(bars2, stress_pct):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 1,
                f'{val}%', ha='center', va='bottom', fontweight='bold', fontsize=14)

    # Add gap annotation
    ax2.annotate('', xy=(0, 38), xytext=(1, 55),
                arrowprops=dict(arrowstyle='<->', color='#2c3e50', lw=2))
    ax2.text(0.5, 47, '+17 pp', ha='center', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig('figures/fig4_race_inflation_disparity.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: figures/fig4_race_inflation_disparity.png")

# =============================================================================
# Figure 5: Regional CPI Variation
# =============================================================================
def create_regional_variation():
    fig, ax = plt.subplots(figsize=(10, 6))

    regions = ['National\nAverage', 'Midwest', 'Northeast', 'NY-Newark-\nJersey City']
    rates = [2.7, 3.0, 3.1, 3.0]

    colors = ['#2c3e50'] + ['#e74c3c' if r > 2.7 else '#27ae60' for r in rates[1:]]

    bars = ax.bar(regions, rates, color=colors, edgecolor='black', linewidth=0.5)

    ax.axhline(y=2.7, color='#2c3e50', linestyle='--', linewidth=2, alpha=0.5)

    for bar, val in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.05,
                f'{val}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

    ax.set_ylabel('12-Month CPI Inflation Rate (%)')
    ax.set_title('Regional Inflation Variation (November 2025)\nGeographic Disparities in Price Increases', fontweight='bold')
    ax.set_ylim(0, 4)

    plt.tight_layout()
    plt.savefig('figures/fig5_regional_variation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: figures/fig5_regional_variation.png")

# =============================================================================
# Figure 6: Spending Composition by Income
# =============================================================================
def create_spending_composition():
    fig, ax = plt.subplots(figsize=(12, 7))

    categories = ['Housing', 'Transportation', 'Food', 'Healthcare', 'Other']

    # Approximate spending shares by quintile
    lowest_20 = [40, 15, 16, 8, 21]
    middle_20 = [33, 17, 13, 8, 29]
    highest_20 = [30, 16, 11, 7, 36]

    x = np.arange(len(categories))
    width = 0.25

    bars1 = ax.bar(x - width, lowest_20, width, label='Lowest 20%', color='#e74c3c', edgecolor='black')
    bars2 = ax.bar(x, middle_20, width, label='Middle 20%', color='#f39c12', edgecolor='black')
    bars3 = ax.bar(x + width, highest_20, width, label='Highest 20%', color='#27ae60', edgecolor='black')

    ax.set_ylabel('Share of Total Expenditure (%)')
    ax.set_xlabel('Spending Category')
    ax.set_title('Spending Composition by Income Quintile\nLower-Income Households Allocate More to Necessities', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 50)

    # Add annotation
    ax.annotate('Higher necessity\nspending share', xy=(0, 40), xytext=(1, 45),
                arrowprops=dict(arrowstyle='->', color='#e74c3c'),
                fontsize=10, color='#e74c3c', fontweight='bold')

    plt.tight_layout()
    plt.savefig('figures/fig6_spending_composition.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: figures/fig6_spending_composition.png")

# =============================================================================
# Figure 7: Argentina Case Study
# =============================================================================
def create_argentina_case():
    fig, ax = plt.subplots(figsize=(10, 6))

    years = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']
    official = [8, 15, 22, 30, 40, 50, 60, 70, 80]  # Approximate cumulative
    bpp = [8, 20, 35, 50, 70, 95, 115, 130, 137]  # Approximate cumulative from BPP

    ax.plot(years, official, 'o-', color='#2c3e50', linewidth=2.5, markersize=8, label='Official INDEC')
    ax.plot(years, bpp, 's-', color='#e74c3c', linewidth=2.5, markersize=8, label='Billion Prices Project')

    ax.fill_between(years, official, bpp, alpha=0.3, color='#e74c3c')

    ax.set_ylabel('Cumulative Inflation (%)')
    ax.set_xlabel('Year')
    ax.set_title('Argentina: Official vs. Independent Inflation Measurement (2007-2015)\nThe Billion Prices Project Exposed Systematic Manipulation', fontweight='bold')
    ax.legend(loc='upper left')

    # Add annotations
    ax.annotate('2012: The Economist\nstops publishing\nINDEC figures',
                xy=(5, 50), xytext=(6.5, 30),
                arrowprops=dict(arrowstyle='->', color='#2c3e50'),
                fontsize=9, ha='center')

    ax.annotate('2013: IMF\ncensures Argentina',
                xy=(6, 60), xytext=(7.5, 45),
                arrowprops=dict(arrowstyle='->', color='#2c3e50'),
                fontsize=9, ha='center')

    ax.annotate('Gap: 57 pp\n(2.3x official)',
                xy=(8, 110), xytext=(7, 120),
                fontsize=11, fontweight='bold', color='#e74c3c')

    plt.tight_layout()
    plt.savefig('figures/fig7_argentina_case.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: figures/fig7_argentina_case.png")

# =============================================================================
# Figure 8: Novel Metrics Framework
# =============================================================================
def create_novel_metrics_diagram():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, 'Novel Inflation Metrics: Data Sources and Construction',
            ha='center', fontsize=16, fontweight='bold')

    # Central node
    center = plt.Circle((7, 5), 1.2, color='#3498db', alpha=0.8)
    ax.add_patch(center)
    ax.text(7, 5, 'Novel\nInflation\nMetrics', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')

    # Metric nodes
    metrics = [
        (2, 8, 'Time-Cost\nIndex', '#e74c3c'),
        (5, 8.5, 'Life Stage\nBaskets', '#e67e22'),
        (9, 8.5, 'Shrinkflation\nIndex', '#f1c40f'),
        (12, 8, 'First-Time\nBuyer Index', '#27ae60'),
        (2, 2, 'Necessity vs.\nDiscretionary', '#9b59b6'),
        (5, 1.5, 'Asset-Adjusted\nCPI', '#1abc9c'),
        (9, 1.5, 'Inflation\nTransition', '#e91e63'),
        (12, 2, 'Demographic\nBreakdowns', '#00bcd4'),
    ]

    data_sources = [
        (0.5, 5, 'BLS\nWage Data'),
        (3.5, 5, 'Consumer\nExpenditure\nSurvey'),
        (10.5, 5, 'Truflation\nReal-time'),
        (13.5, 5, 'Zillow/\nCase-Shiller'),
    ]

    for x, y, label, color in metrics:
        circle = plt.Circle((x, y), 0.8, color=color, alpha=0.7)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold', color='white')
        # Draw line to center
        ax.plot([x, 7], [y, 5], 'k-', alpha=0.3, linewidth=1)

    for x, y, label in data_sources:
        rect = mpatches.FancyBboxPatch((x-0.7, y-0.5), 1.4, 1,
                                        boxstyle="round,pad=0.05",
                                        facecolor='#ecf0f1', edgecolor='#2c3e50')
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=8)

    ax.text(7, 0.3, 'All data sources are publicly available or purchasable',
            ha='center', fontsize=10, style='italic')

    plt.savefig('figures/fig8_novel_metrics_framework.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Created: figures/fig8_novel_metrics_framework.png")

# =============================================================================
# Run all figure generation
# =============================================================================
if __name__ == '__main__':
    print("Generating figures...")
    create_methodology_timeline()
    create_income_quintile_chart()
    create_truflation_comparison()
    create_race_inflation_chart()
    create_regional_variation()
    create_spending_composition()
    create_argentina_case()
    create_novel_metrics_diagram()
    print("\nAll figures generated successfully!")
