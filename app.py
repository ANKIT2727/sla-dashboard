from queries import (
    get_sla_summary,
    get_zero_blp,
    get_zero_dlp,
    get_sla_trend
)
import streamlit as st
from datetime import date, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="SAT METERS SLA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
# SLA STATUS ICON
# ===============================
def sla_icon(value):
    if value >= 98:
        return "🟢"
    elif value >= 95:
        return "🟡"
    else:
        return "🔴"

# ===============================
# HEADER
# ===============================
st.markdown(
    "<h1 style='text-align:center;'>📊 SAT METERS SLA</h1>",
    unsafe_allow_html=True
)

# ===============================
# DATE SELECTOR
# ===============================
left, mid, right = st.columns([1, 3, 1])
with left:
    selected_date = st.date_input("Select Report Date", date.today())

# ===============================
# FETCH SUMMARY DATA
# ===============================
df = get_sla_summary(selected_date)

if df.empty:
    st.warning("No data found for selected date")
    st.stop()

row = df.iloc[0]

# ===============================
# EXECUTIVE SLA SUMMARY
# ===============================
st.markdown("## 📌 Executive SLA Summary")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("TOTAL METERS", f"{int(row['Meter_Number']):,}")
c2.metric("BLP SLA (22 Hrs)", f"{row['SLA_22hrs_BLP']} %", sla_icon(row["SLA_22hrs_BLP"]))
c3.metric("DLP SLA (22 Hrs)", f"{row['SLA_22hrs_DLP']} %", sla_icon(row["SLA_22hrs_DLP"]))
c4.metric("❌ ZERO BLP (22 Hrs)", f"{int(row['Zero_22hrs_BLP_Meter_Count']):,}")
c5.metric("❌ ZERO DLP (22 Hrs)", f"{int(row['Zero_22hrs_DLP_Meter_Count']):,}")

st.divider()

# ===============================
# TARGET vs ACTUAL
# ===============================
st.markdown("## 🎯 Target vs Actual (22 Hrs)")

t1, t2, t3, t4 = st.columns(4)
t1.metric("EXPECTED BL BLOCKS", f"{int(row['Target_BLP_Received']):,}")
t2.metric("RECEIVED BL BLOCKS", f"{int(row['Total_Block_22hrs_Received']):,}")
t3.metric("EXPECTED DL", f"{int(row['Target_DLP_Received']):,}")
t4.metric("RECEIVED DL", f"{int(row['Total_DLP_22hrs_Received']):,}")

st.divider()

# ===============================
# SLA PERFORMANCE BY HOURS
# ===============================
st.markdown("## ⏱ SLA Performance by Time")

s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("BL 7 Hrs", f"{row['SLA_7hrs_BLP']} %")
s2.metric("BL 11 Hrs", f"{row['SLA_11hrs_BLP']} %")
s3.metric("BL 22 Hrs", f"{row['SLA_22hrs_BLP']} %")
s4.metric("DL 12 Hrs", f"{row['SLA_12hrs_DLP']} %")
s5.metric("DL 22 Hrs", f"{row['SLA_22hrs_DLP']} %")

st.divider()

# ===============================
# 📊 22 HRS SLA TREND (ZOOMED BAR CHART)
# ===============================
st.markdown("## 📊 22 Hrs SLA Trend (Date-wise)")

col1, col2 = st.columns(2)
with col1:
    trend_start = st.date_input("Trend Start Date", selected_date - timedelta(days=3))
with col2:
    trend_end = st.date_input("Trend End Date", selected_date)

trend_df = get_sla_trend(trend_start, trend_end)

if not trend_df.empty:
    trend_df["report_date"] = pd.to_datetime(trend_df["report_date"])
    trend_df = trend_df.sort_values("report_date")
    dates = trend_df["report_date"].dt.strftime("%d-%b").tolist()

    # ----------- BLP SLA ZOOMED BAR -----------
    st.markdown("### 🔵 BLP SLA (22 Hrs)")

    blp_vals = trend_df["SLA_22hrs_BLP"].values
    blp_min, blp_max = blp_vals.min() - 0.1, blp_vals.max() + 0.1

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    bars = ax1.bar(dates, blp_vals, width=0.6)

    ax1.set_ylim(blp_min, blp_max)
    ax1.set_ylabel("BLP SLA (%)")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h, f"{h:.2f}%", ha="center", va="bottom")

    st.pyplot(fig1)
    st.divider()

    # ----------- DLP SLA ZOOMED BAR -----------
    st.markdown("### 🟣 DLP SLA (22 Hrs)")

    dlp_vals = trend_df["SLA_22hrs_DLP"].values
    dlp_min, dlp_max = dlp_vals.min() - 0.1, dlp_vals.max() + 0.1

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    bars = ax2.bar(dates, dlp_vals, width=0.6)

    ax2.set_ylim(dlp_min, dlp_max)
    ax2.set_ylabel("DLP SLA (%)")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h, f"{h:.2f}%", ha="center", va="bottom")

    st.pyplot(fig2)

st.divider()

# ===============================
# DRILL-DOWN SECTION
# ===============================
st.markdown("## 🔍 Drill-Down Analysis")

d1, d2 = st.columns(2)
with d1:
    if st.button("View Zero BLP Meters (22 Hrs)"):
        st.dataframe(get_zero_blp(selected_date), use_container_width=True)
with d2:
    if st.button("View Zero DLP Meters (22 Hrs)"):
        st.dataframe(get_zero_dlp(selected_date), use_container_width=True)

# ===============================
# FOOTER
# ===============================
st.markdown(
    "<hr><p style='text-align:center; font-size:12px;'>"
    "SAT METERS SLA | Daily SLA Monitoring"
    "</p>",
    unsafe_allow_html=True
)







