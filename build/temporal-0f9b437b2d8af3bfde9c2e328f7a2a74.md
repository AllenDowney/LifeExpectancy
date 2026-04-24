# Temporal Analysis: Evolution of Health Patterns Over Time

## Purpose

This document examines how the relationships between health indicators and gender gaps in Life Expectancy (LE) and Healthy Life Expectancy (HALE) have evolved over time. By analyzing data from different time periods (2000, 2005, 2010, 2015, 2019), we can identify temporal trends in:
- Which health indicators are most important for explaining gender gaps
- How the potential for closing gender gaps through interventions has changed
- Whether the underlying health patterns have shifted over the past two decades

This temporal analysis serves to:
- Understand how health patterns and their relationships to gender gaps have changed over time
- Identify which indicators have become more or less important over the past two decades
- Assess how intervention opportunities have evolved
- Document temporal trends in health indicator importance and counterfactual effects

## Temporal Analysis Framework

For each time period, we examine the following to understand how health patterns have evolved:

**Indicator Importance Over Time:**
- How the relative importance of different health indicators has changed
- Which indicators have gained or lost importance over the past two decades
- Whether the structure of relationships (Mid vs Gap components) has shifted

**Counterfactual Analysis Over Time:**
- How the potential for closing gender gaps through interventions has changed
- Which interventions show increasing or decreasing potential over time
- Whether overall opportunities for gap reduction have increased or decreased

**Key Questions for Temporal Analysis:**
1. How have the most important health indicators changed over time?
2. What do changes in indicator importance tell us about evolving health patterns?
3. How have intervention opportunities (counterfactual effects) evolved?
4. Are there clear temporal trends suggesting improvements or deteriorations in specific areas?
5. What do these changes indicate about the evolution of gender health gaps?

## Temporal Evolution: 2000 to 2019

This section presents results chronologically from 2000 to 2019, allowing us to observe how health patterns and their relationships to gender gaps have evolved over the past two decades. Each analysis uses the most recent year of data available for each country up to the specified cutoff year, excluding 2020+ data to avoid COVID-19 pandemic distortions.

---

## 2000: Early 2000s Health Patterns

**Time Period**: 2000  
**Context**: This represents health patterns at the turn of the millennium, providing a baseline for understanding how health indicators and their relationships to gender gaps have evolved over the subsequent two decades.

### Life Expectancy Gap Model (2000)

**Model Performance:**
- **Cross-validation R²**: 0.743 (Elastic Net, best model)
- **In-sample R²**: 0.896 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.575 years (cross-validation), 0.449 years (in-sample)
- **Non-zero coefficients**: 19 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Cardiovascular**: 17.6 (Mid: 17.6, Gap: 0.0143)
2. **Neoplasms**: 8.02 (Mid: 0, Gap: 8.02)
3. **UnintentionalInjury**: 7.01 (Mid: 2.49, Gap: 4.52)
4. **Homicide**: 5.31 (Mid: 2.17, Gap: 3.14)
5. **ChronicRespiratory**: 4.44 (Mid: 2.05, Gap: 2.4)
6. **Suicide**: 3.87 (Mid: 1.51, Gap: 2.36)
7. **RoadTraffic**: 1.8 (Mid: 0.699, Gap: 1.1)
8. **Alcohol**: 1.24 (Mid: 0.529, Gap: 0.708)
9. **LiverDisease**: 1.08 (Mid: 0.436, Gap: 0.64)
10. **Diabetes**: 0.544 (Mid: 0.544, Gap: 0)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Cardiovascular (-0.00947), Neoplasms (-0.115), UnintentionalInjury (-0.103), Homicide (-0.085), ChronicRespiratory (-0.0111), Suicide (-0.263), RoadTraffic (-0.305), Alcohol (-0.0825), LiverDisease (-0.0454)
- **Gap-widening indicators**: Diabetes (+0.013), DrugDisorder (+0.148)
- **Largest single counterfactual effect**: RoadTraffic: -0.305 years (reducing gap from 12.3 to 5.01, targeting Iceland)
- **Aggregate gap-closing total**: -1.019 years
- **Aggregate gap-widening total**: +0.161 years
- **Net reduction in predicted gap**: -0.858 years

**Key Findings:**
- Cardiovascular disease was the dominant factor explaining LE gender gaps in 2000
- Neoplasms (cancer) was the second most important, driven entirely by gender differences
- Road traffic injuries had the largest potential for intervention (-0.305 years)
- Suicide ranked 6th in importance and had the 2nd largest counterfactual effect (-0.263 years)
- Most indicators contribute through both Mid and Gap components
- DrugDisorder was not selected by Elastic Net (importance = 0.167)

**Interpretation of 2000 Patterns:**
- Cardiovascular disease was the dominant factor, reflecting its importance through average rates (Mid component) rather than gender differences
- Neoplasms (cancer) was the second most important indicator, driven entirely by gender differences in cancer rates
- Road traffic injuries had the largest potential for intervention, suggesting this was a major area where gender gaps could be addressed
- Suicide prevention showed substantial potential, ranking as the 2nd largest counterfactual effect
- Overall, the potential for closing gender gaps was more limited in 2000 (-0.858 years) compared to later periods

