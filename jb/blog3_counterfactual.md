# How Much of the Life Expectancy Gap Could We Close?

*This is Part 3 in a series on gender gaps in life expectancy, what causes them, and what we can do about it.*

---

In the [previous article](https://allendowney.substack.com/p/what-drives-the-life-expectancy-gender), we built a model to estimate how gender gaps in cause-specific death rates affect the life expectancy gap.
We identified the factors with the largest coefficients and the highest importance — cancer, cardiovascular disease, homicide, and others.

But the most important factor overall might not be the most important factor for a particular country.
Drug disorders have low importance globally because the gap is small in most OECD countries — but in the United States and Canada, drug disorders have a much larger effect on the life expectancy gap.
So now we'll ask a different question: *for a given country*, which causes of death offer the largest opportunity to close the gap?

## The Counterfactual

We won't assume that every gap can be closed entirely.
Instead, we'll look at the smallest gaps in the dataset as an indication of what's possible.

The following table shows the minimum gap observed across all 37 countries and 24 years, and the country and year where the minimum occurred.

```{include} tables/gap_extremes_min_blog_le.html
```

Some gaps might be easier to close than others.
For example, in Ireland in 2021, the gap in childhood mortality rates was only 0.59 per 100,000, substantially smaller than the OECD average, about 22 per 100,000.
And the small gap seems to be due to a low rate for boys, rather than a high rate for girls.
This observation suggests that the gap in child mortality can be close to zero.

The rate gap for several causes is negative, which means that in some countries and some times, the usual pattern is reversed and death rates are higher for women.
For these causes, we assume that if the gaps can be negative or positive, they could also be zero.

Some gaps might be harder to close.
The smallest rate gap for suicide is about 4 per 100,000, reported in Greece in 2002.
The OECD average is about 14.
This observation suggests that this gap is harder to close entirely, so for purposes of modeling we assume that the smallest observed gap is the smallest attainable gap. 

Now we'll consider the effect, for a given country, if we can reduce each rate gap to the smallest observed value if it's positive, or zero if it's negative.

## The United States

In 2023, the life expectancy gap in the United States was 5 years, close to the OECD average.
The following table shows how much this gap would change if we reduced each cause-specific gap to its best attainable level.

```{include} tables/counterfactuals_usa_2023_le_blog.html
```

The following figure shows the same results graphically.
Error bars show 94% credible intervals.

```{figure} figs/counterfactual_effects_usa_2023_le_bayesian.png
:width: 80%

Counterfactual effects: hypothetical change in life expectancy gap for each cause-specific death rate, USA (2023), 94% credible intervals.
```

Road traffic has the largest potential impact — reducing the gap to Iceland's 2017 level would close about 0.81 years of the life expectancy gap.

Drug disorders are second — reducing the gap to Japan's 2013 level (essentially zero) would close about 0.77 years.

And if the rate gap due to suicide could be reduced from 18 to 4 per 100,000, the model predicts the life expectancy gap would close by 0.52 years.

For homicide, liver disease, cancer, and alcohol, the potential impact is smaller but still meaningful.
The potential impact of childhood mortality and injury are smaller still, and for COVID-19 in 2023 it is near zero.

For lung disease, the gender gap is negative, meaning that the death rate is higher for women.
So if we close this gap to zero, the life expectancy gap might grow by 0.18 years.

And for cardiovascular disease and diabetes, the estimated coefficient is negative, which means that if we reduce the rate gap, the model predicts that the life expectancy gap would grow.
However, as we discussed in [the previous article](https://allendowney.substack.com/p/what-drives-the-life-expectancy-gender), these negative coefficients might be explained by competing risks -- that is, if general health outcomes are better, more people live long enough to die from diseases of aging, so their rates tend to be higher.
If that's true, the counterfactual assumption might not hold -- that is, if an intervention is able to reduce these gaps, it's not clear what effect that would have on life expectancy.

But for the other causes of death, the counterfactual assumption is plausible.
For example, if the rate gap due to drug disorders closes -- which is likely as overall rates have already started to fall -- it is reasonable to expect the life expectancy gap to close.

The total of the gap-closing effects is about 3.1 years, which suggests that together they could reduce the life expectancy gap from 5 to 2.9 years.
But in reality these effects are likely to interact.
For example, a decrease in consumption of alcohol would directly affect death rates due to alcohol -- and it will indirectly affect rates due to liver disease, cancer, road traffic, accidents, suicide, homicide, and possibly drug disorders.
With these kinds of interactions, the total effect of multiple interventions might be larger or smaller than the sum of the estimates from the model.

Nevertheless, the sizes of these effects suggests which kinds of interventions might have the largest effect on the life expectancy gap.

The following figure shows how the positive contributions to the gap have changed over time.

```{figure} figs/positive_contributions_stacked_area_usa_le.png
:width: 80%

Stacked positive contributions to the life expectancy gap, USA (2000–2023).
```

The total contribution has generally increased, driven by a large increase in the contribution of drug disorders and smaller increases in the contributions of suicide and road traffic.

## Different Factors Lead in Different Countries

For each country, we identified leading factors, which include the factor that makes the largest contribution to the life expectancy gap, and any additional factors with a contribution at least half as big.

Starting in North America, the following list shows the current gender gap in each country, the leading factors, and how much of the gap could be closed if each factor was lowered to the smallest observed value.

- **United States** (5.37 years): Road Traffic (-0.81), Drug Disorders (-0.77), Suicide (-0.52)
- **Canada** (4.61 years): Drug Disorders (-0.51), Cancer (-0.36), Suicide (-0.34)

In every Latin American country, road traffic is a leading factor; in Mexico and Colombia, homicide is the top factor.

- **Colombia** (6.03 years): Homicide (-1.61), Road Traffic (-1.48)
- **Costa Rica** (6.01 years): Road Traffic (-1.77)
- **Mexico** (4.93 years): Homicide (-1.32), Road Traffic (-1.06), Liver Disease (-0.75)
- **Chile** (4.60 years): Road Traffic (-0.88), Liver Disease (-0.45)

In every Northern European country, suicide is a leading factor, and in most cancer is as well.

- **Finland** (5.76 years): Lung Disease (-0.56), Liver Disease (-0.47), Suicide (-0.39)
- **Denmark** (3.93 years): Cancer (-0.47), Suicide (-0.26), Alcohol (-0.25), Liver Disease (-0.24)
- **Norway** (3.61 years): Cancer (-0.33), Suicide (-0.23)
- **Sweden** (3.45 years): Suicide (-0.28), Drug Disorders (-0.15), Cancer (-0.14)
- **Iceland** (3.25 years): Suicide (-0.37), Cancer (-0.21)

Compared to Northern Europe, the life expectancy gaps are bigger in Baltic Countries, but the leading factors are similar, including cancer and suicide.

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

Nine of the thirteen factors in the model appear as a leading factor in at least one country: cancer, cardiovascular disease, homicide, suicide, road traffic, liver disease, lung disease, alcohol, and drug disorders.
Only four did not: unintentional injury, COVID-19, childhood mortality, and diabetes -- although COVID was a leading factor in some countries during the peak of the pandemic.

## Success Story: Road Traffic in Europe

Road traffic is a leading factor in only four countries in the European Union (EU), and it is not the top factor in any.
That might not be a coincidence: In the early 2000s, the EU launched a coordinated effort to reduce traffic fatalities.
A 2001 transport policy set the goal of cutting road deaths in half by 2010, and the European Road Safety Action Programme (2003–2010) promoted stronger enforcement of speeding and drunk-driving laws, expanded seatbelt use, safer road design, and improved vehicle safety standards.
A follow-on program (2011–2020), added focus on safer infrastructure, protection for pedestrians and cyclists, and vehicle features like automatic emergency braking and lane-departure warnings.

These policies were not targeted specifically to men, but because traffic death rates are higher for men, the reduction in their rates was larger.
As a result, in every European country the contribution of traffic deaths to the life expectancy gap declined between 2000 and 2023.
The following figure shows these changes.

```{figure} figs/road_traffic_dumbbell_europe.png
---
name: road-traffic-dumbbell
---
Change in road traffic contribution to the life expectancy gender gap (2000–2023), European OECD countries.
```

The changes are largest in Eastern and Southern Europe, where traffic death rates were highest.
In five countries the life expectancy gap due to traffic decreased by more than a year.
In another eleven countries, it decreased by more than 0.5 years.
And in six countries, the remaining contribution is less than 0.1 years -- which shows that it is possible to eliminate the gender gap in road traffic deaths.

## Amenable to Change

Road traffic in Europe is an example of how public health and safety policies can reduce the life expectancy gap.
It it likely that the other causes of death that contribute to the life expectancy gap are similarly amenable to intervention.

**Drug disorders**: The opioid epidemic in the United States and Canada was avoidable.
Other high-income countries avoided epidemics on the same scale by maintaining stricter controls on opioid prescribing, implementing prescription monitoring systems earlier, limiting pharmaceutical marketing, and expanding harm-reduction measures. 
Deaths due to drug disorders have started to decline in the United States and Canada, although the causes are not yet clear.
If these trends continue, we expect this component of the life expectancy gap to decrease.

**Alcohol**: The Baltic countries and Poland implemented alcohol control policies—including tax increases, availability restrictions, and marketing limits—that reduced alcohol-attributable mortality and contributed to declines in liver disease and suicide.
In general, a decrease in rates of alcohol abuse directly reduces the contribution of alcohol-related mortality and indirectly decreases the contributions of homicide, suicide, road traffic, liver disease, and cancer. 
In many OECD countries, [alcohol use has been falling](https://www.oecd.org/en/publications/2025/11/health-at-a-glance-2025_a894f72e/full-report/alcohol-consumption_f009f222.html), with lower rates of drinking among recent cohorts, compared with previous generations.
If these patterns persist, alcohol-related mortality may decrease as well.

**Smoking**: [Smoking rates have declined in most OECD countries](https://www.oecd.org/en/publications/health-at-a-glance-2025_8f9e3f98-en/full-report/smoking-and-vaping_23b355e4.html#indicator-d1e20246-98cbd291e0), driven by tobacco control policies: higher taxes, smoke-free laws, advertising bans, graphic health warnings on packaging, and restrictions on sales to minors.
Because smoking contributes to lung disease, cardiovascular disease, and several cancers, these declines are expected to reduce smoking-related mortality over time.
Because more men smoke, falling rates have already contributed to reductions in the life expectancy gap in many countries.

**Cancer**: According to [this recent study across 200 countries](https://www.nature.com/articles/s41591-026-04219-7) almost 40% of new cancers are preventable, attributable to factors including smoking and alcohol, obesity and lack of exercise, air pollution, sun exposure, infection, and occupational exposure.
Like smoking and alcohol abuse, many of these factors are amenable to public health and safety policies.
The paper notes that the proportion of preventable cancers is higher in men, which suggests that interventions that reduce death rates due to cancer would likely have a larger effect on men and reduce the life expectancy gap.

**Suicide**: In most OECD countries, the contribution of suicide to the life expectancy gap decreased between 2000 and 2023.
The biggest declines were in the Baltic and Central European countries, due to improving economic conditions after the post-Soviet transition, stronger alcohol control policies, and the adoption of national suicide-prevention strategies. 
Similar declines occurred in Finland, Ireland, and Japan following coordinated public health interventions.

The contribution of suicide increased by 0.11–0.14 years in the United States, Mexico, and Costa Rica, and by 0.34 years in South Korea.
In the United States, rising suicide mortality has been concentrated among middle-aged men in economically declining regions; it is associated with job loss, substance abuse, social isolation, and uneven access to mental-health care.
In South Korea, suicide rates rose sharply after the Asian financial crisis of the late 1990s and have remained high; it has been attributed to economic insecurity, workplace and educational pressures, and population aging, along with limited mental-health services and stigma surrounding treatment.

**Homicide**: In most OECD countries homicide contributes less than 0.05 years to the life expectancy gap, and changes since 2000 are small.
The largest decline was in Colombia, where the contribution fell from 4.17 years to 1.61 years, due to state security policies, the demobilization of paramilitary groups, reduction of armed conflict culminating in the 2016 peace agreement with the FARC, along with violence-prevention efforts in major cities.
In Estonia, Latvia, and Lithuania the contribution decreased by 0.25--0.52 years as economic conditions stabilized and institutions strengthened after the post-Soviet transition. 
The contribution of homicide increased by 0.3 years in Costa Rica and 0.7 years in Mexico due to increasing violence associated with organized crime and drug-trafficking.

These example show that causes of the life expectancy gap are contingent: they depend on economic and social conditions, and they are amenable to the effect of public health and safety policies.

## Technical Note: Country-specific intercepts

NOTE: a possible explanation for the intercepts is unmodeled interactions

The model assigns each country a baseline — an intercept that captures the gap we would expect when all predictors are at their mean.
Countries with higher intercepts have larger gaps than the model would predict from their death rate gaps alone; countries with lower intercepts have smaller gaps.

The following figure shows these country intercepts, sorted from highest to lowest.
Error bars show 94% credible intervals.
The vertical line at zero is the grand mean; countries in blue are above average, countries in red are below.

```{figure} figs/country_intercepts_le_intercepts.png
:width: 80%

Country intercepts (random effects): deviation from grand mean, 94% credible intervals.
```

In 2023, the Baltic countries — Lithuania, Latvia, and Estonia — had the largest gaps in the OECD, all greater than 8 years.
A ferry from Tallinn to Stockholm travels 240 miles and closes the gender gap from 8.1 years in Estonia to 3.7 years in Sweden.
Suicide and road traffic have been major drivers of these large gaps; Lithuania's road traffic gap improved sharply after EU accession in 2004.
Counterfactual analysis for these countries would quantify the remaining potential — which causes are "low-hanging fruit" and which have already improved.

At the other end, the Netherlands, Norway, Luxembourg, and New Zealand had gaps under 3.5 years in 2023.
Near-zero gaps are achievable.
For these countries, the question is what — if anything — could close the remaining gap, or what drove them to achieve small gaps in the first place.




---

*Next: [Healthy life expectancy: quality, not just quantity]*
