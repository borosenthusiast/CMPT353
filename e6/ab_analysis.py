import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import json
import os
import scipy.stats as stats


OUTPUT_TEMPLATE = (
    '"Did more/less users use the search feature?" p-value: {more_users_p:.3g}\n'
    '"Did users search more/less?" p-value: {more_searches_p:.3g}\n'
    '"Did more/less instructors use the search feature?" p-value: {more_instr_p:.3g}\n'
    '"Did instructors search more/less?" p-value: {more_instr_searches_p:.3g}'
)


def main():
    #searchdata_file = sys.argv[1]
    searchdata_file = 'searches.json'
    searchdata = pd.read_json('searches.json', orient='records', lines=True)
    searchdata['A/B'] = searchdata['uid'].apply(lambda x: (x % 2 and 'odd' or 'even'))
    searchdata['searched'] = searchdata['search_count'].apply(lambda x: (x > 0 and 'searched' or 'not searched'))
    ct = pd.crosstab(searchdata['A/B'], searchdata['searched'])
    chi2, p, dof, ex = stats.chi2_contingency(ct)
    #print(ct)
    oddsearchcount = searchdata[searchdata['A/B'] == 'odd']
    evensearchcount = searchdata[searchdata['A/B'] == 'even']
    mwu1 = stats.mannwhitneyu(oddsearchcount['search_count'], evensearchcount['search_count'], alternative='two-sided')
    
    insdata = searchdata[searchdata['is_instructor'] == True]
    ct2 = pd.crosstab(insdata['A/B'], insdata['searched'])
    chi22, p2, dof2, ex2 = stats.chi2_contingency(ct2)

    insodd = insdata[insdata['A/B'] == 'odd']
    inseven = insdata[insdata['A/B'] == 'even']
    mwu2 = stats.mannwhitneyu(insodd['search_count'], inseven['search_count'], alternative='two-sided')
    #print(insdata)
    #print(searchdata)
    
    # ...


    # Output
    print(OUTPUT_TEMPLATE.format(
        more_users_p=p,
        more_searches_p=mwu1.pvalue,
        more_instr_p=p2,
        more_instr_searches_p=mwu2.pvalue,
    ))


if __name__ == '__main__':
    main()