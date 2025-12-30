#!/usr/bin/env python3
"""
Convert in-text citations to proper LaTeX \cite{} commands.
"""

import re
from pathlib import Path

tex = Path('inflation_final_humanized.tex').read_text()

# Citation mapping: patterns to bibkeys
# Format: (pattern, replacement)
# Using \citet for "Author (year)" style and \citep for "(Author, year)" style

# We'll use natbib package which provides \citet and \citep

citations = [
    # Specific multi-author citations
    (r'Boskin et al\., 1996', r'\\citet{boskin1996toward}'),
    (r'Boskin et al\.~\(1996\)', r'\\citet{boskin1996toward}'),
    (r'\(Boskin et al\., 1996\)', r'\\citep{boskin1996toward}'),
    (r'Boskin Commission Report \(Boskin et al\., 1996\)', r'Boskin Commission Report \\citep{boskin1996toward}'),

    (r'Cavallo and Rigobon \(2010\)', r'\\citet{cavallo2016billion}'),
    (r'Cavallo \& Rigobon, 2016', r'\\citet{cavallo2016billion}'),
    (r'\(Cavallo \& Rigobon, 2016\)', r'\\citep{cavallo2016billion}'),
    (r'Cavallo \\& Rigobon \(2016\)', r'\\citet{cavallo2016billion}'),

    (r'Ambrose, Coulson, and Yoshida \(2015\)', r'\\citet{ambrose2015repeat}'),

    (r'Darity and Hamilton \(2012\)', r'\\citet{darity2012bold}'),
    (r'Oliver and Shapiro \(2006\)', r'\\citet{oliver2006black}'),
    (r'Oliver \\& Shapiro, 2006', r'\\citet{oliver2006black}'),

    (r'Saez and Zucman \(2016\)', r'\\citet{saez2016wealth}'),
    (r'Saez \\& Zucman \(2016\)', r'\\citet{saez2016wealth}'),

    (r'Gilens and Page \(2014\)', r'\\citet{gilens2014testing}'),
    (r'Gilens \\& Page, 2014', r'\\citet{gilens2014testing}'),

    (r'Aguiar and Hurst \(2007\)', r'\\citet{aguiar2007measuring}'),

    (r'Athey and Imbens \(2019\)', r'\\citet{athey2019machine}'),
    (r'Athey \\& Imbens, 2019', r'\\citet{athey2019machine}'),

    (r'Argente and Lee \(2021\)', r'\\citet{argente2021cost}'),

    (r'Moulton and Moses \(1997\)', r'\\citet{moulton1997addressing}'),

    (r'Chetty et al\. \(2014\)', r'\\citet{chetty2014land}'),

    (r'Derenoncourt et al\. \(2022\)', r'\\citet{derenoncourt2022wealth}'),

    (r'Darity and Myers \(1998\)', r'\\citet{darity1998persistent}'),
    (r'Darity \\& Myers, 1998', r'\\citet{darity1998persistent}'),

    (r'Armantier et al\. \(2022\)', r'\\citet{armantier2022inflation}'),
    (r'Armantier et al\.~\(2022\)', r'\\citet{armantier2022inflation}'),

    (r'Heise et al\. \(2024\)', r'\\citet{heise2024lower}'),
    (r'Heise, Karahan, and Sahin \(2024\)', r'\\citet{heise2024lower}'),
    (r'Heise, Karahan, \\& Sahin \(2024\)', r'\\citet{heise2024lower}'),

    (r'Kudlyak and Wolpin \(2022\)', r'\\citet{kudlyak2022black}'),
    (r'Kudlyak \\& Wolpin \(2022\)', r'\\citet{kudlyak2022black}'),

    (r'Mullainathan and Spiess \(2017\)', r'\\citet{mullainathan2017machine}'),

    (r'Chen et al\. \(2021\)', r'\\citet{chen2021evaluating}'),

    (r'Taylor et al\. \(2022\)', r'\\citet{taylor2022galactica}'),

    (r'Marshall and Wallace \(2019\)', r'\\citet{marshall2019systematic}'),

    # Single author citations - be careful with word boundaries
    (r'Cavallo \(2013\)', r'\\citet{cavallo2013online}'),
    (r'\(Cavallo, 2013\)', r'\\citep{cavallo2013online}'),

    (r'Stiglitz \(1975\)', r'\\citet{stiglitz1975screening}'),
    (r'Stiglitz \(2017\)', r'\\citet{stiglitz2017revolution}'),

    (r'Foucault \(1975, 1980\)', r'\\citet{foucault1975discipline,foucault1980power}'),
    (r'Foucault \(1975\)', r'\\citet{foucault1975discipline}'),
    (r'Foucault \(1980\)', r'\\citet{foucault1980power}'),

    (r'Scott \(1998\)', r'\\citet{scott1998seeing}'),

    (r'Spence \(1973\)', r'\\citet{spence1973job}'),

    (r'Akerlof \(1970\)', r'\\citet{akerlof1970lemons}'),

    (r'Bourdieu \(1975\)', r'\\citet{bourdieu1975specificity}'),
    (r'Bourdieu \(2004\)', r'\\citet{bourdieu2004science}'),

    (r'Becker \(1965\)', r'\\citet{becker1965time}'),

    (r'Hobijn and Lagakos \(2005\)', r'\\citet{hobijn2005inflation}'),
    (r'Hobijn \\& Lagakos, 2005', r'\\citet{hobijn2005inflation}'),

    (r'Jaravel \(2019\)', r'\\citet{jaravel2019unequal}'),

    (r'Gordon \(2006\)', r'\\citet{gordon2006boskin}'),

    (r'Hausman \(2003\)', r'\\citet{hausman2003sources}'),

    (r'Moulton \(1996\)', r'\\citet{moulton1996bias}'),

    (r'Pakes \(2003\)', r'\\citet{pakes2003reconsideration}'),

    (r'Diewert \(2003\)', r'\\citet{diewert2003hedonic}'),

    (r'Piketty \(2014\)', r'\\citet{piketty2014capital}'),

    (r'Stigler \(1971\)', r'\\citet{stigler1971theory}'),

    (r'Benkler \(2006\)', r'\\citet{benkler2006wealth}'),

    (r'Shirky \(2008\)', r'\\citet{shirky2008here}'),

    (r'Hamilton \(2008\)', r'\\citet{hamilton2008measuring}'),

    (r'Dolan \(2014\)', r'\\citet{dolan2014shadowstats}'),

    (r'Alm[aå]s \(2012\)', r'\\citet{almas2012international}'),

    # BLS citations
    (r'BLS, 2024a', r'\\citet{bls2024concepts}'),
    (r'BLS, 2024b', r'\\citet{bls2024quality}'),
    (r'BLS, 2024c', r'\\citet{bls2024rent}'),
    (r'BLS, 2024d', r'\\citet{bls2024income}'),
    (r'BLS, 2024', r'\\citet{bls2024concepts}'),
    (r'BLS, 2025', r'\\citet{bls2025summary}'),
    (r'BLS, 1999', r'\\citet{bls1999geometric}'),
    (r'BLS, 2002', r'\\citet{bls2002chained}'),
    (r'\(BLS, ', r'\\citep{bls'),

    # FOMC
    (r'FOMC, 2012', r'\\citet{fomc2012statement}'),
    (r'\(FOMC, 2012\)', r'\\citep{fomc2012statement}'),

    # Truflation
    (r'Truflation, 2024', r'\\citet{truflation2024methodology}'),
    (r'\(Truflation, 2024\)', r'\\citep{truflation2024methodology}'),
    (r'Truflation \(2024\)', r'\\citet{truflation2024methodology}'),
]

