import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import scipy.stats as stats

OUTPUT_TEMPLATE = (
    "Initial (invalid) T-test p-value: {initial_ttest_p:.3g}\n"
    "Original data normality p-values: {initial_weekday_normality_p:.3g} {initial_weekend_normality_p:.3g}\n"
    "Original data equal-variance p-value: {initial_levene_p:.3g}\n"
    "Transformed data normality p-values: {transformed_weekday_normality_p:.3g} {transformed_weekend_normality_p:.3g}\n"
    "Transformed data equal-variance p-value: {transformed_levene_p:.3g}\n"
    "Weekly data normality p-values: {weekly_weekday_normality_p:.3g} {weekly_weekend_normality_p:.3g}\n"
    "Weekly data equal-variance p-value: {weekly_levene_p:.3g}\n"
    "Weekly T-test p-value: {weekly_ttest_p:.3g}\n"
    "Mann–Whitney U-test p-value: {utest_p:.3g}"
)

def yearfilter(d):
    if d.year == 2012 or d.year == 2013:
        return True
    else:
        return False

def main():
    #reddit_counts = sys.argv[1]
    reddit_counts = 'reddit-counts.json.gz'
    reddit_counts = pd.read_json(reddit_counts, lines=True)
    reddit_counts['daynumber'] = reddit_counts['date'].apply(lambda x: datetime.date.weekday(x))

    reddit_counts_weekdays = reddit_counts[reddit_counts['daynumber'] < 5]
    reddit_counts_weekdays = reddit_counts_weekdays[reddit_counts_weekdays['subreddit'] == 'canada']
    reddit_counts_weekdays['year_valid'] = reddit_counts_weekdays['date'].apply(lambda x: yearfilter(x))
    reddit_counts_weekdays = reddit_counts_weekdays[reddit_counts_weekdays['year_valid']]
    
    reddit_counts_weekends = reddit_counts[reddit_counts['daynumber'] >= 5]
    reddit_counts_weekends = reddit_counts_weekends[reddit_counts_weekends['subreddit'] == 'canada']
    reddit_counts_weekends['year_valid'] = reddit_counts_weekends['date'].apply(lambda x: yearfilter(x))
    reddit_counts_weekends = reddit_counts_weekends[reddit_counts_weekends['year_valid']]

    reddit_counts_weekdays.drop(columns=['year_valid'], inplace=True)
    reddit_counts_weekends.drop(columns=['year_valid'], inplace=True)

    # student's t test
    ttest_invalid = stats.ttest_ind(reddit_counts_weekdays['comment_count'], reddit_counts_weekends['comment_count']).pvalue
    wdaynormaltest = stats.normaltest(reddit_counts_weekdays['comment_count']).pvalue
    wendnormaltest = stats.normaltest(reddit_counts_weekends['comment_count']).pvalue
    ilevene = stats.levene(reddit_counts_weekdays['comment_count'], reddit_counts_weekends['comment_count']).pvalue

    #Fix #1
    reddit_counts_weekdays['log_CC'] = reddit_counts_weekdays['comment_count'].apply(lambda x: np.log(x))
    reddit_counts_weekends['log_CC'] = reddit_counts_weekends['comment_count'].apply(lambda x: np.log(x))
    logwdaynormaltest = stats.normaltest(reddit_counts_weekdays['log_CC']).pvalue
    logwendnormaltest = stats.normaltest(reddit_counts_weekends['log_CC']).pvalue
    logilevene = stats.levene(reddit_counts_weekends['log_CC'], reddit_counts_weekdays['log_CC']).pvalue
    #print(logwdaynormaltest, logwendnormaltest, logilevene)

    reddit_counts_weekends['exp_CC'] = reddit_counts_weekends['comment_count'].apply(lambda x: np.exp(x)) #all inf
    reddit_counts_weekdays['exp_CC'] = reddit_counts_weekdays['comment_count'].apply(lambda x: np.exp(x)) #all inf
    
    reddit_counts_weekends['sqrt_CC'] = reddit_counts_weekends['comment_count'].apply(lambda x: np.sqrt(x))
    reddit_counts_weekdays['sqrt_CC'] = reddit_counts_weekdays['comment_count'].apply(lambda x: np.sqrt(x))
    sqrtwdaynormaltest = stats.normaltest(reddit_counts_weekdays['sqrt_CC']).pvalue
    sqrtwendnormaltest = stats.normaltest(reddit_counts_weekends['sqrt_CC']).pvalue
    sqrtilevene = stats.levene(reddit_counts_weekends['sqrt_CC'], reddit_counts_weekdays['sqrt_CC']).pvalue
    #print(sqrtwdaynormaltest, sqrtwendnormaltest, sqrtilevene) #Best result, the null hypothesis that the variances are equal is not rejected

    reddit_counts_weekends['count^2_CC'] = reddit_counts_weekends['comment_count'].apply(lambda x: x**2)
    reddit_counts_weekdays['count^2_CC'] = reddit_counts_weekdays['comment_count'].apply(lambda x: x**2)
    powwdaynormaltest = stats.normaltest(reddit_counts_weekdays['count^2_CC']).pvalue
    powwendnormaltest = stats.normaltest(reddit_counts_weekends['count^2_CC']).pvalue
    powilevene = stats.levene(reddit_counts_weekends['count^2_CC'], reddit_counts_weekdays['count^2_CC']).pvalue
    #print(powwdaynormaltest, powwendnormaltest, powilevene)

    plt.scatter(reddit_counts_weekdays['date'], reddit_counts_weekdays['comment_count'])
    plt.scatter(reddit_counts_weekends['date'], reddit_counts_weekends['comment_count'])
    plt.show()


    #Fix 2
    groupweekdays = pd.concat([reddit_counts_weekdays.drop(columns=['daynumber', 'log_CC', 'exp_CC', 'sqrt_CC', 'count^2_CC']), reddit_counts_weekdays['date'].apply(datetime.date.isocalendar).apply(pd.Series)], axis=1)
    groupweekdays.columns = ['date', 'subreddit', 'comment_count', 'isoyear', 'isoweek', 'isoday']
    groupweekends = pd.concat([reddit_counts_weekends.drop(columns=['daynumber', 'log_CC', 'exp_CC', 'sqrt_CC', 'count^2_CC']), reddit_counts_weekends['date'].apply(datetime.date.isocalendar).apply(pd.Series)], axis=1)
    groupweekends.columns = ['date', 'subreddit', 'comment_count', 'isoyear', 'isoweek', 'isoday']
    #groupweekdays = groupweekdays.copy()
    groupweekdays = groupweekdays.groupby(['isoyear', 'isoweek']).aggregate('mean').reset_index()
    groupweekends = groupweekends.groupby(['isoyear', 'isoweek']).aggregate('mean').reset_index()

    wdaynormaltest2 = stats.normaltest(groupweekdays['comment_count']).pvalue
    wendnormaltest2 = stats.normaltest(groupweekends['comment_count']).pvalue

    wlevene = stats.levene(groupweekdays['comment_count'], groupweekends['comment_count']).pvalue
    
    wttest = stats.ttest_ind(groupweekdays['comment_count'], groupweekends['comment_count']).pvalue

    #Fix 3
    utest = stats.mannwhitneyu(reddit_counts_weekends['comment_count'], reddit_counts_weekdays['comment_count'], alternative='two-sided').pvalue

    #print(reddit_counts_weekdays)
    #print(reddit_counts_weekends)
    #print(groupweekdays)
    #print(groupweekends)
    
    print(OUTPUT_TEMPLATE.format(
        initial_ttest_p=ttest_invalid,
        initial_weekday_normality_p=wdaynormaltest,
        initial_weekend_normality_p=wendnormaltest,
        initial_levene_p=ilevene,
        transformed_weekday_normality_p=sqrtwdaynormaltest,
        transformed_weekend_normality_p=sqrtwendnormaltest,
        transformed_levene_p=sqrtilevene,
        weekly_weekday_normality_p=wdaynormaltest2,
        weekly_weekend_normality_p=wendnormaltest2,
        weekly_levene_p=wlevene,
        weekly_ttest_p=wttest,
        utest_p=utest,
    ))


if __name__ == '__main__':
    main()