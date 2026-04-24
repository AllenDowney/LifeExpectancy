# Neoplasms Drilldown Analysis Report

## Overview
This report summarizes the findings from a drilldown analysis of the gender gap in cancer (neoplasm) mortality, using data from the IHME Global Burden of Disease (GBD) 2023. We analyzed the "Deaths per 100,000" measure attributable to risk factors (Behavioral, Metabolic, and Environmental/Occupational) across three locations: the **United States**, **Iceland**, and the **OECD Total**.

## Key Findings

### 1. Dominant Causes of the Gender Gap (USA vs. Iceland vs. OECD)
The mortality gap (Male Rate - Female Rate) is driven by different cancers depending on the location.

| Neoplasm | USA Gap | Iceland Gap | OECD Gap |
| :--- | :---: | :---: | :---: |
| **Tracheal, bronchus, and lung cancer** | +18.40 | +4.94 | +42.80 |
| **Liver cancer** | +5.68 | +5.88 | +6.72 |
| **Esophageal cancer** | +5.69 | +4.93 | +5.52 |
| **Breast cancer** | -12.40 | -11.40 | -12.50 |
| **Cervical cancer** | -4.19 | -3.02 | -5.42 |
| **Colon and rectum cancer** | +2.07 | +2.39 | +3.44 |

#### Geographical Variations:
*   **Lung Cancer**: While it is the dominant positive driver for the OECD (+42.8) and USA (+18.4), the gap in **Iceland** is remarkably small (+4.9). This suggests Iceland has much more parity in smoking history or environmental exposures.
*   **Liver and Esophageal Cancer**: These show consistent positive gaps across all three locations, typically between +5 and +7.
*   **Breast Cancer**: This remains the largest "negative" gap (higher female mortality) across all locations, consistently around -11 to -13.

### 2. Risk Factor Contributions
Across all locations, the IHME data attributes these gaps primarily to:
*   **Behavioral Risks**: The single largest driver for lung, liver, and esophageal gaps (primarily smoking and alcohol).
*   **Metabolic Risks**: Significant for colon, liver, and pancreatic cancer gaps (primarily BMI and blood sugar).
*   **Environmental/Occupational Risks**: Contributes to the lung cancer gap and is the primary driver for mesothelioma.

### 3. Missing Data on Specific Cancers
We observed that several cancers—including **Brain/CNS cancer, Eye cancer, Hodgkin lymphoma, and Testicular cancer**—have no risk factor attribution in the GBD dataset. This is because the GBD framework does not currently recognize any of the 87 modifiable risk factors as having a "convincing or suggestive" causal link to these outcomes. Consequently, while these cancers contribute to the *total* neoplasm gap, they do not show up in this *attributable* drilldown.

## Detailed Results (United States)

The following tables provide more granular detail for the United States. In the US, the sum of all "positive" gaps (where male mortality is higher) is **45.70** deaths per 100,000, while the sum of all "negative" gaps (where female mortality is higher) is **-21.93** deaths per 100,000.

### Neoplasm Gaps by Cancer Type
This table shows the death rates (per 100,000) for males and females across 34 cancer types, sorted by the absolute difference.

```{include} tables/neoplasms_gap_usa.html
```

### Risk Factor Attribution
This table shows how the gender gap for each cancer type is allocated across the three risk categories: Behavioral, Environmental/Occupational, and Metabolic.

```{include} tables/neoplasms_risk_gap_usa.html
```

## Conclusion
The "attributable" gender gap in cancer is largely a story of Behavioral and Metabolic risks. The USA and OECD gaps are dominated by lung cancer (Behavioral/Smoking), while Iceland's gap is more evenly distributed across liver, esophageal, and lung cancers. In all regions, breast cancer remains the primary driver of higher female cancer mortality.


