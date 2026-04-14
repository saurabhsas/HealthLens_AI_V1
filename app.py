import gradio as gr
import pandas as pd
import tempfile

from engine import process_query
from data_loader import load_data

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- LOAD DATA ----------------
df_master = load_data("data.csv")

lob_values = ["All"] + sorted(df_master["LINEOFBUSINESS"].unique().tolist())
gender_values = ["All"] + sorted(df_master["GENDER"].unique().tolist())

# ---------------- COLUMN MAP ----------------
COLUMN_MAP = {
    "ELIGIBILITYYEARANDMONTH": "Eligibility Month",
    "MED_COST": "Medical Cost",
    "RX_COST": "Pharmacy Cost",
    "TOTAL_COST": "Total Cost",
    "ED_VISITS": "ED Visits",
    "IP_VISITS": "IP Visits",
    "COUNTY": "County",
    "AGE_CATEGORY": "Age Category",
    "MEMBERID": "Member ID"
}

# ---------------- FORMAT ----------------
def format_currency(v):
    return f"${v:,.0f}" if v else ""

def format_number(v):
    return f"{int(v):,}" if v else ""


# ---------------- AI INSIGHT ----------------
def generate_insight(df, kpis):

    total = kpis["total_cost"]
    avg = kpis["avg_cost"]

    insight = f"💰 Total cost is {format_currency(total)}. "
    insight += f"📊 Avg cost is {format_currency(avg)}. "

    if "MED_COST" in df.columns and "RX_COST" in df.columns:
        med = df["MED_COST"].sum()
        rx = df["RX_COST"].sum()

        if med + rx > 0:
            pct = round((med / (med + rx)) * 100, 1)
            insight += f"🏥 Medical contributes {pct}%."

    return insight


# ---------------- EXPORT ----------------
def export_excel(df):
    if df is None or len(df) == 0:
        return None

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(temp.name, index=False)
    return temp.name


def export_pdf(df, insight):
    if df is None or len(df) == 0:
        return None

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(temp.name)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("Healthcare Analytics Report", styles["Title"]),
        Spacer(1, 10),
        Paragraph(insight, styles["Normal"]),
        Spacer(1, 10)
    ]

    for _, row in df.head(10).iterrows():
        content.append(Paragraph(str(row.to_dict()), styles["Normal"]))

    doc.build(content)

    return temp.name


# ---------------- MAIN ----------------
def run_query(query, lob, gender):

    result, plot, kpis, _ = process_query(query, lob, gender)
    df = pd.DataFrame(result)

    # Rename columns
    df.rename(columns=COLUMN_MAP, inplace=True)

    # 🔥 FIX Eligibility Month
    if "Eligibility Month" in df.columns:
        df["Eligibility Month"] = df["Eligibility Month"].astype(str)

        try:
            df["Eligibility Month"] = pd.to_datetime(
                df["Eligibility Month"], format="%Y%m"
            )
            df = df.sort_values("Eligibility Month")
            df["Eligibility Month"] = df["Eligibility Month"].dt.strftime("%b-%Y")
        except:
            pass

    # Format table
    for col in df.columns:
        if col == "Eligibility Month":
            continue
        elif "Cost" in col:
            df[col] = df[col].apply(format_currency)
        elif "Visits" in col:
            df[col] = df[col].apply(format_number)

    # KPI
    total = format_currency(kpis["total_cost"])
    avg = f"${kpis['avg_cost']:,.1f}"
    ed = format_number(kpis["total_ed"])
    ip = format_number(kpis["total_ip"])

    insight = generate_insight(df_master, kpis)

    # ---------------- INTELLIGENT CHART FIX ----------------
    if plot:

        # Rename legend labels
        plot.for_each_trace(
            lambda t: t.update(name=COLUMN_MAP.get(t.name, t.name))
        )

        # 🔥 AUTO-DETECT AXIS
        cols = list(df.columns)

        x_label = cols[0] if len(cols) > 0 else "Category"
        y_label = "Value"

        # Improve labels
        x_label = COLUMN_MAP.get(x_label.upper(), x_label)

        # Dynamic title
        title = f"{' vs '.join(cols[1:])} by {x_label}" if len(cols) > 1 else "Analysis"

        plot.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            legend_title="Metrics"
        )

        plot.update_xaxes(type="category")

    return df, plot, total, avg, ed, ip, insight, query, df, insight


def refresh(query, lob, gender):
    if query:
        return run_query(query, lob, gender)
    return None, None, "", "", "", "", "", query, None, ""


# ---------------- PROMPTS ----------------
def generate_prompts(df):

    return [
        "Compare medical and pharmacy cost",
        "Medical cost trend",
        "Top 5 costly members",
        "Top members by total cost",
        "Average medical cost",
        "Total cost by county",
        "Medical cost by age category",
        "Pharmacy cost trend",
        "Compare total and medical cost",
        "Show cost trend over time"
    ]


# ---------------- UI ----------------
with gr.Blocks() as demo:

    gr.Markdown("# 🤖 AI Healthcare Analytics Dashboard")

    gr.Markdown("### 💡 Smart Suggestions")

    prompts = generate_prompts(df_master)
    buttons = []

    with gr.Row():
        for p in prompts[:5]:
            buttons.append(gr.Button(p))

    with gr.Row():
        for p in prompts[5:]:
            buttons.append(gr.Button(p))

    gr.Markdown("<br><br>")

    with gr.Row():
        msg = gr.Textbox(placeholder="🔍 Ask your question...", scale=5)
        run = gr.Button("Run")

    gr.Markdown("## 🎛️ Filters")
    with gr.Row():
        lob = gr.Dropdown(lob_values, value="All", label="LOB")
        gender = gr.Dropdown(gender_values, value="All", label="Gender")

    gr.Markdown("## 📊 Key Metrics")
    with gr.Row():
        total = gr.Textbox(label="💰 Total Cost")
        avg = gr.Textbox(label="📊 Avg Cost")
        ed = gr.Textbox(label="🚑 ED Visits")
        ip = gr.Textbox(label="🏥 IP Visits")

    gr.Markdown("## 📈 Trends / Comparison")
    plot = gr.Plot()

    gr.Markdown("## 🧠 Insights")
    insight_box = gr.Markdown()

    gr.Markdown("## 📋 Data")
    table = gr.Dataframe()

    gr.Markdown("## 📥 Export")
    with gr.Row():
        excel_btn = gr.Button("Download Excel")
        pdf_btn = gr.Button("Download PDF")

    file_output = gr.File()

    state_df = gr.State()
    state_insight = gr.State()

    run.click(
        run_query,
        [msg, lob, gender],
        [table, plot, total, avg, ed, ip, insight_box, msg, state_df, state_insight]
    )

    msg.submit(
        run_query,
        [msg, lob, gender],
        [table, plot, total, avg, ed, ip, insight_box, msg, state_df, state_insight]
    )

    for btn in buttons:
        btn.click(
            run_query,
            [btn, lob, gender],
            [table, plot, total, avg, ed, ip, insight_box, msg, state_df, state_insight]
        )

    lob.change(
        refresh,
        [msg, lob, gender],
        [table, plot, total, avg, ed, ip, insight_box, msg, state_df, state_insight]
    )

    gender.change(
        refresh,
        [msg, lob, gender],
        [table, plot, total, avg, ed, ip, insight_box, msg, state_df, state_insight]
    )

    excel_btn.click(export_excel, state_df, file_output)
    pdf_btn.click(export_pdf, [state_df, state_insight], file_output)


demo.launch(
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1400px;
        margin: auto;
        padding: 10px;
    }
    """
)