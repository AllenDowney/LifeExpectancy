# Healthy Life Expectancy and the Gender Gap — draft

*This is Part 5 in a series on gender gaps in life expectancy, what causes them, and what we can do about it.*

*Draft for review: same HALE outputs as the Bayesian panel model (IHME HALE and causes, 2000–2023), parallel to [Part 2](blog2_model.md) (LE coefficients and importance), [Part 3](blog3_counterfactual.md) (counterfactuals), and [Part 4](blog4_international.md) (intercepts). Narrative and wrap-up text still to finish.*

Figures below **alternate life expectancy (LE)** and **healthy life expectancy (HALE)** so pairs are easy to compare. (LE panels use OWID life expectancy; HALE uses IHME GBD 2023. Same model structure and cause gaps for both.)

---

## The HALE Gap

So far we've focused on life expectancy at birth, using data from [Our World in Data](https://ourworldindata.org/).
But the Global Gender Gap Report (GGGR) we cited in [Part 1](blog1_time_series.md) is based on healthy life expectancy (HALE), which is [expected years of good health](https://www.healthdata.org/research-analysis/about-gbd).
To replicate our analysis with health life expectancy, we used HALE data from the [IHME Global Burden of Disease](https://vizhub.healthdata.org/gbd-compare/).

The following figure shows the gender gap in HALE (female minus male) for OECD countries from 2000 to 2023. 

```{figure} figs/hale_gap_timeseries_blog_match.png
:width: 80%

HALE gender gap (2000–2023), same highlighted countries as above; other OECD countries in gray. Generated from `notebooks/time_series_figs.md`.
```

In 2023, the average HALE gap was 2.2 years
At the same time, the life expectancy gap was 5.1 years.
This difference suggests that some of the additional years that women live are not spent in good health.

The trends in HALE are similar to the trends in life expectancy we saw in [Part 1](blog1_time_series.md): decreasing in most countries, except during the COVID pandemic -- and increasing in the United States and Canada due to the opioid epidemic.

The table below summarizes ordinary least squares linear trends (slope in years of HALE per calendar year) for male HALE, female HALE, and the gender gap, 2000–2023, for the same OECD set used elsewhere in this series. The “Gap”, “Male HALE”, and “Female HALE” columns classify direction as up or down only when the two-sided *p*-value from `scipy.stats.linregress` is below 0.05; otherwise the label is “flat”. Values and directions match the export in `notebooks/time_series.md` (also in `notebooks/tables/hale_gap_and_levels_slopes_by_country.csv`).

```{include} tables/hale_gap_slopes_trends_by_country.html
```

The 2025 GGGR notes these decreasing gaps and concludes:

> While overall life expectancy by gender has remained more stable than healthy life expectancy, and women continue to outlive men, this indicates that the proportion of women’s lives spent in full health has declined relative to men.

In general, when we see a decreasing gap, it could indicate that health outcomes are getting worse in one group, improving in the other, getting worse at different rates, or getting better at different rates.

While this is technically true, it would be just as true to write that the proportion of men's lifes in good health has improved relative to women, but either summary is equally misleading.
If we only look at the gap, and not the life expectancies in both groups, we can't tell whether a closing gap is due to a decrease in one group, and increase in the other or -- as is actually the case -- increases in both groups, at difference rates.

---

## 2. Model: coefficients, importance, and residuals

With the HALE data, we ran a Bayesian hierarchical panel with the same predictors we used with the life expectancy data, described in [Part 2](blog2_model.md).
The following figure shows the estimated coefficients.

```{figure} figs/coefficients_hale.png
:width: 80%

Predictor coefficients for the **HALE** gender gap (posterior mean and 94% intervals). OECD, 2000–2023.
```

Road traffic deaths have the largest coefficient, about 0.46 years per standard deviation, which means that if a country is average in every way except that its gender gap in traffic deaths is one standard deviation above the mean, we expect its HALE gap to be 0.46 years above average. Other factors with large coefficients are lung disease, suicide, and homicide.

The coefficients for cardiovascular disease and diabetes are negative, just as in the life expectancy model.
As we discussed, a likely explantion is competing risks -- where death rates from other causes are low, cardiovascular disease and diabetes become more common causes of death, because they are diseases of aging.

The following table shows the coefficient for each cause, sorted by magnitude, and the rank of each cause in the two models.

| Cause | Coefficient | Rank (HALE) | Rank (LE) |
| --- | ---: | ---: | ---: |
| Road traffic | 0.463 | 1 | 1 |
| Lung disease | 0.367 | 2 | 5 |
| Suicide | 0.364 | 3 | 3 |
| Homicide | 0.307 | 4 | 2 |
| Cardiovascular | −0.273 | 5 | 7 |
| Cancer | 0.238 | 6 | 4 |
| Unintentional injury | 0.194 | 7 | 8 |
| Liver disease | 0.191 | 8 | 6 |
| Alcohol | 0.130 | 9 | 9 |
| Diabetes | −0.128 | 10 | 12 |
| COVID-19 | 0.060 | 11 | 10 |
| Drug disorders | 0.055 | 12 | 11 |
| Childhood (under-five) | 0.005 | 13 | 13 |

The rankings are consistent.
The biggest difference is that lung disease, which has the fifth largest coefficient in the life expectancy model, moves up to second in the HALE model.
The other differences are small and generally within the bounds we'd expect based on the uncertainty of the estimates.


## Importance

The magnitudes of the coefficients indicate the strength of the statistical relationship between death rate gaps and HALE. But they don’t tell us which factors contribute most to differences between countries and changes over time. For that, we'll use importance, which is the product of the coefficient and the standard deviation for each cause.

The following figure shows the importance of each cause of death in the HALE model.

```{figure} figs/importance_hale.png
:width: 80%

Predictor importance for the HALE gap (\|β\| × SD on the original scale).
```

The following table compares these results with the importances we computed in the life expectancy model in  [Part 2](blog2_model.md).

| Cause | HALE importance | Rank (HALE) | Rank (LE) |
| --- | ---: | ---: | ---: |
| Cardiovascular | 10.085 | 1 | 2 |
| Cancer | 9.079 | 2 | 1 |
| Homicide | 4.135 | 3 | 3 |
| Lung disease | 3.936 | 4 | 5 |
| Suicide | 3.481 | 5 | 4 |
| Unintentional injury | 2.955 | 6 | 8 |
| Road traffic | 2.737 | 7 | 6 |
| Liver disease | 1.858 | 8 | 7 |
| Alcohol | 0.811 | 9 | 11 |
| COVID-19 | 0.640 | 10 | 9 |
| Diabetes | 0.452 | 11 | 12 |
| Childhood (under-five) | 0.385 | 12 | 10 |
| Drug disorders | 0.154 | 13 | 13 |

The importance metrics are consistent between the HALE and life expectancy models -- the causes of death are ranked higher or lower by at most two spots.


## Goodness of fit

The model generally fits the data well.
The following figure shows the residuals (actual gaps minus the predictions from the model) for each country.

```{figure} figs/residuals_by_country_hale.png
:width: 80%

HALE model residuals by country (years); same layout as LE.
```

Most errors are less than 0.5 years and almost all are less than 1.0 years.
The model is more accurate for some countries than others, but the predictions are mostly unbiased -- that is, the average error for most countries is close to zero.

## Counterfactuals

Using the method described in [Part 3](blog3_counterfactual.md) we predicted counterfactual HALE for each country, assuming that the gap in each death rate could be lowered to the best observed value.

The following table shows the results for the United States.

```{include} tables/counterfactuals_usa_2023_hale_blog.html
```

This figure shows the counterfactual effects graphically.

```{figure} figs/counterfactual_effects_usa_2023_hale_bayesian.png
:width: 80%

HALE: hypothetical change in predicted gap if each cause-specific death-rate gap matched the best observed country-year, USA 2023, with 94% credible intervals.
```

The top factor is road traffic -- if the gap in death rates could be reduced from 13 to 1.92 per 100,000, the model predicts that the HALE gap would be reduced by 0.86 years.

The other leading contributors are suicide and drug disorders.
The top three factors in the HALE model are the same as in the life expectancy model.

The following figure shows how these contributions have changed over time.

```{figure} figs/positive_contributions_stacked_area_usa_hale.png
:width: 80%

HALE: stacked gap-closing contributions vs predicted and actual HALE gap, USA.
```

The trends are the same as the onces we saw in life expectancy.
The total has generally increased, driven by a large increase in the contribution of drug disorders and smaller increases in the contributions of suicide and road traffic. 




## Discussion




And maybe this rhetoric:

Suppose we observe that girls and women and suffer from eating disorder at higher rates than boys and men -- the ratio of lifetime prevalence is 2-3.
And suppose I offered as explanation that women are more neurotic than men -- the difference is 0.3 to 0.5 standard deviations -- and neuroticism is associated with eating disorders -- which is also true.
Now, suppose I conclude from these observations that the gender gap in eating disorders is biologically determined, and there's nothing we can or should do about it.
Suppose further that the ratio varies widely across countries and over time, but ignoring that variation, I claim that an average risk ratio of 2.5 is natural -- and take it as a benchmark for comparisons between countries.
Then, if we observe a lower ratio -- that is, a smaller gap -- in a particular country, we take that as evidence of disadvantage for men in that country.

Most people would immediately see problems with that conclusion:

1) Even if women are more neurotic than men, we don't know that the difference is biological. There could be other causes.

2) Even if neuroticism is associated with eating disorders, that doesn't mean neuroticism explains the entire difference -- and we have plenty of evidence for other contributing factors, including internalization of societal preference for thinness.

