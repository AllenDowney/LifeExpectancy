# The Life Expectancy Gender Gap: Evidence and Policy

## Executive summary

In most countries, women live longer than men -- but the life expectancy gap is not inevitable.
It depends on public health and safety policy, economic conditions, and demographics. 

The size of the gap differs between countries and varies over time.

* Between 2000 and 2023, the largest gap in OECD countries is 12.7 years (Lithuania, 2007); the smallest is 2.5 years (Israel, 2015).

* Over that interval, the OECD average decreased from 6.5 to 5.1 years. The gap narrowed in 35 out of 38 OECD countries; in 8 of them it narrowed by more than two years.

The magnitude of these changes suggests that a large part of the observed gap is contingent.

To see what factors contribute to the gap, we identify causes of death with large gender gaps and use a statistical model to estimate the part of the life expectancy gap explained by each.
In the United States, the largest contributors are road traffic (0.8 years), drug disorders (0.8 years), and suicide (0.5 years).
Other contributing factors are homicide (0.3 year), liver disease (0.2 years), cancer (0.2 years), and alcohol (0.2 years).
In 2023 these causes of death accounted for 62% of the observed life expectancy gap (3.1 out of 5.0 years).

Leading contributors differ by region: 

* In North America, drug disorders and suicide are large contributors.

* In the Latin American members of the OECD, road traffic is a leading factor; in Mexico and Colombia, homicide is the top factor.

* In Northern European countries, suicide is a leading factor, and in most, cancer is as well.

* Compared to Northern Europe, the life expectancy gaps are bigger in Baltic Countries, but the leading factors are similar, including cancer and suicide.

* The life expectancy gaps in Western Europe are among the smallest.
Cancer is a leading factor in every country; suicide, lung disease, and liver disease are also common.

* In Eastern European OECD countries, cancer, suicide and liver disease are leading factors in every country.

* The patterns in Australia and New Zealand are similar to Western Europe, where cancer and suicide are often leading factors, along with road traffic.

Comparisons with other countries suggest that gender gaps in these death rates can be narrowed with effective policies -- and if so, we would expect a corresponding reduction in the life expectancy gap.

To demonstrate the effect of public safety on the life expectancy gap, we consider road safety programs in the EU, which successfully reduced road traffic death rates by more than 50% between 2000 and 2020.
According to our model, lower death rates (for both men and women) closed the death rate gap, in every European country in the dataset, in many cases by more than a year.
In six countries, the remaining contribution (estimated for 2023) is less than 0.1 years.
This example suggests that the observed difference in road traffic death rates is not entirely the result of gender-based differences in behavior, and that the effect of the differences can be substantially mitigated.

In addition to period life expectancy, we also consider the gap in healthy life expectancy (HALE).
Over time, healthy life expectancy in most OECD countries has increased for both men and women, and the gap has narrowed.
The causes of death with the largest effect on HALE are mostly the same as the ones with the largest effect on life expectancy.
Together, they might account for a larger fraction of the observed gaps.

Premature male mortality imposes substantial social and economic costs through lost productivity, disability, caregiving burdens, and reduced family stability.
Our analysis highlights three areas where policies to reduce death rates would have the largest effect on the life expectancy gap in the United States: road traffic safety, substance abuse prevention and harm reduction, and suicide prevention.
Other policies that could reduce the gap include violence prevention and reduction of smoking and alcohol consumption.

## The gap differs between counties and over time

Looking at differences between countries and changes over time, we find numerous examples where life expectancy gaps depend on public health and safety policy, economic conditions, and demographics. 

The following figure shows the gender gap in life expectancy for 38 OECD countries from 2000-2023, with selected countries labeled.

```{figure} figs/le_gap_timeseries_selected.png
:width: 80%

Life expectancy gender gap (2000–2023), OECD countries.
From Our World in Data (OWID) - Combines Human Mortality Database (2025) and UN World Population Prospects (2024).
```

A positive gap means women live longer. The dashed line shows the OECD average.

The differences between countries are large.
The largest gap in the dataset was 12.7 years in Lithuania in 2007.
The smallest was just 2.5 years in Israel in 2015.

In 2023 the largest gaps are in Lithuania, Latvia, and Estonia, all greater than 8 years.
The smallest gaps are in Norway, the Netherlands, Luxembourg, and New Zealand, all less than 3.5 years.
The United States is close to the OECD average at 5.0 years.

Notably, some of the largest gaps are in Baltic countries, and some of the smallest in Scandinavia.
A ferry from Tallinn to Stockholm travels 240 miles and closes the gender gap from 8.1 years in Estonia to 3.7 years in Sweden.

There are also large differences over time.
The OECD average dropped from 6.5 to 5.1 between 2000 and 2023 at an average rate of 0.6 years per decade.
The largest decrease was in Estonia, at a rate of 1.5 years per decade.
Gaps in Slovenia, Lithuania, Colombia, and Hungary have also closed faster than 1.0 years per decade.
The only increases were in Mexico (0.8 years per decade) and Costa Rica (0.3 years per decade).

