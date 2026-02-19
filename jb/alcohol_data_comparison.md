# Understanding the Difference: WHO Alcohol-Attributable Deaths vs IHME Alcohol Use Disorders

## Summary

The dramatic difference in alcohol gap values between WHO and IHME data (USA: 38.8 vs 5.54, an 86% reduction) reflects fundamental differences in how the two organizations define and measure alcohol-related mortality.

## WHO: Alcohol-Attributable Deaths (Indicator SA_0000001832)

### Definition
WHO uses **"alcohol-attributable all-cause deaths"** which employs **Population Attributable Fraction (PAF)** methodology.

### What It Includes
This approach estimates **all deaths where alcohol is a contributing factor**, including:

1. **Direct alcohol-related deaths:**
   - Alcohol poisoning
   - Alcohol dependence syndrome
   - Alcohol withdrawal

2. **Indirect alcohol-related deaths (where alcohol is a contributing factor):**
   - Liver disease (cirrhosis, alcoholic liver disease)
   - Some cancers (oral, pharyngeal, esophageal, liver, colorectal, breast)
   - Accidents and injuries (road traffic crashes, falls, drownings) where alcohol was involved
   - Violence (homicide, suicide) where alcohol was a contributing factor
   - Cardiovascular diseases where alcohol contributed
   - Other conditions where alcohol is a risk factor

### Methodology
- Uses **Population Attributable Fraction (PAF)** calculations
- Estimates the proportion of deaths from various causes that can be attributed to alcohol
- Based on epidemiological evidence of alcohol's role as a risk factor
- Includes deaths where alcohol is a contributing factor, not just the primary cause

### Example
If 30% of liver disease deaths are attributable to alcohol, and there are 100 liver disease deaths, then 30 deaths are counted as "alcohol-attributable" even if the death certificate lists "liver disease" as the primary cause.

## IHME: Alcohol Use Disorders (Cause B.7.1)

### Definition
IHME uses **"alcohol use disorders"** which refers to deaths where alcohol use disorders are the **primary or direct cause of death**.

### What It Includes
This approach includes deaths where alcohol use disorders are:
- The **primary cause of death** on the death certificate
- Coded as ICD-10 F10 codes (Mental and behavioural disorders due to use of alcohol)
- Includes conditions like:
  - Acute alcohol intoxication
  - Alcohol dependence syndrome (as primary cause)
  - Alcohol withdrawal (as primary cause)
  - Other alcohol-related mental and behavioral disorders

### What It Excludes
This approach **does NOT include**:
- Liver disease deaths (even if alcohol-related) - these are coded under liver disease causes
- Cancer deaths (even if alcohol-related) - these are coded under cancer causes
- Accident deaths (even if alcohol was involved) - these are coded under injury causes
- Other conditions where alcohol is a contributing factor but not the primary cause

### Methodology
- Uses **direct cause-of-death coding** from death certificates
- Follows ICD-10 classification system
- Only counts deaths where alcohol use disorders are the primary cause
- More restrictive definition focused on direct alcohol-related health conditions

## Key Differences

| Aspect | WHO Alcohol-Attributable | IHME Alcohol Use Disorders |
|--------|-------------------------|---------------------------|
| **Scope** | Broad - includes all deaths where alcohol is a contributing factor | Narrow - only deaths where alcohol use disorders are the primary cause |
| **Methodology** | Population Attributable Fraction (PAF) | Direct cause-of-death coding (ICD-10) |
| **Includes** | Direct + indirect alcohol-related deaths | Only direct alcohol use disorder deaths |
| **Examples Included** | Liver disease, some cancers, accidents (if alcohol involved), violence (if alcohol involved) | Alcohol poisoning, alcohol dependence (as primary cause) |
| **Examples Excluded** | None (comprehensive) | Liver disease, cancers, accidents, violence (coded under other causes) |

## Why the Difference is So Large

The 86% difference (38.8 vs 5.54) makes sense because:

1. **WHO includes many more categories:**
   - Liver disease deaths attributable to alcohol
   - Cancer deaths attributable to alcohol
   - Accident deaths where alcohol was involved
   - Violence deaths where alcohol was a contributing factor

2. **IHME only includes direct causes:**
   - Only deaths where alcohol use disorders are the primary cause
   - Excludes all indirect alcohol-related deaths

3. **In the USA context:**
   - Many alcohol-related deaths are coded as liver disease, accidents, or other causes
   - Few deaths have alcohol use disorders as the primary cause
   - This explains why the WHO gap (38.8) is much higher than IHME (5.54)

## Implications for Analysis

### WHO Data Advantages:
- **Comprehensive**: Captures the full burden of alcohol on mortality
- **Policy-relevant**: Shows total impact of alcohol on population health
- **Better for public health**: Reflects all alcohol-related mortality, not just direct causes

### IHME Data Advantages:
- **Specific**: Focuses on direct alcohol use disorder deaths
- **Consistent coding**: Uses standardized ICD-10 cause-of-death codes
- **Better temporal coverage**: 1990-2023 vs WHO's 2019 only
- **Consistent methodology**: Aligns with other IHME indicators

### Which to Use?

The choice depends on the research question:

- **Use WHO** if you want to understand the **total burden** of alcohol on mortality, including indirect effects
- **Use IHME** if you want to focus on **direct alcohol use disorder deaths** or need better temporal coverage

## Conclusion

The large difference between WHO and IHME alcohol data is **expected and reflects different definitions**, not data quality issues. WHO's "alcohol-attributable" definition is much broader and includes indirect alcohol-related deaths, while IHME's "alcohol use disorders" definition is narrower and only includes direct causes. This explains why Alcohol dropped from #1 to #4 in importance when switching from WHO to IHME data - the IHME definition captures a much smaller subset of alcohol-related mortality.