### HALE Gap Model (2000)

**Model Performance:**
- **Cross-validation R²**: 0.715 (Elastic Net, best model)
- **In-sample R²**: 0.946 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.441 years (cross-validation), 0.309 years (in-sample)
- **Non-zero coefficients**: 21 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Cardiovascular**: 13.9 (Mid: 13.9, Gap: 0)
2. **Neoplasms**: 13.8 (Mid: 2.52, Gap: 11.2)
3. **UnintentionalInjury**: 5.71 (Mid: 1.18, Gap: 4.53)
4. **ChronicRespiratory**: 5.01 (Mid: 4.1, Gap: 0.911)
5. **Suicide**: 3.05 (Mid: 1.26, Gap: 1.79)
6. **LiverDisease**: 1.95 (Mid: 0.733, Gap: 1.21)
7. **Homicide**: 1.84 (Mid: 0.637, Gap: 1.2)
8. **Alcohol**: 1.51 (Mid: 0.218, Gap: 1.3)
9. **Diabetes**: 0.985 (Mid: 0.618, Gap: 0.366)
10. **RoadTraffic**: 0.905 (Mid: 0.503, Gap: 0.402)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Cardiovascular (-0.0018), Neoplasms (-0.195), UnintentionalInjury (-0.121), Suicide (-0.502), LiverDisease (-0.195), Homicide (-0.164), Alcohol (-0.209), RoadTraffic (-0.308), DrugDisorder (-0.0698)
- **Gap-widening indicators**: ChronicRespiratory (+0.0848), Diabetes (+0.161)
- **Largest single counterfactual effect**: Suicide: -0.502 years (reducing gap from 16.0 to 3.27, targeting Türkiye)
- **Aggregate gap-closing total**: -1.774 years
- **Aggregate gap-widening total**: +0.246 years
- **Net reduction in predicted gap**: -1.528 years

**Key Findings:**
- Cardiovascular is the most important indicator (13.9), with importance entirely from the Mid component
- Neoplasms ranks 2nd (13.8), with substantial contributions from both Mid (2.52) and Gap (11.2) components
- Suicide has the largest single counterfactual effect (-0.502 years), despite ranking 5th in importance
- Most indicators contribute through both Mid and Gap components

**Interpretation of 2000 Patterns:**
- Cardiovascular disease was the dominant factor in explaining HALE gender gaps in 2000
- Neoplasms (cancer) was the second most important indicator, with substantial contributions from both average rates and gender differences
- Suicide prevention showed the largest potential for intervention (-0.502 years), despite ranking 5th in importance
- Overall, the potential for closing gender gaps was substantial in 2000 (-1.528 years)

---

## 2005: Mid-2000s Health Patterns

**Time Period**: 2005  
**Context**: Five years after 2000, we observe how health patterns and their relationships to gender gaps have evolved.

### Life Expectancy Gap Model (2005)

**Model Performance:**
- **Cross-validation R²**: 0.789 (Elastic Net, best model)
- **In-sample R²**: 0.924 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.514 years (cross-validation), 0.398 years (in-sample)
- **Non-zero coefficients**: 13 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Cardiovascular**: 22.2 (Mid: 22.2, Gap: 0)
2. **Neoplasms**: 12.8 (Mid: 0, Gap: 12.8)
3. **UnintentionalInjury**: 11.1 (Mid: 0, Gap: 11.1)
4. **ChronicRespiratory**: 4.75 (Mid: 2.37, Gap: 2.37)
5. **Suicide**: 3.26 (Mid: 1.93, Gap: 1.34)
6. **Homicide**: 2.67 (Mid: 2.48, Gap: 0.189)
7. **LiverDisease**: 2.24 (Mid: 0, Gap: 2.24)
8. **Alcohol**: 1.38 (Mid: 0, Gap: 1.38)
9. **RoadTraffic**: 0.751 (Mid: 0.751, Gap: 0)
10. **Diabetes**: 0.636 (Mid: 0.636, Gap: 0)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Cardiovascular (-0.00939), Neoplasms (-0.136), UnintentionalInjury (-0.112), Suicide (-0.232), Alcohol (-0.113), Homicide (-0.1), RoadTraffic (-0.376), LiverDisease (-0.0766)
- **Gap-widening indicators**: ChronicRespiratory (+0.112), Diabetes (+0.00512), DrugDisorder (+0.0556)
- **Largest single counterfactual effect**: RoadTraffic: -0.376 years (reducing gap from 13.0 to 3.67, targeting Iceland)
- **Aggregate gap-closing total**: -1.155 years
- **Aggregate gap-widening total**: +0.173 years
- **Net reduction in predicted gap**: -0.982 years

**Key Findings:**
- Cardiovascular is the most important indicator (22.2), with importance entirely from the Mid component
- Neoplasms ranks 2nd (12.8), with importance entirely from the Gap component
- RoadTraffic has the largest single counterfactual effect (-0.376 years), despite ranking 9th in importance
- Suicide ranks 5th in importance and has the 2nd largest counterfactual effect (-0.232 years)
- Most indicators contribute through gap components, though Cardiovascular and some others contribute through Mid
- DrugDisorder was not selected by Elastic Net (importance = 0)

