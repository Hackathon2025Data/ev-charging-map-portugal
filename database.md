# SQLite Database Analysis - Charging Stations (`charging_stations.db`)

This document summarizes the exploratory analysis performed on the `charging_stations.db` database, created from the `data/postos_carregamento.json` JSON file.

## Initial Database Summary

Based on the initial queries, we obtained the following summary of the `stations` table:

*   **Total Stations:** 3,660
*   **Total Charging Points:** 7,067
*   **Average Total Power per Station:** ~87.8 kW
*   **Average Power per Charging Point:** ~41.1 kW
*   **Top 5 Cities (by record count):**
    1.  Lisboa: 228
    2.  Unknown/Null: 130
    3.  Lisbon: 110
    4.  Porto: 92
    5.  Oeiras: 67

> **Note:** Inconsistencies were observed in city names (e.g., 'Lisboa' vs 'Lisbon') and the presence of null values, indicating the need for data cleaning/normalization either at the source or during database insertion.

## Detailed Analysis (Questions & Answers)

The following questions were formulated and answered to deepen the analysis:

### 1. How many stations have a total power greater than 150 kW?

**SQL Query:**
```sql
SELECT COUNT(*) as CountHighPower
FROM stations
WHERE potencia_total_kw > 150;
```

**Answer:** 538 stations.

### 2. What is the average power per charging point in the city of Porto?

**SQL Query:**
```sql
SELECT AVG(potencia_por_ponto_kw) as AvgPowerPerPointPorto
FROM stations
WHERE cidade = 'Porto';
```

**Answer:** Approximately 34.2 kW.

### 3. How many stations lack operator information?

**SQL Query:**
```sql
SELECT COUNT(*) as CountNoOperator
FROM stations
WHERE operador IS NULL OR operador = 'Unknown';
```

**Answer:** 3,660 stations (all stations in the database).

## Conclusion

The analysis of the SQLite database allowed for a quick overview and answers to specific questions about the charging stations. A significant finding is the widespread lack of operator information in the loaded data, which limits analyses related to service providers.