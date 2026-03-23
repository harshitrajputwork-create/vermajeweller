import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Verma Jewellers – Uniform Audit",
    layout="wide",
    page_icon="💎",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .header-band {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 28px 36px;
    border-radius: 14px;
    margin-bottom: 24px;
    color: white;
  }
  .header-band h1 { margin:0; font-size:2rem; font-weight:700; letter-spacing:-.5px; }
  .header-band p  { margin:4px 0 0; opacity:.75; font-size:.95rem; }

  .kpi-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fc 100%);
    border: 1px solid #e8ecf0;
    border-radius: 14px;
    padding: 18px 14px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,.07);
    min-height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .kpi-val { font-size: 2.2rem; font-weight: 700; line-height: 1; margin-bottom: 6px; }
  .kpi-lbl { font-size: .78rem; color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }
  .kpi-sub { font-size: .72rem; color: #9ca3af; margin-top: 4px; }

  .green  { color: #10B981; }
  .yellow { color: #F59E0B; }
  .red    { color: #EF4444; }
  .blue   { color: #3B82F6; }
  .gray   { color: #6B7280; }
  .purple { color: #8B5CF6; }

  .section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e293b;
    border-left: 4px solid #3B82F6;
    padding-left: 10px;
    margin: 24px 0 12px;
  }
  .view-badge {
    display: inline-block;
    background: #EFF6FF;
    color: #1D4ED8;
    border: 1px solid #BFDBFE;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: .8rem;
    font-weight: 600;
    margin-bottom: 6px;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  UNIFORM CHECKLIST DEFINITIONS (from JSON)
# ─────────────────────────────────────────────
UNIFORM_ITEMS = {
    "Sadri Boys": [
        "Boys Uniform", "Hair Proper", "Trimmed/Clean Beard", "Badge",
        "Cleanliness of Shirt Color and Sleeves", "Iron Pent/Sadri/Shirt",
        "Polishe Shoes", "Black Socks", "Belt", "Hankey"
    ],
    "Saree Girls": [
        "Hair Proper Tie with Juda Net", "Eyeliner/Kajal", "Lipshade Same",
        "Peral Earring", "Peral Mala", "Badge", "Iron Saree/Coat/Suit",
        "Nailpaint", "Black Socks", "Black shoes"
    ],
    "Coat Suit Boys": [
        "Hair Proper", "Trimmed/Clean Beard", "Badge",
        "Cleanliness of Shirt Color and Sleeves", "Tie & Pocket Square",
        "Iron Pent/Coat/Shirt", "Polishe Shoes", "Black Socks", "Belt", "Hankey"
    ],
    "Coat Suit Girls": [
        "Ponytail", "Eyeliner/Kajal", "Lipshade Same", "Peral Earring/Gold Earring",
        "Badge", "Iron Pent/Coat/Shirt", "Nailpaint", "Black Socks", "Black shoes", "Belt"
    ],
    "Security": [
        "Black Security Unifrom", "Badge", "Black Socks", "Black shoes", "Gun With Licnce"
    ],
    "House Keeping": [
        "Iron Suit/Duppata/Sweter", "Hair Proper Tie with Juda Net",
        "Nail Proper Clean", "Badge", "Black Socks/Socks", "Eyeliner/Kajal"
    ],
}

TEAM_LEADER_COLS = [
    "Arpana", "Babita", "Himani", "kajal (NPS)", "Kajal( Jewel Club)",
    "Kiranjit", "Mona", "Muskan", "Pooja", "Priyanka Negi", "Priyanka Thakur",
    "Ritika", "Sarla", "Shivani", "Sonal", "Swatika"
]

UNIFORM_SCORE_COLS = {
    "Sadri Boys":     "Sadri Boys",
    "Saree Girls":    "Saree Girls",
    "Coat Suit Boys": "Coat Suit Boys",
    "Coat Suit Girls":"Coat Suit Girls",
    "Security":       "Security",
    "House Keeping":  "House Keeping",
}

def is_blank(val):
    if pd.isna(val): return True
    return str(val).strip() in ("", "--", "-", "N/A", "na")

@st.cache_data(show_spinner="Loading data…")
def load_data(uploaded_file):
    content = uploaded_file.read().decode("utf-8", errors="replace")
    df = pd.read_csv(StringIO(content), dtype=str, low_memory=False)
    df.columns = df.columns.str.strip()

    df["Date"] = pd.to_datetime(
        df["Submitted For"].str.strip(), format="%d %B %Y", errors="coerce"
    )

    def extract_employee(row):
        for col in TEAM_LEADER_COLS:
            if col in df.columns and not is_blank(row.get(col, "")):
                val = str(row[col]).strip()
                if val.upper().startswith("VJS"):
                    return val
        return np.nan

    df["Employee"] = df.apply(extract_employee, axis=1)

    # Parse employee ID and name separately
    df["Employee ID"]   = df["Employee"].apply(
        lambda e: str(e).split("-")[0].strip() if pd.notna(e) and "-" in str(e) else str(e) if pd.notna(e) else np.nan
    )
    df["Employee Name"] = df["Employee"].apply(
        lambda e: "-".join(str(e).split("-")[1:]).strip() if pd.notna(e) and "-" in str(e) else np.nan
    )

    def extract_selected(row):
        uniform = str(row.get("Uniform Issued", "")).strip()
        col = UNIFORM_SCORE_COLS.get(uniform)
        if not col or col not in df.columns:
            return []
        raw = str(row.get(col, "")).strip()
        if is_blank(raw):
            return []
        return [x.strip() for x in raw.split(",") if x.strip()]

    df["SelectedItems"] = df.apply(extract_selected, axis=1)

    def parse_float(val):
        try: return float(str(val).replace("%", "").strip())
        except: return np.nan

    # Use the native top-level 'Compliance' column — this matches what the platform
    # shows in the CSV (column N in the screenshot). The 'Uniform Information' column
    # was the section-level score which could exceed 100 for House Keeping etc.
    df["Compliance_pct"] = df["Compliance"].apply(parse_float)
    df["Attendance"]     = df["Attendance  Status"].str.strip()
    df["Auditor"]        = df["Updated By"].str.strip()
    df["Department"]     = df["Select Department"].str.strip()
    df["Uniform"]        = df["Uniform Issued"].str.strip()
    df["Store"]          = df["Store"].str.strip()

    return df


# ─────────────────────────────────────────────
#  UI HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-band">
  <h1>💎 Verma Jewellers – Uniform Audit Dashboard</h1>
  <p>Upload the Uniform Audit CSV to see live analytics</p>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("📂 Upload Uniform Audit CSV", type=["csv"], label_visibility="collapsed")

if uploaded is None:
    st.info("👆 Please upload the **Uniform Audit.csv** file to begin.")
    st.stop()

df = load_data(uploaded)

# ─────────────────────────────────────────────
#  SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("🔍 Filters")

min_d = df["Date"].dropna().min().date()
max_d = df["Date"].dropna().max().date()
try:
    d0, d1 = st.sidebar.date_input("📅 Date Range", [min_d, max_d])
except ValueError:
    d0, d1 = min_d, max_d

departments = sorted(df["Department"].dropna().unique())
sel_depts = st.sidebar.multiselect("🏢 Department", departments, default=departments)

auditors = sorted(df["Auditor"].dropna().unique())
sel_auditors = st.sidebar.multiselect("👤 Team Leader (Auditor)", auditors, default=auditors)

uniforms = sorted(df[df["Uniform"].notna() & ~df["Uniform"].isin(["--", ""])]["Uniform"].unique())
sel_uniforms = st.sidebar.multiselect("👔 Uniform Type", uniforms, default=uniforms)

st.sidebar.markdown("---")
# ── VIEW TOGGLE ──────────────────────────────────────────────────────────────
view_mode = st.sidebar.radio(
    "📊 Dashboard View",
    options=["Auditor View", "Auditee (Employee) View"],
    index=0,
    help="Switch between summary by Auditor/Store vs. by individual Employee"
)

# ─────────────────────────────────────────────
#  FILTER DATA
# ─────────────────────────────────────────────
mask = (
    (df["Date"].dt.date >= d0) & (df["Date"].dt.date <= d1) &
    (df["Department"].isin(sel_depts)) &
    (df["Auditor"].isin(sel_auditors))
)
fdf = df[mask].copy()

present_df = fdf[fdf["Attendance"] == "Present"].copy()
uniform_df = present_df[
    present_df["Uniform"].isin(sel_uniforms) &
    present_df["Uniform Issued"].notna()
].copy()

# ─────────────────────────────────────────────
#  KPI HELPERS
# ─────────────────────────────────────────────
def kpi_block(val, label, sub, css_class="blue"):
    return f"""
    <div class="kpi-card">
      <div class="kpi-val {css_class}">{val}</div>
      <div class="kpi-lbl">{label}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

# ─────────────────────────────────────────────
#  SHARED MISSING-ITEMS COMPUTATION
# ─────────────────────────────────────────────
def compute_missing(subdf):
    missing_counter = {}
    for _, row in subdf.iterrows():
        u = row["Uniform"]
        all_items = UNIFORM_ITEMS.get(u, [])
        selected  = row["SelectedItems"]
        for it in all_items:
            found = any(it.lower() in s.lower() or s.lower() in it.lower() for s in selected)
            if not found:
                missing_counter[it] = missing_counter.get(it, 0) + 1
    if not missing_counter:
        return pd.DataFrame(columns=["Item", "Times Missing"])
    return (
        pd.DataFrame(list(missing_counter.items()), columns=["Item", "Times Missing"])
        .sort_values("Times Missing", ascending=False)
        .head(12)
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW A: AUDITOR VIEW  (original dashboard)
# ═══════════════════════════════════════════════════════════════════════════════
if view_mode == "Auditor View":

    st.markdown('<span class="view-badge">📋 Auditor / Store View</span>', unsafe_allow_html=True)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    total_attempts    = len(fdf)            # Every row that TL submitted, including absent
    successful_audits = len(uniform_df)     # Present + uniform recorded
    not_present       = len(fdf[fdf["Attendance"] != "Present"])
    avg_compliance    = uniform_df["Compliance_pct"].mean() if not uniform_df.empty else 0
    audit_days        = (d1 - d0).days + 1

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(kpi_block(
            total_attempts, "Total Audit Attempts",
            "All rows submitted by TLs", "blue"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_block(
            successful_audits, "Uniform Audits Done",
            "Present + uniform recorded", "green"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_block(
            not_present, "Not Present",
            "Absent / Leave / Week off / Official", "red"), unsafe_allow_html=True)
    with col4:
        c_class = "green" if avg_compliance >= 90 else ("yellow" if avg_compliance >= 75 else "red")
        st.markdown(kpi_block(
            f"{avg_compliance:.1f}%", "Avg Uniform Compliance",
            "Based on audited employees", c_class), unsafe_allow_html=True)
    with col5:
        st.markdown(kpi_block(audit_days, "Days in Range", f"{min_d} → {max_d}", "gray"), unsafe_allow_html=True)

    # ── Compliance Trend + Dept Bar ───────────────────────────────────────────
    st.markdown('<div class="section-title">Compliance Overview</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2])

    with c1:
        st.subheader("📈 Daily Avg Compliance %")
        if not uniform_df.empty:
            td = uniform_df.groupby(uniform_df["Date"].dt.date)["Compliance_pct"].mean().reset_index()
            td.columns = ["Date", "Compliance"]
            fig = px.line(td, x="Date", y="Compliance", markers=True, line_shape="spline",
                          template="plotly_white", color_discrete_sequence=["#3B82F6"])
            fig.update_yaxes(range=[0, 105], title="Compliance %")
            fig.update_traces(line_width=2.5)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No compliance data for selected filters.")

    with c2:
        st.subheader("🏢 By Department")
        if not uniform_df.empty:
            dd = uniform_df.groupby("Department")["Compliance_pct"].mean().reset_index().sort_values("Compliance_pct")
            fig = px.bar(dd, x="Compliance_pct", y="Department", orientation="h",
                         template="plotly_white", color="Compliance_pct",
                         color_continuous_scale="RdYlGn", range_color=[50, 100])
            fig.update_layout(coloraxis_showscale=False, xaxis_range=[0, 105])
            fig.update_xaxes(title="Avg Compliance %")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data.")

    # ── Uniform Type + Attendance Pie ─────────────────────────────────────────
    c3, c4 = st.columns([2, 2])

    with c3:
        st.subheader("👔 Compliance by Uniform Type")
        if not uniform_df.empty:
            ud = uniform_df.groupby("Uniform")["Compliance_pct"].mean().reset_index().sort_values("Compliance_pct", ascending=False)
            fig = px.bar(ud, x="Uniform", y="Compliance_pct", template="plotly_white",
                         color="Compliance_pct", color_continuous_scale="RdYlGn", range_color=[50, 100])
            fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_range=[0, 105])
            fig.update_yaxes(title="Avg Compliance %")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data.")

    with c4:
        st.subheader("📊 Attendance Distribution")
        if not fdf.empty:
            att = fdf["Attendance"].value_counts().reset_index()
            att.columns = ["Status", "Count"]
            fig = px.pie(att, names="Status", values="Count", hole=0.42,
                         template="plotly_white", color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data.")

    # ── Auditor Leaderboard + Missing Items ───────────────────────────────────
    st.markdown('<div class="section-title">Auditor Performance & Gaps</div>', unsafe_allow_html=True)
    c5, c6 = st.columns([2, 3])

    with c5:
        st.subheader("👤 Auditor Leaderboard")
        if not uniform_df.empty:
            al = (
                uniform_df.groupby("Auditor")
                .agg(Audits=("Employee", "count"), AvgComp=("Compliance_pct", "mean"))
                .reset_index().sort_values("AvgComp", ascending=False)
            )
            al["AvgComp"] = al["AvgComp"].round(1)
            al.columns = ["Auditor", "# Uniform Audits", "Avg Compliance %"]
            st.dataframe(al, hide_index=True, use_container_width=True)
        else:
            st.info("No data.")

    with c6:
        st.subheader("❌ Most Common Non-Compliant Items")
        mc_df = compute_missing(uniform_df)
        if not mc_df.empty:
            fig = px.bar(mc_df, x="Times Missing", y="Item", orientation="h",
                         template="plotly_white", color="Times Missing", color_continuous_scale="Reds")
            fig.update_layout(coloraxis_showscale=False, yaxis={"autorange": "reversed"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No missing items found!")

    # ── Store × Uniform stacked bar ───────────────────────────────────────────
    st.markdown('<div class="section-title">Store & Uniform Breakdown</div>', unsafe_allow_html=True)
    if not uniform_df.empty:
        su = uniform_df.groupby(["Store", "Uniform"]).size().reset_index(name="Count")
        fig = px.bar(su, x="Store", y="Count", color="Uniform", template="plotly_white",
                     barmode="stack", color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_xaxes(title="Store", tickangle=-25)
        st.plotly_chart(fig, use_container_width=True)

    # ── Raw Records Table ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">All Audit Records</div>', unsafe_allow_html=True)
    disp = fdf[["Date","Store","Department","Auditor","Employee Name","Employee ID",
                 "Attendance","Uniform","Compliance_pct"]].copy()
    disp.columns = ["Date","Store","Department","Auditor","Employee","Emp ID",
                    "Attendance","Uniform Type","Compliance %"]
    disp["Date"] = disp["Date"].dt.strftime("%d %b %Y")
    disp["Compliance %"] = pd.to_numeric(disp["Compliance %"], errors="coerce").round(1)
    st.dataframe(disp.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW B: AUDITEE (EMPLOYEE) VIEW
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<span class="view-badge">🙋 Auditee / Employee View</span>', unsafe_allow_html=True)

    # Only use audited (present) rows with a valid employee
    emp_df = uniform_df[uniform_df["Employee"].notna()].copy()

    # ── KPIs ─────────────────────────────────────────────────────────────────
    total_attempts    = len(fdf)
    unique_auditees   = emp_df["Employee"].nunique()
    avg_compliance    = emp_df["Compliance_pct"].mean() if not emp_df.empty else 0
    fully_compliant   = (
        emp_df[emp_df["Compliance_pct"] >= 100]["Employee"].nunique()
        if not emp_df.empty else 0
    )
    non_compliant     = unique_auditees - fully_compliant

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(kpi_block(
            total_attempts, "Total Audit Attempts",
            "All rows submitted by TLs", "blue"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_block(
            unique_auditees, "Unique Employees Audited",
            "Present + uniform recorded", "green"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_block(
            fully_compliant, "Fully Compliant",
            "100% compliance score", "green"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_block(
            non_compliant, "Below 100%",
            "At least one item missing", "red"), unsafe_allow_html=True)
    with col5:
        c_class = "green" if avg_compliance >= 90 else ("yellow" if avg_compliance >= 75 else "red")
        st.markdown(kpi_block(
            f"{avg_compliance:.1f}%", "Avg Employee Compliance",
            "Across all audit records", c_class), unsafe_allow_html=True)

    # ── Employee compliance chart ─────────────────────────────────────────────
    st.markdown('<div class="section-title">Employee Compliance Summary</div>', unsafe_allow_html=True)

    if not emp_df.empty:
        # Per-employee avg compliance (may have multiple audit dates)
        emp_summary = (
            emp_df.groupby(["Employee Name", "Employee ID", "Department", "Uniform"])
            .agg(
                Days_Audited=("Date", "nunique"),
                Avg_Compliance=("Compliance_pct", "mean"),
                Min_Compliance=("Compliance_pct", "min"),
                Max_Compliance=("Compliance_pct", "max"),
            )
            .reset_index()
        )
        emp_summary["Avg_Compliance"] = emp_summary["Avg_Compliance"].round(1)
        emp_summary["Min_Compliance"] = emp_summary["Min_Compliance"].round(1)
        emp_summary["Max_Compliance"] = emp_summary["Max_Compliance"].round(1)

        # ── Employee compliance bar ───────────────────────────────────────────
        c1, c2 = st.columns([3, 2])

        with c1:
            st.subheader("📊 Employee Avg Compliance %")
            # Show ALL employees sorted by compliance then name, removing .tail(40)
            plot_df = emp_summary.sort_values(["Avg_Compliance", "Employee Name"], ascending=[True, False])
            fig = px.bar(
                plot_df, x="Avg_Compliance", y="Employee Name",
                orientation="h", template="plotly_white",
                color="Avg_Compliance", color_continuous_scale="RdYlGn",
                range_color=[50, 100],
                hover_data={"Department": True, "Uniform": True,
                            "Days_Audited": True, "Min_Compliance": True}
            )
            fig.update_layout(
                coloraxis_showscale=False,
                xaxis_range=[0, 100],  # Fix the x-axis to exactly 100 to avoid the visual 'break' overlap at 108
                height=max(400, len(plot_df) * 22)
            )
            fig.update_xaxes(title="Avg Compliance %")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("🏢 Avg Compliance by Department")
            dept_emp = (
                emp_df.groupby("Department")["Compliance_pct"].mean()
                .reset_index().sort_values("Compliance_pct")
            )
            fig = px.bar(dept_emp, x="Compliance_pct", y="Department", orientation="h",
                         template="plotly_white", color="Compliance_pct",
                         color_continuous_scale="RdYlGn", range_color=[50, 100])
            fig.update_layout(coloraxis_showscale=False, xaxis_range=[0, 108])
            fig.update_xaxes(title="Avg Compliance %")
            st.plotly_chart(fig, use_container_width=True)

        # ── Compliance trend per employee ─────────────────────────────────────
        st.markdown('<div class="section-title">Employee Compliance Over Time</div>', unsafe_allow_html=True)
        all_names = sorted(emp_df["Employee Name"].dropna().unique())
        sel_emps = st.multiselect(
            "Select employee(s) to plot trends",
            options=all_names,
            default=all_names[:5] if len(all_names) >= 5 else all_names
        )
        if sel_emps:
            trend_data = emp_df[emp_df["Employee Name"].isin(sel_emps)]
            trend = (
                trend_data.groupby(["Date", "Employee Name"])["Compliance_pct"]
                .mean().reset_index()
            )
            fig = px.line(
                trend, x="Date", y="Compliance_pct", color="Employee Name",
                markers=True, template="plotly_white", line_shape="spline"
            )
            fig.update_yaxes(range=[0, 108], title="Compliance %")
            st.plotly_chart(fig, use_container_width=True)

        # ── Missing items for selected employees ──────────────────────────────
        st.markdown('<div class="section-title">Non-Compliance Item Gaps</div>', unsafe_allow_html=True)
        c3, c4 = st.columns([3, 2])

        with c3:
            st.subheader("❌ Most Common Missing Items (Employee View)")
            mc_df = compute_missing(emp_df)
            if not mc_df.empty:
                fig = px.bar(mc_df, x="Times Missing", y="Item", orientation="h",
                             template="plotly_white", color="Times Missing",
                             color_continuous_scale="Reds")
                fig.update_layout(coloraxis_showscale=False, yaxis={"autorange": "reversed"})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No missing items!")

        with c4:
            st.subheader("👔 Employees by Uniform Type")
            unif_emp = emp_df.groupby("Uniform")["Employee"].nunique().reset_index()
            unif_emp.columns = ["Uniform", "Unique Employees"]
            fig = px.pie(unif_emp, names="Uniform", values="Unique Employees", hole=0.4,
                         template="plotly_white",
                         color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

        # ─────────────────────────────────────────────────────────────────────
        #  SINGLE MERGED EMPLOYEE TABLE  (replaces both summary + drill-down)
        #  — one row per audit date per employee
        #  — Streamlit's built-in column search / filter works on every column
        # ─────────────────────────────────────────────────────────────────────
        st.markdown(
            '<div class="section-title">📋 Employee Audit Detail Table '
            '<span style="font-size:.8rem;font-weight:400;color:#6b7280;">'
            '— use the 🔍 column search icon on any column header to filter</span></div>',
            unsafe_allow_html=True
        )

        # Build flat per-audit-record table
        flat = emp_df[
            ["Date", "Employee Name", "Employee ID", "Department", "Store",
             "Auditor", "Uniform", "Compliance_pct", "SelectedItems"]
        ].copy()

        # Compute missing items per row as a readable string
        def missing_items_str(row):
            all_items = UNIFORM_ITEMS.get(row["Uniform"], [])
            selected  = row["SelectedItems"] if isinstance(row["SelectedItems"], list) else []
            missing = [
                it for it in all_items
                if not any(it.lower() in s.lower() or s.lower() in it.lower() for s in selected)
            ]
            return ", ".join(missing) if missing else "—"

        flat["Missing Items"]   = flat.apply(missing_items_str, axis=1)
        flat["Selected Items"]  = flat["SelectedItems"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else "")
        flat["Compliance_pct"]  = flat["Compliance_pct"].round(1)
        flat["Date"]            = flat["Date"].dt.strftime("%d %b %Y")

        flat = flat.drop(columns=["SelectedItems"]).rename(columns={
            "Employee Name":  "Employee",
            "Employee ID":    "Emp ID",
            "Uniform":        "Uniform Type",
            "Compliance_pct": "Compliance %",
        })

        flat = flat[
            ["Date", "Employee", "Emp ID", "Department", "Store",
             "Auditor", "Uniform Type", "Compliance %",
             "Selected Items", "Missing Items"]
        ].sort_values(["Employee", "Date"], ascending=[True, False])

        st.dataframe(
            flat,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Compliance %": st.column_config.NumberColumn(
                    "Compliance %", format="%.1f %%",
                    help="Overall compliance % from the platform (Compliance column in CSV)"
                ),
                "Date":          st.column_config.TextColumn("Date", width="small"),
                "Employee":      st.column_config.TextColumn("Employee"),
                "Emp ID":        st.column_config.TextColumn("Emp ID", width="small"),
                "Department":    st.column_config.TextColumn("Department"),
                "Store":         st.column_config.TextColumn("Store"),
                "Auditor":       st.column_config.TextColumn("Auditor (TL)"),
                "Uniform Type":  st.column_config.TextColumn("Uniform Type"),
                "Selected Items":st.column_config.TextColumn("✅ Selected Items", width="large"),
                "Missing Items": st.column_config.TextColumn("❌ Missing Items", width="large"),
            }
        )
    else:
        st.info("No employee audit records for selected filters.")


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#9ca3af;font-size:.82rem;'>"
    "Verma Jewellers · Uniform Audit Dashboard · Built with Taqtics</p>",
    unsafe_allow_html=True
)