**Changes from 2000:**
- **Cardiovascular importance increased** (17.6 → 22.2, +26.1%), maintaining its top position
- **Neoplasms importance increased** (8.02 → 12.8, +59.6%), suggesting cancer became a stronger predictor
- **UnintentionalInjury importance increased** (7.01 → 11.1, +58.3%)
- **Homicide importance decreased** (5.31 → 2.67, -49.7%), continuing the decline from 2000
- **RoadTraffic counterfactual effect increased** (-0.305 → -0.376 years, +23.3%), becoming the largest effect
- **Suicide counterfactual effect decreased** (-0.263 → -0.232 years, -11.8%)
- **Net gap reduction increased** (-0.858 → -0.982 years), suggesting more potential for intervention

**Interpretation of 2005 Patterns:**
- Cardiovascular disease remained the dominant factor, with importance continuing to increase
- Neoplasms and UnintentionalInjury gained importance, suggesting these became stronger predictors
- Road traffic injuries became the top intervention priority for LE gaps
- Homicide continued to decline in importance, suggesting improvements in this area

### HALE Gap Model (2005)

**Model Performance:**
- **Cross-validation R²**: 0.701 (Elastic Net, best model)
- **In-sample R²**: 0.939 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.574 years (cross-validation), 0.385 years (in-sample)
- **Non-zero coefficients**: 19 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Cardiovascular**: 30.0 (Mid: 30.0, Gap: 0)
2. **Neoplasms**: 13.7 (Mid: 2.92, Gap: 10.8)
3. **UnintentionalInjury**: 8.96 (Mid: 2.26, Gap: 6.7)
4. **ChronicRespiratory**: 5.69 (Mid: 2.29, Gap: 3.41)
5. **Suicide**: 2.69 (Mid: 0.9, Gap: 1.79)
6. **Alcohol**: 2.0 (Mid: 0.823, Gap: 1.18)
7. **Homicide**: 1.99 (Mid: 0.913, Gap: 1.08)
8. **RoadTraffic**: 1.64 (Mid: 0.8, Gap: 0.844)
9. **LiverDisease**: 1.48 (Mid: 0.752, Gap: 0.725)
10. **Diabetes**: 0.781 (Mid: 0.781, Gap: 0)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Cardiovascular (-0.00697), Neoplasms (-0.169), UnintentionalInjury (-0.138), Suicide (-0.271), Homicide (-0.153), LiverDisease (-0.157), Alcohol (-0.0873), RoadTraffic (-0.153)
- **Gap-widening indicators**: ChronicRespiratory (+0.0835), Diabetes (+0.00418)
- **Largest single counterfactual effect**: Suicide: -0.271 years (reducing gap from 14.0 to 2.42, targeting Türkiye)
- **Aggregate gap-closing total**: -1.135 years
- **Aggregate gap-widening total**: +0.088 years
- **Net reduction in predicted gap**: -1.047 years

**Key Findings:**
- Cardiovascular is by far the most important indicator (30.0), with importance entirely from the Mid component
- Neoplasms ranks 2nd (13.7), with substantial contributions from both Mid (2.92) and Gap (10.8) components
- Suicide has the largest single counterfactual effect (-0.271 years), despite ranking 5th in importance
- Most indicators contribute through both Mid and Gap components
- DrugDisorder was not selected by Elastic Net (importance = 0)

**Changes from 2000:**
- **Cardiovascular importance more than doubled** (13.9 → 30.0, +115.8%), becoming even more dominant
- **Neoplasms importance decreased slightly** (13.8 → 13.7, -0.7%), remaining the second most important indicator
- **UnintentionalInjury importance increased** (5.71 → 8.96, +56.9%)
- **Homicide importance increased slightly** (1.84 → 1.99, +8.2%)
- **RoadTraffic importance increased** (0.905 → 1.64, +81.2%)
- **Suicide counterfactual effect decreased** (-0.502 → -0.271 years, -46.0%), but became the largest effect
- **Net gap reduction decreased** (-1.528 → -1.047 years), suggesting less potential for intervention

**Interpretation of 2005 Patterns:**
- Cardiovascular disease became even more dominant, reaching its peak importance (30.0) in explaining HALE gaps
- Neoplasms gained importance, suggesting cancer became a stronger factor in gender gaps
- Suicide prevention became the top intervention priority, replacing road traffic injuries
- Homicide became less important, suggesting improvements in this area or changes in its relationship to gender gaps

---

## 2010: Early 2010s Health Patterns

**Time Period**: 2010  
**Context**: A decade after 2000, we observe continued evolution of health patterns and their relationships to gender gaps.

### Life Expectancy Gap Model (2010)