In the United States, the gap closed slightly between 2000 and 2015, then increased due to the opioid epidemic and COVID.
Since 2021 it has decreased again as deaths due to both causes have declined.
The net change is a decrease from 5.3 in 2000 to 5.0 in 2023.
The pattern in Canada is similar to the U.S.

The large differences between countries and the consistent decline in almost all OECD countries suggest that the gender gap in life expectancy is not inevitable.


## Men's death rates are higher for most causes

For many of the most common causes of death, there is a substantial gender gap, and for most of them, the death rate is higher for men.
And because cause-specific death rates contribute to age-specific death rates, they affect life expectancy.

By comparing death rates between countries and changes over time, we can start to identify factors likely to contribute to the life expectancy gap.

We'll use cause-specific death rates from the [Global Burden of Disease (GBD)](https://www.healthdata.org/research-analysis/gbd) study, produced by the Institute for Health Metrics and Evaluation (IHME).
This dataset includes death rates by cause, sex, country, and year, with a consistent methodology 

### Drug Use Disorders

As a first example, it is likely that the increasing gap in the United States between 2015 and 2020 was caused at least in part by the opioid epidemic.
To see whether that explanation is plausible, we'll consider death rates due to drug disorders in OECD countries between 2000 and 2023.

```{figure} figs/drug_disorders_gap_timeseries_selected.png
:width: 80%

Drug use disorders, death rate gender gap (2000–2023), OECD countries.
Source: Global Burden of Disease from IHME.
```

