"""
stats_tests.py
Step 5: hypothesis tests. These are the SAME 5 tests as Statistics.py (run from main.py):
same variables, same sample sizes, same random_state=42 and same formulas,
so the dashboard shows exactly the numbers printed by the statistics step.

Every test returns a dictionary with: the null (h0) and alternative (h1) hypothesis,
the test statistic, the p-value, the decision and a one-line observation.

Rule used in every test (significance level = 0.05):
    p-value < 0.05  -> reject the null hypothesis (the difference is real)
    p-value >= 0.05 -> fail to reject the null hypothesis (the difference may be just chance)
"""
import numpy as np
from scipy import stats

ALPHA = 0.05
SEED = 42            # same random_state as Statistics.py


def finish(h0, h1, statistic, p_value, reject_text, accept_text, note, **extra):
    """Put every result in the same dictionary shape."""
    rejected = p_value < ALPHA
    result = {"h0": h0, "h1": h1, "statistic": statistic, "p_value": p_value,
              "rejected": rejected,
              "decision": "Reject H0" if rejected else "Fail to reject H0",
              "observation": reject_text if rejected else accept_text,
              "note": note}
    result.update(extra)
    return result


def one_sample_z_test(data, benchmark=35):
    """Test 1: is the average delivery time different from the benchmark? (sample of 500)"""
    sample = data["Delivery_Time_Minutes"].sample(500, random_state=SEED)
    mean = sample.mean()
    z = (mean - benchmark) / (sample.std() / np.sqrt(len(sample)))
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    direction = "higher" if mean > benchmark else "lower"
    return finish(
        f"average delivery time = {benchmark} minutes",
        f"average delivery time is not equal to {benchmark} minutes",
        z, p_value,
        f"Sample mean of delivery time (minutes) is {mean:.2f}, which is significantly {direction} than {benchmark}.",
        f"Sample mean of delivery time (minutes) is {mean:.2f}, which is not significantly different from {benchmark}.",
        "Random sample of 500 orders (random_state = 42)", sample_mean=mean)


def two_sample_z_test(data):
    """Test 2: Metropolitan vs Semi-Urban delivery time (500 orders each)."""
    metro = data[data["Region"] == "Metropolitan"]["Delivery_Time_Minutes"].sample(500, random_state=SEED)
    semi = data[data["Region"] == "Semi-Urban"]["Delivery_Time_Minutes"].sample(500, random_state=SEED)
    se = np.sqrt(metro.var() / len(metro) + semi.var() / len(semi))
    z = (metro.mean() - semi.mean()) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    higher = "Metropolitan" if metro.mean() > semi.mean() else "Semi-Urban"
    summary = f"Metropolitan ({metro.mean():.2f}) and Semi-Urban ({semi.mean():.2f})"
    return finish(
        "average delivery time of Metropolitan = average delivery time of Semi-Urban",
        "average delivery time of Metropolitan is not equal to Semi-Urban",
        z, p_value,
        f"{summary} have significantly different average delivery time (minutes); {higher} is higher.",
        f"{summary} do not have a significantly different average delivery time (minutes).",
        "500 random orders from each region (random_state = 42)",
        mean_a=metro.mean(), mean_b=semi.mean())


def one_sample_t_test(data, benchmark=35):
    """Test 3: same question as test 1 but with a small sample of 30 orders."""
    sample = data["Delivery_Time_Minutes"].sample(30, random_state=SEED)
    mean = sample.mean()
    t, p_value = stats.ttest_1samp(sample, popmean=benchmark)

    direction = "higher" if mean > benchmark else "lower"
    return finish(
        f"average delivery time = {benchmark} minutes",
        f"average delivery time is not equal to {benchmark} minutes",
        t, p_value,
        f"Sample mean of delivery time (minutes) is {mean:.2f}, which is significantly {direction} than {benchmark}.",
        f"Sample mean of delivery time (minutes) is {mean:.2f}, which is not significantly different from {benchmark}.",
        "Random sample of 30 orders (random_state = 42)", sample_mean=mean)


def two_sample_t_test(data):
    """Test 4: festive vs normal Final_Amount (40 orders each)."""
    festive = data[data["Festival_Flag"] == True]["Final_Amount"].sample(40, random_state=SEED)
    normal = data[data["Festival_Flag"] == False]["Final_Amount"].sample(40, random_state=SEED)
    t, p_value = stats.ttest_ind(festive, normal)

    higher = "Festive" if festive.mean() > normal.mean() else "Normal"
    summary = f"Festive ({festive.mean():.2f}) and Normal ({normal.mean():.2f})"
    return finish(
        "average final amount of festive orders = average final amount of normal orders",
        "average final amount of festive orders is not equal to normal orders",
        t, p_value,
        f"{summary} have significantly different average final amount (Rs); {higher} is higher.",
        f"{summary} do not have a significantly different average final amount (Rs).",
        "40 random orders from festive and 40 from normal months (random_state = 42)",
        mean_a=festive.mean(), mean_b=normal.mean())


def paired_t_test(data):
    """Test 5: delivered revenue of the same 12 months in 2024 and 2025."""
    delivered = data[data["Order_Status"] == "Delivered"]
    monthly = delivered.groupby(["Order_Year", "Order_Month"])["Final_Amount"].sum().unstack(0)
    before, after = monthly[2024], monthly[2025]
    difference = (after - before).mean()
    t, p_value = stats.ttest_rel(before, after)

    return finish(
        "monthly delivered revenue of 2024 = monthly delivered revenue of 2025",
        "monthly delivered revenue of 2024 is not equal to 2025",
        t, p_value,
        f"Average difference in monthly delivered revenue (Rs) from 2024 to 2025 is {difference:,.2f} "
        f"per month, and this change is significant.",
        f"Average difference in monthly delivered revenue (Rs) from 2024 to 2025 is {difference:,.2f} "
        f"per month, which is not significant (no real change).",
        "12 month pairs: every month of 2024 is paired with the same month of 2025",
        difference=difference)