**Model Performance:**
- **Cross-validation R²**: 0.903 (Elastic Net, best model)
- **In-sample R²**: 0.967 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.367 years (cross-validation), 0.269 years (in-sample)
- **Non-zero coefficients**: 17 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Neoplasms**: 17.0 (Mid: 1.12, Gap: 15.9)
2. **UnintentionalInjury**: 8.68 (Mid: 0, Gap: 8.68)
3. **ChronicRespiratory**: 6.0 (Mid: 3.74, Gap: 2.25)
4. **LiverDisease**: 2.34 (Mid: 0.475, Gap: 1.86)
5. **Alcohol**: 2.05 (Mid: 0.354, Gap: 1.7)
6. **Suicide**: 1.82 (Mid: 0.801, Gap: 1.02)
7. **Homicide**: 1.77 (Mid: 0.821, Gap: 0.948)
8. **Diabetes**: 1.26 (Mid: 0.779, Gap: 0.485)
9. **RoadTraffic**: 0.681 (Mid: 0.678, Gap: 0.0027)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Neoplasms (-0.246), UnintentionalInjury (-0.162), LiverDisease (-0.18), Alcohol (-0.198), Suicide (-0.201), Homicide (-0.0817), RoadTraffic (-0.188)
- **Gap-widening indicators**: ChronicRespiratory (+0.121), Diabetes (+0.0579)
- **Largest single counterfactual effect**: Neoplasms: -0.246 years (reducing gap from 23.2 to 0.94, targeting Mexico)
- **Aggregate gap-closing total**: -1.257 years
- **Aggregate gap-widening total**: +0.179 years
- **Net reduction in predicted gap**: -1.078 years

**Key Findings:**
- Neoplasms is the most important indicator (17.0), with substantial contributions from both Mid (1.12) and Gap (15.9) components
- UnintentionalInjury ranks 2nd (8.68), with importance entirely from the gap component
- Neoplasms has the largest single counterfactual effect (-0.246 years)
- Most indicators contribute through gap components, though some (ChronicRespiratory, Suicide, Homicide) have notable Mid contributions
- Cardiovascular and DrugDisorder were not selected by Elastic Net (importance = 0)

**Changes from 2005:**
- **Cardiovascular was no longer selected** (22.2 → 0), a major shift suggesting its relationship to LE gaps changed
- **Neoplasms importance increased** (12.8 → 17.0, +32.8%), becoming the top indicator
- **UnintentionalInjury importance decreased** (11.1 → 8.68, -21.8%)
- **ChronicRespiratory importance increased** (4.75 → 6.0, +26.3%)
- **Neoplasms counterfactual effect increased** (-0.136 → -0.246 years, +80.9%), becoming the largest effect
- **RoadTraffic counterfactual effect decreased** (-0.376 → -0.188 years, -50.0%)
- **Net gap reduction increased** (-0.982 → -1.078 years)

**Interpretation of 2010 Patterns:**
- A major shift occurred: Cardiovascular was no longer a significant predictor of LE gender gaps
- Neoplasms (cancer) became the dominant factor, suggesting cancer became a stronger driver of gender gaps
- Cancer prevention became the top intervention priority for LE gaps
- Overall potential for closing gaps increased

### HALE Gap Model (2010)

**Model Performance:**
- **Cross-validation R²**: 0.712 (Elastic Net, best model)
- **In-sample R²**: 0.94 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.472 years (cross-validation), 0.369 years (in-sample)
- **Non-zero coefficients**: 17 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Cardiovascular**: 24.0 (Mid: 24.0, Gap: 0)
2. **Neoplasms**: 11.3 (Mid: 0, Gap: 11.3)
3. **ChronicRespiratory**: 5.36 (Mid: 3.94, Gap: 1.42)
4. **UnintentionalInjury**: 5.32 (Mid: 0, Gap: 5.32)
5. **Suicide**: 3.18 (Mid: 1.34, Gap: 1.85)
6. **Homicide**: 2.69 (Mid: 1.12, Gap: 1.56)
7. **LiverDisease**: 2.3 (Mid: 0.824, Gap: 1.47)
8. **Alcohol**: 1.48 (Mid: 0.279, Gap: 1.2)
9. **RoadTraffic**: 1.05 (Mid: 0.71, Gap: 0.337)
10. **Diabetes**: 0.789 (Mid: 0.777, Gap: 0.0116)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Cardiovascular (-0.00179), Neoplasms (-0.177), UnintentionalInjury (-0.0995), Suicide (-0.352), Homicide (-0.122), LiverDisease (-0.161), Alcohol (-0.142), RoadTraffic (-0.311)
- **Gap-widening indicators**: ChronicRespiratory (+0.0907), Diabetes (+0.00713)
- **Largest single counterfactual effect**: Suicide: -0.352 years (reducing gap from 15.1 to 2.23, targeting Türkiye)
- **Aggregate gap-closing total**: -1.366 years
- **Aggregate gap-widening total**: +0.098 years
- **Net reduction in predicted gap**: -1.268 years

**Key Findings:**
- Cardiovascular is by far the most important indicator (24.0), with importance entirely from the Mid component
- Neoplasms ranks 2nd (11.3), with importance entirely from the Gap component
- Suicide has the largest single counterfactual effect (-0.352 years), despite ranking 5th in importance
- RoadTraffic ranks 9th in importance and has the 2nd largest counterfactual effect (-0.311 years)
- Most indicators contribute through both Mid and Gap components
- DrugDisorder was not selected by Elastic Net (importance = 0)