The most notable feature is the increase in the United States and Canada after 2013, which aligns with the [third and fourth waves of the opioid epidemic](https://en.wikipedia.org/wiki/Opioid_epidemic_in_the_United_States), attributed to synthetic opioids like fentanyl.
In the United States, the fourth wave peaked in 2022 with 107,000 deaths in a single year.
Men account for about 70% of opioid overdose deaths.
The pattern is similar in Canada, although the gaps are lower throughout.

In many other countries, the gap declined slowly, with the steepest decline in Norway.
Other than the United States and Canada, the biggest increases were in Lithuania and the United Kingdom.

The smallest gap was essentially zero in Japan in 2013; the smallest current gap is in South Korea.
In both countries, social stigma against illicit drug use, conservative prescribing practices, and strict narcotics controls likely limited opioid markets.


### Homicide

In most countries, men are more likely to be victims of homicide.
The following figure shows gender gaps in death rates due to interpersonal violence.

```{figure} figs/homicide_gap_timeseries_selected.png
:width: 80%

Homicide, death rate gender gap (2000–2023), selected OECD countries.
Source: Global Burden of Disease from IHME.
```

The smallest gap was in Norway in 2019, when the rate was 0.48 for men and 0.55 for women, one of few instances where the female rate was slightly higher.
Currently the smallest gap is in Switzerland, where the rates are 0.47 and 0.45.

The largest gap was in Colombia in 2002: the homicide rate was 158 per 100,000 for men and 18 for women, a difference of 140 (truncated in the chart).
In Colombia in the early 2000s, homicide rates were among the highest in the world, due to armed conflict, paramilitary violence, drug trafficking networks, and weak state control in some regions.
Nearly nine out of ten victims were men.
When homicide declined, the gender gap narrowed.

Other than Colombia, the largest decreases were in the Baltic countries.
The largest increases were in Mexico, Costa Rica, and the United States.

In the United States, homicide rates for men and women declined between 2000 and 2014, and the gap shrank.
Since then, the gap has increased, driven primarily by firearm homicides.
A sharp rise in 2020 coincided with pandemic-related social disruption and increased gun purchasing.
During this period, the homicide rate for men increased much more than the rate for women, so the gap expanded.
The net effect is an increase from 6.6 in 2000 to 8.8 in 2023.


### Suicide

In every OECD country, men are more likely than women to die by suicide.
The following figure shows gender gaps in death rates due to self-harm.

```{figure} figs/suicide_gap_timeseries_selected.png
:width: 80%

Suicide, death rate gender gap (2000–2023), selected OECD countries.
Source: Global Burden of Disease from IHME.
```

The gender gap is much higher in Lithuania than in any other OECD country, driven by extraordinary male suicide rates in the aftermath of post-Soviet economic disruption.
Since 2000, those rates have fallen sharply.

Other countries with large gaps are Latvia and South Korea, both over 20 per 100,000.
South Korea’s suicide rate rose sharply after the 1997 Asian financial crisis, especially among working-age and elderly men.
Economic disruption, elderly poverty, alcohol use, and limited mental health access are likely contributing factors.

The countries with the smallest gaps — and lowest rates — are Turkey, Greece, and Israel.
These low rates might be explained by cultural characteristics, but they might also reflect classification practices.

In the United States, suicide rates have increased for both men and women, but they have increased about three times faster for men, so the gender gap has grown from 14 in 2000 to 18 in 2023.
The increase has been driven in part by firearm suicides, which are more lethal.
Economic instability, declining labor-force attachment among less-educated men, substance abuse, and social isolation are likely contributing factors.
In 2023, the rate for men was 24.2 per 100,000, almost four times the rate for women, 6.5 per 100,000.


### Road Traffic

In every OECD country, death rates due to road traffic are higher for men than for women, in part because of greater exposure, that is, more miles traveled.
The following figure shows gender gaps in death rates due to road traffic.

```{figure} figs/road_traffic_gap_timeseries_selected.png
:width: 80%

Road traffic, death rate gender gap (2000–2023), selected OECD countries.
Source: Global Burden of Disease from IHME.
```

The most apparent change is the decline in Lithuania, from worst in 2005 to close to the OECD average.
This decline followed EU accession in 2004, which brought stricter enforcement, infrastructure investment, and vehicle safety improvements.
Alcohol-control measures and speed enforcement also contributed.

Also apparent is the divergence of Mexico and Costa Rica.
Costa Rica's traffic mortality declined alongside strengthened enforcement and road safety initiatives, while Mexico's worsened amid institutional strain, rising motorcycle use, and uneven traffic law enforcement.

In the United States, the gap narrowed slightly between 2000 and 2010, then grew from 10 in 2010 to 13 in 2023.
This change is driven primarily by the increase in death rates for men, from 17.5 in 2010 to 21 in 2023.

The widening gap reflects both exposure and risk per mile.
Men in the United States drive about 60 percent more vehicle miles per year than women, and a disproportionate share of those miles occur in higher-risk settings such as nighttime and rural driving.
Adjusting for miles driven removes roughly half of the raw male-female difference in fatalities.
But even per mile driven, risk for men is higher, primarily due to higher rates of speeding, alcohol impairment, and lower seatbelt use.


### Gender gaps are contingent

In all of these cause-specific death rates, we see large differences between countries and large changes over time.
We can identify likely causes for these differences, including

* Historical shocks, such as armed conflict in Colombia, the collapse of the Soviet Union, the Asian financial crisis, and the COVID pandemic.

* Economic structure and labor-market conditions, including unemployment, deindustrialization, and elderly poverty.

* Social and institutional conditions, such as family structure, social isolation, mental health access, and law enforcement capacity.

* Cultural norms and behavioral patterns, including alcohol use, stigma around drug use, and norms surrounding risk-taking and help-seeking.

* Public health and safety policies, such as the Vision Zero road safety program, alcohol-control reforms in Lithuania, narcotics regulation, and vehicle and firearm policies.

Gender gaps in cause-specific death rates are highly contingent, and they contribute directly to gender gaps in life expectancy.

### Gender gaps are causative

By construction, differences in cause-specific death rates contribute to differences in age-specific death rates, which contribute to differences in period life expectancy.

For that reason, these factors are causal in the counterfactual sense — if the gaps in the death rates were smaller, the gap in life expectancy would be smaller — and in the intervention sense — if a public health policy is able to reduce these rates, it would cause the life expectancy gap to close.

We note that there are two ways to reduce cause-specific death rates:

* If a gender-targeted intervention reduces death rates for men more than for women, it would decrease the gender gap.

* Less obviously, if a general intervention is equally effective for men and women — in the sense that it decreases rates by the same percentage — it would also decrease the gender gap. For example, the 2023 death rates due to drug use disorders in the United States were 41 for men and 17 for women, a gap of 24 deaths per 100,000.
If both rates were cut by 50%, they would be 20.5 and 8.5, a gap of 12.

In general, an intervention that improves health outcomes is likely to decrease the life expectancy gap.

## Modeling the Life Expectancy Gap

We built a panel model that uses 24 years of data from 37 OECD countries.
It includes gender gaps in 13 cause-specific death rates from the [Global Burden of Disease (GBD)](https://www.healthdata.org/research-analysis/gbd) study: alcohol, suicide, homicide, road traffic injuries, cardiovascular disease, diabetes, cancer, lung disease, liver disease, unintentional injury, drug disorders, childhood mortality (under-5), and COVID-19.

For each cause of death, the model estimates a coefficient that shows how much the life expectancy gap changes for each standard-deviation increase in cause-specific gap.
Positive coefficients mean that when a death rate gap is larger (men die at higher rates than women), the life expectancy gap is larger (women live longer).

The following figure shows the estimated coefficients; the error bars show 94% credible intervals.

```{figure} figs/blog2_coefficients_le.png
:width: 80%

Cause of death coefficients for life expectancy gender gap (2000–2023).
Source: IHME cause-specific death rates, OWID Life Expectancy, analysis by Allen Downey.
```

Road traffic deaths have the largest coefficient, about 0.43 years per standard deviation, which means that if a country is average in every way except that its gender gap in traffic deaths is one standard deviation above the mean, we expect its life expectancy gap to be 0.43 years above average.
Other factors with large coefficients are homicide, suicide, cancer, lung disease, and liver disease.

The magnitudes of these coefficients depend on both death rates and the ages of the people affected.
Cancer and respiratory disease have high rates, but they primarily affect older people, so their effect on life expectancy is attenuated.
Homicide and suicide have lower rates, but they affect younger people, so their effect on life expectancy is amplified.

Child mortality affects the youngest people, so each death removes many potential years of life.
But the estimated coefficient is small, and the lower bound of the credible interval is close to zero. 
In most OECD countries the gender gap in child mortality is already small and changes only slowly over time. 
So the model detects only a weak relationship between variation in child mortality and life expectancy.

The coefficient of alcohol is relatively small, but that is partly the result of classification.
In the GBD database, alcohol-related deaths are defined narrowly, not including indirect effects — such as liver disease, cancer, road traffic, homicide, suicide, and accidental injury — where alcohol is often a contributing factor.

Similarly, we note the underlying effect of smoking, which contributes to gaps in death rates due to cancer, cardiovascular disease, respiratory disease, and possibly COVID-19.

The model quantifies the relationship between death rate gaps and the life expectancy gap, across countries and time.
We can use this model to estimate, for each country, the contribution of each cause of death to the life expectancy gap.

We'll present a detailed analysis for the United States and then summarize results from other countries.

## Counterfactuals

As an indication of what's possible, we'll consider the smallest observed gap for each cause-specific death rate.
The following table shows the minimum gap, in deaths per 100,000 people, across all 37 countries and 24 years, and the country and year where it occurred.

```{include} tables/policy_gap_extremes_min_blog_le.html
```

For example, in Ireland in 2021, the gap in childhood mortality rates was only 0.59 per 100,000, substantially smaller than the OECD average, about 22 per 100,000.
This small difference seems to be due to an unusually low rate for boys, rather than a high rate for girls.
This example suggests that the gap in child mortality can be close to zero.

The rate gap for several causes is negative, which means that in some places and times, the usual pattern is reversed and death rates are higher for women.
For these causes, we assume that if the gaps can be negative or positive, they can also be zero.

Some gaps might be harder to close than others.
The smallest rate gap for suicide is about 4 per 100,000, reported in Greece in 2002.
The OECD average is about 14.

To be conservative, we'll assume that the smallest observed gap is the smallest attainable gap. 

### Road traffic is the largest contributor in the U.S.

In 2023, the life expectancy gap in the United States was 5.0 years, close to the OECD average.
The following table shows how much this gap would change, according to the model, if we reduced each cause-specific gap to its best attainable level.

```{include} tables/policy_counterfactuals_usa_2023_le_blog.html
```

The following figure shows the results graphically, with 94% credible intervals.

```{figure} figs/counterfactual_effects_usa_2023_le_bayesian.png
:width: 80%

Counterfactual effects: hypothetical change in life expectancy gap for each cause-specific death rate, United States (2023), 94% credible intervals.
```

Road traffic has the largest potential impact — reducing the death rate gap to Iceland's 2017 level would close the life expectancy gap by 0.81 years.

Drug disorders are second — reducing the gap to Japan's 2013 level (essentially zero) would close the life expectancy gap by 0.77 years.

And if the rate gap due to suicide could be reduced from 18 to 4 per 100,000, the model predicts the life expectancy gap would close by 0.52 years.

For homicide, liver disease, cancer, and alcohol, the potential impact is smaller but still meaningful.
The potential impact of childhood mortality and injury is smaller still, and for COVID-19 in 2023 it is near zero.

For lung disease, the gender gap in the U.S. is negative, meaning that the death rate is higher for women.
So if we close this gap to zero, the life expectancy gap might grow by 0.18 years.

For cardiovascular disease and diabetes, the estimated coefficient is negative, which means that if we reduce the rate gap, the model predicts that the life expectancy gap would grow.
However, these negative coefficients might be explained by competing risks — if general health outcomes are better, more people live long enough to die from diseases of aging, so those rates tend to be higher.
If that's true, the counterfactual assumption might not hold — that is, if an intervention is able to reduce these gaps, it's not clear what effect that would have on life expectancy.

But for the other causes of death, the counterfactual assumption is plausible.
For example, if the rate gap due to drug disorders closes — which is likely as overall rates have already started to fall — it is reasonable to expect the life expectancy gap to close, other things being equal.

The total of the gap-closing effects is about 3.1 years, which suggests that together they could reduce the life expectancy gap from 5.0 to 2.9 years.

In reality these effects are likely to interact.
For example, a decrease in consumption of alcohol would directly affect death rates due to alcohol, and indirectly affect rates due to liver disease, cancer, road traffic, accidents, suicide, homicide, and possibly drug disorders.
With these kinds of interactions, the total effect of multiple interventions might be larger or smaller than the sum of the estimates from the model.

Nevertheless, the magnitudes of the contributions indicate which interventions have the most potential to reduce the life expectancy gap.

The following figure shows how the positive contributions to the gap have changed over time.

```{figure} figs/positive_contributions_stacked_area_usa_le.png
:width: 80%

Stacked positive contributions to the life expectancy gap, United States (2000–2023).
```

The total has generally increased, driven by a large increase in the contribution of drug disorders and smaller increases in the contributions of suicide and road traffic.
But this pattern is unusual; in most OECD countries, the total contribution decreased over this period.


### Different regions, different causes

For each country, we identify the factor that makes the largest contribution to the life expectancy gap and additional factors with a contribution at least half as big.

Starting in North America, the following list shows the current gender gap in each country, the leading factors, and how much of the gap could be closed if each factor was lowered to the smallest observed value.

- **United States** (5.37 years): Road Traffic (-0.81), Drug Disorders (-0.77), Suicide (-0.52)
- **Canada** (4.61 years): Drug Disorders (-0.51), Cancer (-0.36), Suicide (-0.34)

Canada is the only OECD country where drug deaths are the top factor.
If the gender gap in drug disorders could be closed to the smallest observed gap (essentially zero), it would close the life expectancy gap by about half a year, according to the model.

In every Latin American country, road traffic is a leading factor; in Mexico and Colombia, homicide is the top factor.

- **Colombia** (6.03 years): Homicide (-1.61), Road Traffic (-1.48)
- **Costa Rica** (6.01 years): Road Traffic (-1.77)
- **Mexico** (4.93 years): Homicide (-1.32), Road Traffic (-1.06), Liver Disease (-0.75)
- **Chile** (4.60 years): Road Traffic (-0.88), Liver Disease (-0.45)

In every Northern European country, suicide is a leading factor, and in most, cancer is as well.

- **Finland** (5.76 years): Lung Disease (-0.56), Liver Disease (-0.47), Suicide (-0.39)
- **Denmark** (3.93 years): Cancer (-0.47), Suicide (-0.26), Alcohol (-0.25), Liver Disease (-0.24)
- **Norway** (3.61 years): Cancer (-0.33), Suicide (-0.23)
- **Sweden** (3.45 years): Suicide (-0.28), Drug Disorders (-0.15), Cancer (-0.14)
- **Iceland** (3.25 years): Suicide (-0.37), Cancer (-0.21)

Compared to Northern Europe, the life expectancy gaps are bigger in Baltic countries, but the leading factors are similar, including cancer and suicide.

- **Latvia** (9.73 years): Cancer (-0.95), Suicide (-0.83), Road Traffic (-0.71), Cardiovascular (-0.59), Lung Disease (-0.53)
- **Lithuania** (8.78 years): Suicide (-1.17), Cancer (-0.87), Liver Disease (-0.60)
- **Estonia** (8.71 years): Liver Disease (-0.71), Cancer (-0.66), Suicide (-0.60), Lung Disease (-0.50), Alcohol (-0.48), Cardiovascular (-0.44)

The life expectancy gaps in Western Europe are among the smallest.
Cancer is a leading factor in every country; suicide, lung disease, and liver disease are also common.

- **France** (6.17 years): Cancer (-0.84), Suicide (-0.53)
- **Portugal** (5.92 years): Cancer (-1.19)
- **Spain** (5.29 years): Cancer (-0.94), Lung Disease (-0.71)
- **Germany** (4.81 years): Cancer (-0.58), Suicide (-0.44), Liver Disease (-0.42), Lung Disease (-0.35)
- **Austria** (4.77 years): Suicide (-0.55), Cancer (-0.44), Liver Disease (-0.38)
- **Italy** (4.43 years): Cancer (-0.67), Lung Disease (-0.45), Road Traffic (-0.34)
- **Belgium** (4.38 years): Lung Disease (-0.61), Cancer (-0.50), Suicide (-0.50)
- **United Kingdom** (3.96 years): Cancer (-0.36), Suicide (-0.21), Drug Disorders (-0.21), Liver Disease (-0.20)
- **Switzerland** (3.87 years): Cancer (-0.41), Suicide (-0.28)
- **Ireland** (3.84 years): Cancer (-0.30), Suicide (-0.19)
- **Netherlands** (3.40 years): Cancer (-0.49)
- **Luxembourg** (3.39 years): Liver Disease (-0.27), Cancer (-0.26), Suicide (-0.17), Lung Disease (-0.17), Cardiovascular (-0.15)

In Eastern Europe, cancer, suicide and liver disease are leading factors in every country.

- **Poland** (7.16 years): Suicide (-0.66), Cancer (-0.59), Liver Disease (-0.58), Alcohol (-0.48), Road Traffic (-0.42)
- **Slovakia** (6.79 years): Liver Disease (-0.78), Cancer (-0.67), Suicide (-0.48)
- **Hungary** (6.24 years): Liver Disease (-0.94), Suicide (-0.61), Cancer (-0.53)
- **Czechia** (5.60 years): Cancer (-0.53), Suicide (-0.49), Liver Disease (-0.46), Lung Disease (-0.43), Road Traffic (-0.30)
- **Slovenia** (5.50 years): Cancer (-0.68), Suicide (-0.68), Alcohol (-0.46), Cardiovascular (-0.43), Liver Disease (-0.39), Lung Disease (-0.35)

The patterns in other OECD countries are similar to Western Europe, where cancer and suicide are often leading factors, along with road traffic.

- **Australia** (4.04 years): Cancer (-0.50), Suicide (-0.34)
- **New Zealand** (3.67 years): Cancer (-0.31), Suicide (-0.30), Road Traffic (-0.30)
- **Greece** (5.73 years): Cancer (-1.11), Road Traffic (-0.61)
- **Japan** (6.88 years): Lung Disease (-1.19), Cancer (-1.17)
- **South Korea** (6.78 years): Cancer (-0.80), Suicide (-0.75)
- **Israel** (3.69 years): Road Traffic (-0.18), Cancer (-0.17), Suicide (-0.11)

Nine of the thirteen factors in the model appear as a leading factor in at least one country.
Only four did not: unintentional injury, COVID-19, childhood mortality, and diabetes — although COVID was a leading factor in some countries during the peak of the pandemic.

### Success story: Road traffic in Europe

Road traffic is a leading factor in only four countries in the European Union (EU), and it is not the top factor in any.
That might not be a coincidence: In the early 2000s, the EU launched a coordinated effort to reduce traffic fatalities.

* A 2001 transport policy set the goal of cutting road deaths in half by 2010.

* The European Road Safety Action Programme (2003–2010) promoted stronger enforcement of speeding and drunk-driving laws, and encouraged seatbelt use, safer road design, and improved vehicle safety standards.

* A follow-on program (2011–2020) added focus on protection for pedestrians and cyclists, and vehicle features like automatic emergency braking and lane-departure warnings.

These policies were not targeted specifically to men, but because traffic death rates are higher for men, the reduction in their rates was larger.
As a result, in every European country the contribution of traffic deaths to the life expectancy gap decreased between 2000 and 2023.
The following figure shows these changes.

```{figure} figs/road_traffic_dumbbell_europe.png
---
name: policy-road-traffic-dumbbell
---
Change in road traffic contribution to the life expectancy gender gap (2000–2023), European OECD countries.
```

The declines are largest in Eastern and Southern Europe, where traffic death rates were highest.
In five countries the life expectancy gap due to traffic decreased by more than a year.
In another eleven countries, it decreased by more than 0.5 years.
And in six countries, the remaining contribution is less than 0.1 years — which suggests that it is possible to eliminate the gender gap in road traffic deaths.

### The largest contributors are amenable to Change

Road traffic in Europe is an example of how public health and safety policies can reduce the life expectancy gap.
It is likely that the other causes of death that contribute to the gap are also amenable to intervention.

**Drug disorders**: The magnitude of the opioid epidemic in the United States and Canada was avoidable.
Other high-income countries avoided harms on the same scale by maintaining stricter controls on opioid prescribing, implementing prescription monitoring systems earlier, limiting pharmaceutical marketing, and expanding harm-reduction measures. 
Deaths due to drug disorders have started to decline in the United States and Canada (although the causes are not yet clear).
If these trends continue, we expect this component of the life expectancy gap to decrease.

**Alcohol**: The Baltic countries and Poland implemented alcohol control policies — including tax increases, availability restrictions, and marketing limits — that reduced alcohol-attributable mortality and contributed to declines in liver disease and suicide.
In general, a decrease in alcohol use directly reduces the contribution of alcohol-related mortality and indirectly reduces the contributions of homicide, suicide, road traffic, liver disease, and cancer. 
In many OECD countries, [alcohol use is falling](https://www.oecd.org/en/publications/2025/11/health-at-a-glance-2025_a894f72e/full-report/alcohol-consumption_f009f222.html), with lower rates of drinking among recent cohorts, compared with previous generations.
If these patterns persist, alcohol's contribution to the life expectancy gap may decrease as well.

**Smoking**: [Smoking rates have declined in most OECD countries](https://www.oecd.org/en/publications/health-at-a-glance-2025_8f9e3f98-en/full-report/smoking-and-vaping_23b355e4.html), driven by higher taxes, smoke-free laws, advertising bans, graphic health warnings on packaging, and restrictions on sales to minors.
Because more men smoke, and they might suffer greater harms due to smoking, the decline of smoking should reduce the contributions of lung disease, cardiovascular disease, and cancer to the life expectancy gap.

**Cancer**: According to [this recent study across 185 countries](https://www.nature.com/articles/s41591-026-04219-7) almost 40% of new cancers are preventable, attributable to factors including smoking and alcohol, obesity and lack of exercise, air pollution, solar radiation, infection, and occupational exposure.
Like smoking and alcohol use, many of these factors are responsive to public health and safety policies.
The paper notes that the proportion of preventable cancers is higher in men, which suggests that interventions that reduce death rates due to cancer would have a larger effect on men and reduce the life expectancy gap.

**Suicide**: In most OECD countries, the contribution of suicide to the life expectancy gap decreased between 2000 and 2023.
The biggest declines were in the Baltic and Central European countries, due to improving economic conditions after the post-Soviet transition, stronger alcohol control policies, and the adoption of national suicide-prevention strategies. 
Similar declines occurred in Finland, Ireland, and Japan following coordinated public health interventions.

At the same time, the contribution of suicide *increased* by 0.11–0.14 years in the United States, Mexico, and Costa Rica, and by 0.34 years in South Korea.
In the United States, rising suicide mortality has been concentrated among middle-aged men in economically declining regions; it is associated with job loss, substance abuse, social isolation, and uneven access to mental-health care.
In South Korea, suicide rates rose sharply after the Asian financial crisis of the late 1990s and have remained high; this pattern has been attributed to economic insecurity, workplace and educational pressures, and population aging, along with limited mental-health services and stigma surrounding treatment.

**Homicide**: In most OECD countries homicide contributes less than 0.05 years to the life expectancy gap, and changes since 2000 are small.
The largest decline was in Colombia, where the contribution fell from 4.17 years to 1.61 years, due to state security policies, the demobilization of paramilitary groups, reduction of armed conflict, and violence-prevention efforts in major cities.
In Estonia, Latvia, and Lithuania the contribution decreased by 0.25–0.52 years as economic conditions stabilized and institutions strengthened after the post-Soviet transition. 
The contribution of homicide increased by 0.3 years in Costa Rica and 0.7 years in Mexico due to increasing violence associated with organized crime and drug trafficking.

These examples show that the leading causes of the life expectancy gap are contingent: they depend on economic and social conditions, and they are amenable to the effect of public health and safety policies.

## Healthy Life Expectancy

So far we've focused on period life expectancy, but we have done the same analysis for healthy life expectancy (HALE), which is [expected years of good health](https://www.healthdata.org/research-analysis/about-gbd).

The following figure shows the gender gap in HALE (female minus male) for OECD countries from 2000 to 2023.

```{figure} figs/hale_gap_timeseries_blog_match.png
:width: 80%

HALE gender gap (2000–2023), OECD countries.
```

In 2023, the average HALE gap was 2.2 years, smaller than the average life expectancy gap, which was 5.1 years.
This difference suggests that some of the additional years that women live are not spent in good health.

The trends in HALE are similar to the trends in life expectancy: decreasing in most countries, except during the COVID pandemic -- and increasing in the United States and Canada, primarily due to the opioid epidemic.

The 2025 Global Gender Gap Report notes these decreasing gaps and concludes:

> While overall life expectancy by gender has remained more stable than healthy life expectancy, and women continue to outlive men, this indicates that the proportion of women’s lives spent in full health has declined relative to men.

This interpretation makes it sound like women's health outcomes are getting worse, but they are not.
The following figure shows HALE over time for OECD countries, with green lines for men and purple for women.
As examples, it highlights the countries with the largest and smallest gaps, Lithuania and Norway.

```{figure} figs/hale_levels_male_female_timeseries.png
:width: 80%

Healthy life expectancy by sex, OECD 2000–2023 (IHME).
```

The HALE gap is narrowing in 34 out of 37 countries -- and in *every one of them* HALE is increasing for both men and women.
Because men generally suffer worse health outcomes, as health outcomes improve, they improve faster for men, closing the gap.


### Contributions to the HALE gap

With the HALE data, we ran a panel model with the same predictors as the life expectancy model.
The following table shows the estimated coefficient for each cause, sorted by magnitude, and the rank of each cause in the two models.

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

The causes of death with the highest coefficients are mostly the same in the HALE model and the life expectancy model.
The biggest difference is that lung disease, which has the fifth largest coefficient in the life expectancy model, moves up to second in the HALE model.
The other differences are small and within expected variability.

We used the model to predict counterfactual HALE for each country, assuming that each death-rate gap could be lowered to the best observed value.
The following table shows the results for the United States in 2023.

```{include} tables/policy_counterfactuals_usa_2023_hale_blog.html
```

The leading contributors in the HALE model are the same as in the life expectancy model.
The top factor is road traffic -- if the death-rate gap could be reduced from 13 to 1.92 per 100,000, the model predicts that the HALE gap would be reduced by 0.86 years.

The following figure shows how these contributions have changed over time.

```{figure} figs/positive_contributions_stacked_area_usa_hale.png
:width: 80%

HALE: stacked gap-closing contributions vs predicted and actual HALE gap, USA.
```

The HALE trends are consistent with the life expectancy trends.
The total has generally increased, driven by a large increase in the contribution of drug disorders and smaller increases in the contributions of suicide and road traffic.

## Intervention changes behavior and consequences

These models show how gender differences in death rates contribute to the life expectancy gap.
Now let's consider why these differences exist.

In the list of cause-specific death rates, we see several that are related to smoking -- lung disease, cardiovascular disease, and cancer -- and several related to drinking -- liver disease, cancer, road traffic, homicide, suicide, accidental injury, and deaths attributed directly to alcohol use.

If men are naturally more inclined to risky behavior, that might contribute to higher rates of smoking, drinking, drug use, and traffic deaths.
And if the behavior difference is biological, the differences in death rates and life expectancy might be, too.

But even if natural risk taking explains part of the life expectancy gap, it is important to know what part.
And even if that part is large, that doesn't mean it is unavoidable.

We have seen examples, including road traffic in Europe, where health and safety policies reduce risky behavior (for example, drunk driving) and reduce the consequences of risky behavior (for example, by improving road safety infrastructure).
Similarly, public campaigns have reduced smoking rates while medical advances have lessened the health impacts of smoking.

So we should not assume that all of the life expectancy gap is explained by risk-taking behavior, or that there is nothing we can do about it.
Public policy, health care, and economic conditions can reduce risky behavior and mitigate the consequences of that behavior.

The evidence across OECD countries suggests that large parts of the life expectancy gender gap are responsive to public policy, economic conditions, and public health interventions.
Countries that reduced deaths from road traffic, smoking, alcohol, violence, and drug disorders also reduced the life expectancy gap.
Rather than treating the current gap as a fixed biological benchmark, policymakers should treat excess male mortality as a measurable and partially preventable public health problem.


## Appendix A — Methods

This appendix summarizes the quantitative methods behind the policy-facing narrative in the body of the report.

### Data

- Life expectancy and the life expectancy gender gap (female minus male years): Our World in Data, combining life-table inputs from the Human Mortality Database (2025) and the United Nations World Population Prospects (2024 revision), with other national sources where OWID harmonizes series. Calendar years 2000–2023; includes 38 OECD countries, with 37 countries in the regression model after excluding Turkey.

- Cause-specific mortality and male–female gaps in death rates: Institute for Health Metrics and Evaluation Global Burden of Disease (GBD) cause-specific death rates by age, sex, country, and year, aggregated to the cause groups used in the model (e.g. road traffic injuries, self-harm, interpersonal violence, neoplasms, chronic respiratory disease, substance use and related categories, cardiovascular disease, diabetes, COVID-19, all-cause under-five mortality).

The outcome series (OWID) and predictor series (IHME) are aligned by country and year in a country–year panel.

### Panel regression model

The core estimator is a Bayesian hierarchical linear model fit to 888 country–year observations (37 countries × 24 years): the life expectancy gender gap is regressed on the vector of standardized male–female gaps in cause-specific death rates.

Predictors are standardized; the outcome gap is centered, which stabilizes sampling and keeps the intercept interpretable.

Cause-specific coefficients are shared across countries, so each coefficient is interpreted as the expected change in the life expectancy gap per one-standard-deviation increase in that cause’s death-rate gap, holding other gaps constant.

Each country has a random intercept that captures persistent over- or under-prediction of the life expectancy gap. Gaps in Estonia, Latvia, and South Korea are larger than the model predicts; the gap in Mexico is smaller. These offsets may reflect omitted predictors, interactions, or measurement errors.

The hierarchical model achieves mean absolute error on the order of 0.2 years on the life expectancy gap in the reported specification—substantially smaller than one year for most country-years.

For most countries, residuals are centered near zero; some countries exhibit larger dispersion, consistent with small-population noise or drivers omitted from the cause-gap list.

Counterfactual scenarios take each cause’s male–female death-rate gap to the minimum gap observed in the OECD panel over 2000–2023. Scenarios are partial: they move one margin at a time, so summing across causes is not a joint intervention forecast.

Maternal disorders and conflict/terrorism were examined; coefficients were small, credible intervals crossed zero, and fit gains were negligible, so they were dropped.

Turkey is excluded from the regression sample because it behaves as a multivariate outlier relative to other OECD members when included; descriptive tables include all 38 OECD members.

### Competing risks

In both models (period life expectancy and HALE) the estimated coefficients for cardiovascular disease and diabetes are negative, which means that if a country has a larger death rate gap, the model predicts a *smaller* life expectancy gap.
This is counterintuitive — for example, if more men die of cardiovascular disease, their age-specific death rates should increase and their life expectancy should decrease.

A possible explanation is competing risks — where death rates from other causes are low, cardiovascular disease and diabetes become more common causes of death, because they are diseases of aging.
If you live long enough to die of cardiovascular disease, it means you avoided the causes of death that affect younger people.

In the regression model, these variables might act as a proxy for overall health outcomes.
If a large (positive) death rate gap indicates good outcomes, and good outcomes are associated with smaller life expectancy gaps, that would explain the negative coefficients.

If that explanation is correct, the counterfactual assumption might not hold — that is, if an intervention is able to reduce these gaps, it's not clear what effect that would have on life expectancy.




