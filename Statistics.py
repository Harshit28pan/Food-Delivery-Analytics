"""
Statistics module (sampling, CLT, normality, hypothesis tests)
Only functions here. They are called from main.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

import EDA as eda

CHART_FOLDER = "statistics_charts"
os.makedirs(CHART_FOLDER, exist_ok=True)


# ---------------- SAMPLING ----------------
# Population = all 100,000 orders. Sample = a small part of it.

def simple_random_sample(data, column, size):
    # every order has an equal chance of being picked
    return data[column].sample(n=size, random_state=42)


def stratified_sample(data, column, group_column, fraction=0.005):
    # pick the same % of orders from every group (here: every region)
    sample = data.groupby(group_column).sample(frac=fraction, random_state=42)
    return sample[column]


def systematic_sample(data, column, step):
    # pick every 'step'-th order (every 200th order)
    return data[column].iloc[::step]


# ---------------- CENTRAL LIMIT THEOREM ----------------
# Idea: take many samples, find the mean of each sample.
# These sample means form a bell curve, even if the original data is not bell shaped.

def central_limit_theorem(data, column, sample_size=50, repeats=200):
    population = data[column]

    sample_means = []
    for i in range(repeats):
        sample = population.sample(n=sample_size, random_state=i)
        sample_means.append(sample.mean())
    sample_means = pd.Series(sample_means)

    # standard error = std of the sample means = population std / sqrt(sample size)
    formula_se = population.std() / np.sqrt(sample_size)
    actual_se = sample_means.std()

    print("\nCLT for", column)
    print("Population mean      :", round(population.mean(), 2))
    print("Mean of sample means :", round(sample_means.mean(), 2))
    print("Standard error (formula):", round(formula_se, 2))
    print("Standard error (actual) :", round(actual_se, 2))

    plt.figure(figsize=(8, 5))
    sns.histplot(sample_means, kde=True, color=eda.TEAL)
    plt.title("CLT: distribution of sample means - " + column)
    plt.xlabel("Sample mean")
    eda.save_chart(CHART_FOLDER, "CLT_" + column + ".png")


# ---------------- NORMALITY ----------------
# Skewness: 0 = symmetric. Kurtosis: 0 = normal-like tails.

def check_normality(data, column):
    values = data[column]

    print("\nNormality check for", column)
    print("Skewness:", round(stats.skew(values), 2))
    print("Kurtosis:", round(stats.kurtosis(values), 2))

    plt.figure(figsize=(8, 5))
    sns.histplot(values, kde=True, color=eda.TEAL)
    plt.title("Normality check - " + column)
    eda.save_chart(CHART_FOLDER, "Normality_" + column + ".png")


# ---------------- HYPOTHESIS TESTING ----------------
# Every test has two hypotheses:
# H0 (null hypothesis)        : there is no difference / no change
# H1 (alternative hypothesis) : there is a difference / a change
# Significance level = 0.05. If p-value < 0.05, reject H0, otherwise fail to reject H0.

def show_result(test_name, h0, h1, statistic, p_value, reject_text, accept_text):
    print("\n" + test_name)
    print("H0 (null)       :", h0)
    print("H1 (alternative):", h1)
    print("Test statistic  :", round(statistic, 4))
    print("P-value         :", f"{p_value:.4g}")   # .4g keeps very small p-values visible (not 0)
    if p_value < 0.05:
        print("Decision        : p < 0.05, reject H0")
        print("Observation     :", reject_text)
    else:
        print("Decision        : p >= 0.05, fail to reject H0")
        print("Observation     :", accept_text)


def one_sample_z_test(sample, benchmark, label, h0, h1):
    # Is the sample mean different from the benchmark? (n >= 30)
    # z = (sample mean - benchmark) / (std / sqrt(n))
    n = len(sample)
    mean = sample.mean()
    z = (mean - benchmark) / (sample.std() / np.sqrt(n))
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))        # two-sided

    direction = "higher" if mean > benchmark else "lower"
    reject_text = f"Sample mean of {label} is {mean:.2f}, which is significantly {direction} than {benchmark}."
    accept_text = f"Sample mean of {label} is {mean:.2f}, which is not significantly different from {benchmark}."
    show_result("One sample Z-test", h0, h1, z, p_value, reject_text, accept_text)


def two_sample_z_test(sample1, sample2, name1, name2, label, h0, h1):
    # Are the means of two groups different? (n >= 30 in both)
    # z = (mean1 - mean2) / sqrt(var1/n1 + var2/n2)
    mean1, mean2 = sample1.mean(), sample2.mean()
    se = np.sqrt(sample1.var() / len(sample1) + sample2.var() / len(sample2))
    z = (mean1 - mean2) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    higher = name1 if mean1 > mean2 else name2
    reject_text = (f"{name1} ({mean1:.2f}) and {name2} ({mean2:.2f}) have significantly different "
                   f"average {label}; {higher} is higher.")
    accept_text = (f"{name1} ({mean1:.2f}) and {name2} ({mean2:.2f}) do not have a significantly "
                   f"different average {label}.")
    show_result("Two sample Z-test", h0, h1, z, p_value, reject_text, accept_text)


def one_sample_t_test(sample, benchmark, label, h0, h1):
    # Same as the Z-test, but used for small samples (n < 30)
    mean = sample.mean()
    t, p_value = stats.ttest_1samp(sample, popmean=benchmark)

    direction = "higher" if mean > benchmark else "lower"
    reject_text = f"Sample mean of {label} is {mean:.2f}, which is significantly {direction} than {benchmark}."
    accept_text = f"Sample mean of {label} is {mean:.2f}, which is not significantly different from {benchmark}."
    show_result("One sample T-test", h0, h1, t, p_value, reject_text, accept_text)


def two_sample_t_test(sample1, sample2, name1, name2, label, h0, h1):
    # Same as the two sample Z-test, but for small samples
    mean1, mean2 = sample1.mean(), sample2.mean()
    t, p_value = stats.ttest_ind(sample1, sample2)

    higher = name1 if mean1 > mean2 else name2
    reject_text = (f"{name1} ({mean1:.2f}) and {name2} ({mean2:.2f}) have significantly different "
                   f"average {label}; {higher} is higher.")
    accept_text = (f"{name1} ({mean1:.2f}) and {name2} ({mean2:.2f}) do not have a significantly "
                   f"different average {label}.")
    show_result("Two sample T-test", h0, h1, t, p_value, reject_text, accept_text)


def paired_t_test(before, after, name_before, name_after, label, h0, h1):
    # Same group measured twice (here: the same 12 months in two different years).
    # The test is done on the difference (after - before) of every pair.
    difference = (after - before).mean()
    t, p_value = stats.ttest_rel(before, after)

    reject_text = (f"Average difference in {label} from {name_before} to {name_after} is {difference:,.2f} "
                   f"per month, and this change is significant.")
    accept_text = (f"Average difference in {label} from {name_before} to {name_after} is {difference:,.2f} "
                   f"per month, which is not significant (no real change).")
    show_result("Paired T-test", h0, h1, t, p_value, reject_text, accept_text)