**Changes from 2005:**
- **Cardiovascular importance decreased** (30.0 → 24.0, -20.0%), but remained the top indicator
- **Neoplasms importance decreased** (13.7 → 11.3, -17.5%)
- **UnintentionalInjury importance decreased** (8.96 → 5.32, -40.6%)
- **ChronicRespiratory importance decreased** (5.69 → 5.36, -5.8%)
- **Suicide counterfactual effect increased** (-0.271 → -0.352 years, +29.9%), becoming the largest effect again
- **RoadTraffic counterfactual effect increased** (-0.153 → -0.311 years, +103.3%), becoming the 2nd largest effect
- **Net gap reduction increased** (-1.047 → -1.268 years), suggesting more potential for intervention

**Interpretation of 2010 Patterns:**
- Cardiovascular remained dominant but began to decline from its 2005 peak
- Suicide prevention regained prominence as the top intervention priority
- Road traffic injuries became increasingly important for intervention
- Overall potential for closing gaps increased compared to 2005

---

## 2015: Mid-2010s Health Patterns

**Time Period**: 2015  
**Context**: Approaching the end of the analysis period, we observe continued evolution toward more recent patterns.

### Life Expectancy Gap Model (2015)

**Model Performance:**
- **Cross-validation R²**: 0.901 (Elastic Net, best model)
- **In-sample R²**: 0.97 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.326 years (cross-validation), 0.238 years (in-sample)
- **Non-zero coefficients**: 15 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Neoplasms**: 10.6 (Mid: 0, Gap: 10.6)
2. **UnintentionalInjury**: 7.23 (Mid: 0, Gap: 7.23)
3. **ChronicRespiratory**: 4.31 (Mid: 2.59, Gap: 1.72)
4. **Suicide**: 2.3 (Mid: 0.426, Gap: 1.87)
5. **Alcohol**: 1.52 (Mid: 0.0209, Gap: 1.5)
6. **LiverDisease**: 1.4 (Mid: 0.14, Gap: 1.26)
7. **RoadTraffic**: 0.882 (Mid: 0.391, Gap: 0.491)
8. **Diabetes**: 0.55 (Mid: 0, Gap: 0.55)
9. **Homicide**: 0.522 (Mid: 0.0802, Gap: 0.442)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Neoplasms (-0.178), UnintentionalInjury (-0.247), Suicide (-0.393), Alcohol (-0.212), LiverDisease (-0.165), RoadTraffic (-0.305), Homicide (-0.044)
- **Gap-widening indicators**: ChronicRespiratory (+0.111), Diabetes (+0.223)
- **Largest single counterfactual effect**: Suicide: -0.393 years (reducing gap from 16.0 to 3.27, targeting Türkiye)
- **Aggregate gap-closing total**: -1.544 years
- **Aggregate gap-widening total**: +0.334 years
- **Net reduction in predicted gap**: -1.21 years

**Key Findings:**
- Neoplasms is the most important indicator (10.6), with importance entirely from the gap component
- UnintentionalInjury ranks 2nd (7.23), with importance entirely from the gap component
- Suicide has the largest single counterfactual effect (-0.393 years), despite ranking 4th in importance
- RoadTraffic has the 2nd largest counterfactual effect (-0.305 years), despite ranking 7th in importance
- Most indicators contribute through gap components rather than mid components
- Cardiovascular and DrugDisorder were not selected by Elastic Net (importance = 0)

**Changes from 2010:**
- **Neoplasms importance decreased** (17.0 → 10.6, -37.6%), but remained the top indicator
- **UnintentionalInjury importance decreased** (8.68 → 7.23, -16.7%)
- **ChronicRespiratory importance decreased** (6.0 → 4.31, -28.2%)
- **Suicide counterfactual effect increased** (-0.201 → -0.393 years, +95.5%), becoming the largest effect
- **RoadTraffic counterfactual effect increased** (-0.188 → -0.305 years, +62.2%), becoming the 2nd largest effect
- **Net gap reduction increased** (-1.078 → -1.21 years)

**Interpretation of 2015 Patterns:**
- Neoplasms remained dominant but declined in importance
- Suicide prevention became the top intervention priority for LE gaps
- Road traffic injuries regained prominence as an intervention target
- Overall potential for closing gaps increased

### HALE Gap Model (2015)

**Model Performance:**
- **Cross-validation R²**: 0.715 (Elastic Net, best model)
- **In-sample R²**: 0.946 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.441 years (cross-validation), 0.309 years (in-sample)
- **Non-zero coefficients**: 21 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Cardiovascular**: 13.9 (Mid: 13.9, Gap: 0)
2. **Neoplasms**: 13.8 (Mid: 2.52, Gap: 11.2)
3. **UnintentionalInjury**: 5.71 (Mid: 1.18, Gap: 4.53)
4. **ChronicRespiratory**: 5.01 (Mid: 4.1, Gap: 0.911)
5. **Suicide**: 3.05 (Mid: 1.26, Gap: 1.79)
6. **LiverDisease**: 1.95 (Mid: 0.733, Gap: 1.21)
7. **Homicide**: 1.84 (Mid: 0.637, Gap: 1.2)
8. **Alcohol**: 1.51 (Mid: 0.218, Gap: 1.3)
9. **Diabetes**: 0.985 (Mid: 0.618, Gap: 0.366)
10. **RoadTraffic**: 0.905 (Mid: 0.503, Gap: 0.402)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Cardiovascular (-0.0018), Neoplasms (-0.195), UnintentionalInjury (-0.121), Suicide (-0.502), LiverDisease (-0.195), Homicide (-0.164), Alcohol (-0.209), RoadTraffic (-0.308), DrugDisorder (-0.0698)
- **Gap-widening indicators**: ChronicRespiratory (+0.0848), Diabetes (+0.161)
- **Largest single counterfactual effect**: Suicide: -0.502 years (reducing gap from 16.0 to 3.27, targeting Türkiye)
- **Aggregate gap-closing total**: -1.774 years
- **Aggregate gap-widening total**: +0.246 years
- **Net reduction in predicted gap**: -1.528 years