3) Even if the difference in neuroticism is natural, and even if it explains part of the gender gap, that doesn't mean there's nothing we can do about it. We have a long history of using public health and safety policies to mitigate the negative consequences of natural vulnerability.

Generalizing from this example, we might suggest consider the principle that when we see that a particular group suffers harm at higher rates, we should allocate resources to identify causes and look for solutions.
Further, we might adopt the principle that a policy to address suffering should include general efforts to help everyone, as well as targeted efforts to help groups with the highest rates -- in proportions that depend in part on which measures are more effective.
And finally, we might find it unwarranted to take an observed difference in the present and make it a benchmark for the future.

In my opinion, those objections are valid, and these principles are solid.
Now let's apply them to another example...

---

## Regenerating artifacts

- **LE / HALE coefficient, importance, and HALE residual PNGs:** from `notebooks/`, run  
  `jupytext --to ipynb bayesian_le_figs.md --output bayesian_le_figs.ipynb` then  
  `papermill bayesian_le_figs.ipynb bayesian_le_figs_executed.ipynb`  
  (LE: `blog2_*_le.png`; HALE: `coefficients_hale.png`, `importance_hale.png`, `residuals_timeseries_hale.png`, `residuals_by_country_hale.png`.)
- **Counterfactuals / intercepts:** `notebooks/bayes_counter_le.md` and `notebooks/bayes_counter_hale.md` → papermill.
- **Fit posteriors:** `notebooks/bayesian_model.md` (suffix `*_ihme_nomid_nogrw_y2023_covid`).
- **HALE gap / levels trend table (`jb/tables/hale_gap_slopes_trends_by_country.html`):** run `notebooks/time_series.md` through the cell that writes that file (or the full notebook).
