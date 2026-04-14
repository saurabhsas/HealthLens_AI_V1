import pandas as pd
import plotly.express as px
from data_loader import load_data

df_master = load_data("data.csv")


def process_query(query, lob, gender):

    df = df_master.copy()

    # FILTER
    if lob != "All":
        df = df[df["LINEOFBUSINESS"] == lob]

    if gender != "All":
        df = df[df["GENDER"] == gender]

    # KPIs
    kpis = {
        "total_cost": df["TOTAL_COST"].sum(),
        "avg_cost": df["TOTAL_COST"].mean(),
        "total_ed": df.get("EDVISITS", pd.Series()).sum(),
        "total_ip": df.get("IPVISITS", pd.Series()).sum()
    }

    query = query.lower()

    # ---------------- COMPARE ----------------
    if "compare" in query:

        result = df.groupby("ELIGIBILITYYEARANDMONTH")[
            ["MED_COST", "RX_COST"]
        ].sum().reset_index()

        plot = px.line(result,
                       x="ELIGIBILITYYEARANDMONTH",
                       y=["MED_COST", "RX_COST"],
                       title="Medical vs Pharmacy Cost")

        return result, plot, kpis, "Comparison of medical and pharmacy cost."

    # ---------------- TREND ----------------
    if "trend" in query:

        result = df.groupby("ELIGIBILITYYEARANDMONTH")[
            "MED_COST"
        ].sum().reset_index()

        plot = px.line(result,
                       x="ELIGIBILITYYEARANDMONTH",
                       y="MED_COST",
                       title="Medical Cost Trend")

        return result, plot, kpis, "Medical cost trend."

    # ---------------- TOP MEMBERS ----------------
    if "top" in query:

        result = df.groupby("MEMBERID")[
            "TOTAL_COST"
        ].sum().reset_index().sort_values(by="TOTAL_COST", ascending=False).head(5)

        plot = px.bar(result,
                      x="MEMBERID",
                      y="TOTAL_COST",
                      title="Top Costly Members")

        return result, plot, kpis, "Top members by cost."

    # ---------------- COUNTY ----------------
    if "county" in query:

        result = df.groupby("COUNTY")[
            "TOTAL_COST"
        ].sum().reset_index()

        plot = px.bar(result,
                      x="COUNTY",
                      y="TOTAL_COST",
                      title="Cost by County")

        return result, plot, kpis, "Cost by county."

    # ---------------- AGE CATEGORY (FIXED) ----------------
    if "age" in query and "category" in query:

        result = df.groupby("AGE_CATEGORY")[
            "MED_COST"
        ].sum().reset_index()

        plot = px.bar(
            result,
            x="AGE_CATEGORY",
            y="MED_COST",
            title="Medical Cost by Age Category"
        )

        return result, plot, kpis, "Medical cost by age category."

    # ---------------- DEFAULT ----------------
    return df.head(20), None, kpis, "Showing sample data."