**Key Findings:**
- Cardiovascular is the most important indicator (13.9), with importance entirely from the Mid component
- Neoplasms ranks 2nd (13.8), with substantial contributions from both Mid (2.52) and Gap (11.2) components
- Suicide has the largest single counterfactual effect (-0.502 years), despite ranking 5th in importance
- Most indicators contribute through both Mid and Gap components

**Changes from 2010:**
- **Cardiovascular importance decreased substantially** (24.0 → 13.9, -42.1%), continuing its decline
- **Neoplasms importance increased** (11.3 → 13.8, +22.1%), approaching parity with Cardiovascular
- **UnintentionalInjury importance increased** (5.32 → 5.71, +7.3%)
- **Suicide counterfactual effect increased** (-0.352 → -0.502 years, +42.6%), strengthening its position as top intervention
- **RoadTraffic counterfactual effect decreased slightly** (-0.311 → -0.308 years, -1.0%)
- **Net gap reduction increased** (-1.268 → -1.528 years), suggesting more potential for intervention

**Interpretation of 2015 Patterns:**
- Cardiovascular continued to decline in importance, while Neoplasms gained ground
- The two indicators were nearly equal in importance (13.9 vs 13.8), suggesting a transition period
- Suicide prevention remained the top intervention priority with increased potential
- Overall potential for closing gaps continued to increase

---

## 2019: Pre-Pandemic Health Patterns

**Time Period**: 2019  
**Context**: The most recent pre-pandemic year, representing current health patterns and relationships before COVID-19 disruptions.

### Life Expectancy Gap Model (2019)

**Model Performance:**
- **Cross-validation R²**: 0.879 (Elastic Net, best model)
- **In-sample R²**: 0.971 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.326 years (cross-validation), 0.217 years (in-sample)
- **Non-zero coefficients**: 13 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Neoplasms**: 11.4 (Mid: 0, Gap: 11.4)
2. **UnintentionalInjury**: 4.93 (Mid: 0, Gap: 4.93)
3. **ChronicRespiratory**: 2.22 (Mid: 1.42, Gap: 0.802)
4. **LiverDisease**: 2.08 (Mid: 0.418, Gap: 1.67)
5. **Homicide**: 1.84 (Mid: 0.869, Gap: 0.966)
6. **Suicide**: 1.82 (Mid: 0, Gap: 1.82)
7. **Alcohol**: 1.53 (Mid: 0.281, Gap: 1.25)
8. **Diabetes**: 0.848 (Mid: 0, Gap: 0.848)
9. **RoadTraffic**: 0.442 (Mid: 0.442, Gap: 0)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Neoplasms (-0.214), UnintentionalInjury (-0.301), LiverDisease (-0.203), Homicide (-0.135), Suicide (-0.537), Alcohol (-0.241), RoadTraffic (-0.156)
- **Gap-widening indicators**: ChronicRespiratory (+0.0572), Diabetes (+0.432)
- **Largest single counterfactual effect**: Suicide: -0.537 years (reducing gap from 17.3 to 4.51, targeting Türkiye)
- **Aggregate gap-closing total**: -1.787 years
- **Aggregate gap-widening total**: +0.489 years
- **Net reduction in predicted gap**: -1.298 years

**Key Findings:**
- Neoplasms is the most important indicator, with importance entirely from the gap component (11.4)
- Suicide has the largest single counterfactual effect (-0.537 years), despite ranking 6th in importance
- UnintentionalInjury ranks 2nd in importance and has the 2nd largest counterfactual effect (-0.301 years)
- Most indicators contribute through gap components rather than mid components
- Cardiovascular and DrugDisorder were not selected by Elastic Net (importance = 0)

**Changes from 2015:**
- **Neoplasms importance increased** (10.6 → 11.4, +7.5%), maintaining its top position
- **UnintentionalInjury importance decreased** (7.23 → 4.93, -31.8%)
- **ChronicRespiratory importance decreased substantially** (4.31 → 2.22, -48.5%)
- **Homicide importance more than tripled** (0.522 → 1.84, +252.7%), moving from #9 to #5
- **Suicide counterfactual effect increased** (-0.393 → -0.537 years, +36.6%), becoming the largest effect
- **RoadTraffic counterfactual effect decreased** (-0.305 → -0.156 years, -48.9%)
- **Net gap reduction increased** (-1.21 → -1.298 years)

**Interpretation of 2019 Patterns:**
- Neoplasms (cancer) remained the dominant factor, with importance driven entirely by gender differences
- Suicide prevention became the top intervention priority for LE gaps, with the largest potential effect
- Homicide regained substantial importance, suggesting it became a stronger factor in explaining gender gaps
- Cardiovascular disease was no longer a significant predictor, a major shift from earlier periods
- Overall potential for closing gaps increased to the highest level (-1.298 years)

