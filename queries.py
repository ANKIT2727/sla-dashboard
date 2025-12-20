import pandas as pd
from db import get_connection


# -------------------------------
# COMMON QUERY RUNNER
# -------------------------------
def run_query(query, params=None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


# -------------------------------
# MAIN SLA SUMMARY QUERY (FULL)
# -------------------------------
def get_sla_summary(report_date):
    query = """
    SELECT 
        report_date AS Report_Date,

        /* 🔢 TOTAL METERS */
        COUNT(DISTINCT meter_no) AS Meter_Number,

        /* 🎯 TARGET VALUES */
        COUNT(DISTINCT meter_no) * 48 AS Target_BLP_Received,
        COUNT(DISTINCT meter_no)      AS Target_DLP_Received,

        /* 📊 ACTUAL RECEIVED – BLP */
        SUM(block_7_hrs)  AS Total_Block_7hrs_Received,
        SUM(block_11_hrs) AS Total_Block_11hrs_Received,
        SUM(block_22_hrs) AS Total_Block_22hrs_Received,

        /* 📊 ACTUAL RECEIVED – DLP */
        SUM(daily_12_hrs) AS Total_DLP_12hrs_Received,
        SUM(daily_22_hrs) AS Total_DLP_22hrs_Received,

        /* 📈 SLA % – BLP */
        ROUND(
            (SUM(block_7_hrs) /
             NULLIF(COUNT(DISTINCT meter_no) * 48, 0)) * 100, 2
        ) AS SLA_7hrs_BLP,

        ROUND(
            (SUM(block_11_hrs) /
             NULLIF(COUNT(DISTINCT meter_no) * 48, 0)) * 100, 2
        ) AS SLA_11hrs_BLP,

        ROUND(
            (SUM(block_22_hrs) /
             NULLIF(COUNT(DISTINCT meter_no) * 48, 0)) * 100, 2
        ) AS SLA_22hrs_BLP,

        /* 📈 SLA % – DLP */
        ROUND(
            (SUM(daily_12_hrs) /
             NULLIF(COUNT(DISTINCT meter_no), 0)) * 100, 2
        ) AS SLA_12hrs_DLP,

        ROUND(
            (SUM(daily_22_hrs) /
             NULLIF(COUNT(DISTINCT meter_no), 0)) * 100, 2
        ) AS SLA_22hrs_DLP,

        /* ❌ ZERO DATA METERS */
        SUM(CASE WHEN block_22_hrs = 0 THEN 1 ELSE 0 END)
            AS Zero_22hrs_BLP_Meter_Count,

        SUM(CASE WHEN daily_22_hrs = 0 THEN 1 ELSE 0 END)
            AS Zero_22hrs_DLP_Meter_Count

    FROM hes.sla
    WHERE report_date = %s
    GROUP BY report_date
    """
    return run_query(query, [report_date])


# -------------------------------
# DRILL-DOWN: ZERO BLP METERS
# -------------------------------
def get_zero_blp(report_date):
    query = """
    SELECT
        meter_no,
        block_7_hrs,
        block_11_hrs,
        block_22_hrs
    FROM hes.sla
    WHERE report_date = %s
      AND block_22_hrs = 0
    ORDER BY meter_no
    """
    return run_query(query, [report_date])


# -------------------------------
# DRILL-DOWN: ZERO DLP METERS
# -------------------------------
def get_zero_dlp(report_date):
    query = """
    SELECT
        meter_no,
        daily_12_hrs,
        daily_22_hrs
    FROM hes.sla
    WHERE report_date = %s
      AND daily_22_hrs = 0
    ORDER BY meter_no
    """
    return run_query(query, [report_date])


# -------------------------------
# SLA TREND: 22 HRS (BLP vs DLP)
# USED FOR BAR GRAPH / HISTOGRAM
# -------------------------------
def get_sla_trend(start_date, end_date):
    query = """
    SELECT
        report_date,

        ROUND(
            (SUM(block_22_hrs) /
             NULLIF(COUNT(DISTINCT meter_no) * 48, 0)) * 100, 2
        ) AS SLA_22hrs_BLP,

        ROUND(
            (SUM(daily_22_hrs) /
             NULLIF(COUNT(DISTINCT meter_no), 0)) * 100, 2
        ) AS SLA_22hrs_DLP

    FROM hes.sla
    WHERE report_date BETWEEN %s AND %s
    GROUP BY report_date
    ORDER BY report_date
    """
    return run_query(query, [start_date, end_date])