# Apply replacements
for pattern, replacement in citations:
    tex = re.sub(pattern, replacement, tex)

print("Applied citation replacements")

# Add natbib package to preamble if not present
if '\\usepackage{natbib}' not in tex:
    # Add after hyperref setup
    tex = tex.replace(
        '\\usepackage{booktabs}\\usepackage{float}',
        '\\usepackage{booktabs}\\usepackage{float}\\usepackage{natbib}'
    )
    print("Added natbib package")

# Remove old references section and add bibliography
# Find the references section
ref_start = tex.find('\\subsection{References}\\label{sec:references}')
if ref_start != -1:
    # Find where the next section/appendix starts
    appendix_start = tex.find('\\subsection{Appendix A:', ref_start)
    if appendix_start == -1:
        appendix_start = tex.find('\\section{Appendix', ref_start)

    if appendix_start != -1:
        # Replace references section with bibliography
        old_refs = tex[ref_start:appendix_start]
        new_refs = '''\\section{References}\\label{sec:references}

\\bibliographystyle{apalike}
\\bibliography{references}

'''
        tex = tex[:ref_start] + new_refs + tex[appendix_start:]
        print("Replaced references section with bibliography")

# Write output
Path('inflation_final_humanized.tex').write_text(tex)
print("\nCitation conversion complete!")
print("Run: pdflatex, bibtex, pdflatex, pdflatex to compile")