### HALE Gap Model (2019)

**Model Performance:**
- **Cross-validation R²**: 0.778 (Elastic Net, best model)
- **In-sample R²**: 0.968 (Elastic Net)
- **Mean Absolute Error (MAE)**: 0.422 years (cross-validation), 0.228 years (in-sample)
- **Non-zero coefficients**: 20 out of 22 predictors (Elastic Net)

**Top Indicators by Importance:**
1. **Neoplasms**: 28.2 (Mid: 15.3, Gap: 12.8)
2. **UnintentionalInjury**: 5.69 (Mid: 3.37, Gap: 2.31)
3. **Cardiovascular**: 5.55 (Mid: 5.24, Gap: 0.306)
4. **ChronicRespiratory**: 5.22 (Mid: 4.42, Gap: 0.801)
5. **Homicide**: 3.92 (Mid: 1.44, Gap: 2.48)
6. **Suicide**: 2.96 (Mid: 1.05, Gap: 1.9)
7. **LiverDisease**: 2.52 (Mid: 1.26, Gap: 1.26)
8. **Alcohol**: 1.73 (Mid: 0.491, Gap: 1.23)
9. **Diabetes**: 1.69 (Mid: 0.934, Gap: 0.755)
10. **RoadTraffic**: 0.468 (Mid: 0.468, Gap: 0)

**Counterfactual Analysis (USA):**
- **Gap-closing indicators**: Neoplasms (-0.28), UnintentionalInjury (-0.0421), Homicide (-0.281), Suicide (-0.801), LiverDisease (-0.205), Alcohol (-0.273), RoadTraffic (-0.165), DrugDisorder (-0.206)
- **Gap-widening indicators**: Cardiovascular (+0.00179), ChronicRespiratory (+0.0869), Diabetes (+0.409)
- **Largest single counterfactual effect**: Suicide: -0.801 years (reducing gap from 17.3 to 4.51, targeting Türkiye)
- **Aggregate gap-closing total**: -2.253 years
- **Aggregate gap-widening total**: +0.498 years
- **Net reduction in predicted gap**: -1.755 years

**Key Findings:**
- Neoplasms is by far the most important indicator (28.2), with substantial contributions from both Mid (15.3) and Gap (12.8) components
- Suicide has the largest single counterfactual effect (-0.801 years), despite ranking 6th in importance
- Most indicators contribute through both Mid and Gap components
- Cardiovascular ranks 3rd in importance but has minimal counterfactual effect (+0.00179 years)

**Changes from 2015:**
- **Cardiovascular importance decreased substantially** (13.9 → 5.55, -60.1%), falling from #1 to #3
- **Neoplasms importance more than doubled** (13.8 → 28.2, +104.3%), becoming the dominant indicator
- **Homicide importance more than doubled** (1.84 → 3.92, +113.0%), moving from #7 to #5
- **RoadTraffic importance decreased** (0.905 → 0.468, -48.3%)
- **Suicide counterfactual effect increased substantially** (-0.502 → -0.801 years, +59.6%), strengthening its position as top intervention
- **Net gap reduction increased** (-1.528 → -1.755 years), reaching the highest level across all time periods

**Interpretation of 2019 Patterns:**
- A major shift occurred: Neoplasms (cancer) became the overwhelmingly dominant factor, more than doubling in importance from 2015
- Cardiovascular disease declined substantially in importance, suggesting improvements in cardiovascular health or changes in its relationship to gender gaps
- Suicide prevention became the top intervention priority with the largest potential effect (-0.801 years)
- Homicide regained importance, suggesting it became a stronger factor in explaining gender gaps
- Overall potential for closing gaps reached its peak (-1.755 years), suggesting the greatest opportunities for intervention

---

## Summary and Conclusions: Evolution of Health Patterns Over Time

### Key Temporal Changes: What Has Changed Over Two Decades?

**Major Shifts in Indicator Importance:**

**1. The Rise of Neoplasms (Cancer):**
- **HALE Model**: Dramatically increased from 13.8 (2000) → 28.2 (2019), a 104% increase, becoming the dominant factor
- **LE Model**: Increased from 8.02 (2000) → 11.4 (2019), a 42% increase, maintaining top position
- **Interpretation**: Cancer has become an increasingly important driver of gender gaps in both HALE and LE, suggesting that gender differences in cancer rates and outcomes have grown or become more predictive of overall gender gaps

**2. The Decline of Cardiovascular Disease:**
- **HALE Model**: Decreased from 13.9 (2000) → 5.55 (2019), a 60% decrease, falling from #1 to #3
- **LE Model**: Decreased from 17.6 (2000) → 0 (not selected in 2019), a complete disappearance as a predictor
- **Interpretation**: Cardiovascular disease has become less important in explaining gender gaps, suggesting either improvements in cardiovascular health, reductions in gender differences, or that other factors have become relatively more important

**3. The Evolution of Homicide:**
- **HALE Model**: Decreased from 1.84 (2000) → 1.84 (2015) → 3.92 (2019), showing a recovery pattern
- **LE Model**: Decreased from 5.31 (2000) → 0.522 (2015) → 1.84 (2019), also showing recovery
- **Interpretation**: Homicide declined in importance through the mid-2010s, then regained importance by 2019, suggesting either a resurgence of homicide-related gender gaps or changes in its relationship to overall health outcomes

**4. The Decline of Road Traffic Injuries:**
- **HALE Model**: Decreased from 1.82 (2000) → 0.468 (2019), a 74% decrease
- **LE Model**: Decreased from 1.8 (2000) → 0.442 (2019), a 75% decrease
- **Interpretation**: Road traffic injuries have become less important in explaining gender gaps, likely reflecting improvements in road safety and reductions in gender differences in traffic-related mortality

**5. The Stability of Suicide:**
- **HALE Model**: Relatively stable importance (3.05 → 2.96), but counterfactual effects increased dramatically (-0.502 → -0.801 years, +60% increase)
- **LE Model**: Relatively stable importance (3.87 → 1.82), but counterfactual effects increased substantially (-0.263 → -0.537 years, +104% increase)
- **Interpretation**: While suicide's importance as a predictor remained relatively stable, its potential as an intervention target has increased dramatically, suggesting that gender gaps in suicide have become more addressable or that the potential for improvement has grown

### Evolution of Intervention Opportunities

**Increasing Potential for Gap Reduction:**
- **HALE**: Net gap reduction increased from -1.528 years (2000) → -1.755 years (2019), a 15% increase
- **LE**: Net gap reduction increased from -0.858 years (2000) → -1.298 years (2019), a 51% increase
- **Interpretation**: The potential for closing gender gaps through interventions has increased substantially over time, suggesting either that gaps have widened (creating more room for improvement) or that interventions have become more effective

**Shifting Intervention Priorities:**

**2000-2005 Period:**
- Road traffic injuries and cardiovascular disease were primary intervention targets
- Suicide prevention showed moderate potential

**2010-2015 Period:**
- Suicide prevention emerged as the top intervention priority
- Neoplasms (cancer) prevention gained importance
- Road traffic injuries declined in intervention priority

**2019 (Current Patterns):**
- Suicide prevention is the dominant intervention target (largest counterfactual effect: -0.801 years for HALE, -0.537 years for LE)
- Neoplasms prevention has become increasingly important
- Overall intervention potential has reached its peak

### What These Changes Tell Us About Health Evolution

**1. Cancer Has Become the Dominant Health Issue:**
The dramatic increase in Neoplasms importance, particularly in the HALE model, suggests that:
- Gender differences in cancer incidence, treatment, or outcomes have become the primary driver of gender gaps in healthy life expectancy
- This may reflect improvements in other areas (cardiovascular disease, road safety) that have made cancer relatively more important
- Cancer prevention and treatment equity should be a major focus for addressing gender health gaps

**2. Cardiovascular Health Improvements:**
The decline in Cardiovascular importance suggests:
- Successful public health interventions have reduced cardiovascular disease as a driver of gender gaps
- Gender differences in cardiovascular outcomes may have narrowed
- This represents a success story in public health, though it may have been partially offset by increases in other areas

**3. Suicide Prevention Has Become More Critical:**
The increasing counterfactual effects for Suicide, despite relatively stable importance, suggests:
- Gender gaps in suicide have become more addressable through interventions
- The potential impact of suicide prevention has grown substantially
- Suicide prevention should be a top priority for reducing gender health gaps

**4. Overall Health Patterns Have Shifted:**
The changes in indicator importance and counterfactual effects indicate:
- Health patterns are not static—the factors driving gender gaps have evolved significantly over two decades
- Successes in some areas (cardiovascular, road safety) have been accompanied by new challenges (cancer, suicide)
- The increasing net gap reduction potential suggests that while some gaps may have widened, there are also greater opportunities for intervention

### Implications for Policy and Intervention

**Priority Areas for 2019 and Beyond:**
1. **Suicide Prevention**: Highest intervention potential for both HALE and LE gaps
2. **Cancer Prevention and Treatment**: Dominant factor in HALE gaps, important for LE gaps
3. **Unintentional Injuries**: Consistently important across time periods
4. **Homicide Prevention**: Regained importance by 2019, requiring renewed attention

**Areas Showing Improvement:**
1. **Cardiovascular Disease**: Declined in importance, suggesting successful interventions
2. **Road Traffic Injuries**: Declined in importance, reflecting safety improvements

**Temporal Stability Assessment:**
- **Moderate stability**: Some indicators (Neoplasms, UnintentionalInjury) remain consistently important, while others show substantial temporal variation
- **Dynamic relationships**: The relationships between health indicators and gender gaps have evolved, indicating that health patterns are not static
- **Increasing opportunities**: The potential for closing gender gaps has increased over time, suggesting both challenges and opportunities for intervention

---

## Notes

- All analyses exclude 2020+ data to avoid COVID-19 pandemic distortions
- Cutoff year determines the maximum year included in the analysis. For each country, the most recent year of data available up to the cutoff year is used
- Earlier cutoff years may result in using older data for some countries, which may affect model performance and indicator importance
- Each analysis uses one year of data per country (the most recent year ≤ cutoff year)

