import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)

# =====================================================================
# APP IDENTITY
# =====================================================================
APP_NAME = "NutriPath"
APP_TAGLINE = "Your Personalized Path to Smarter Eating"

st.set_page_config(
    page_title=f"{APP_NAME} | Diet & Macro Calculator",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# CUSTOM STYLING
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    color: #111111;
}

/* Force readable dark text everywhere by default */
p, span, div, label, li, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText, .stCaption, .stAlert, .stTextInput label,
.stNumberInput label, .stSelectbox label {
    color: #111111;
}

.stApp {
    background-color: #f2fbf4; /* light green */
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
}
section[data-testid="stSidebar"] * {
    color: #111111;
}

/* Input fields (number inputs, text inputs, selectboxes) — force light background + dark text */
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 1px solid #cfe8d8 !important;
}
.stNumberInput button {
    background-color: #f2fbf4 !important;
    color: #111111 !important;
}
.stSelectbox div[data-baseweb="select"] * {
    color: #111111 !important;
}
/* Dropdown menu options */
ul[data-baseweb="menu"] {
    background-color: #ffffff !important;
}
ul[data-baseweb="menu"] li {
    color: #111111 !important;
}

/* Hero header — keep white text here since it sits on a dark green gradient */
.hero {
    background: linear-gradient(135deg, #1f8a4c 0%, #34c471 55%, #7be0a3 100%);
    padding: 2.6rem 2rem;
    border-radius: 20px;
    color: #ffffff;
    text-align: center;
    margin-bottom: 1.6rem;
    box-shadow: 0 10px 30px rgba(31, 138, 76, 0.25);
}
.hero h1, .hero p {
    color: #ffffff !important;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
    letter-spacing: -0.5px;
}
.hero p {
    font-size: 1.05rem;
    opacity: 0.95;
    margin: 0;
}

/* Section card */
.section-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    margin-bottom: 1.4rem;
    border: 1px solid #eaf3ec;
    color: #111111;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1f8a4c;
    margin-bottom: 0.8rem;
}

/* Metric-like badge cards */
.badge-card {
    background: #ffffff;
    border: 1px solid #d7f0e0;
    border-radius: 14px;
    padding: 1rem 1.1rem;
    text-align: center;
}
.badge-card .label {
    font-size: 0.82rem;
    color: #333333;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.badge-card .value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #146c3a;
    margin-top: 0.15rem;
}

/* Buttons — keep white text, they sit on a solid green button background */
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #1f8a4c, #34c471);
    color: #ffffff !important;
    font-weight: 600;
    border-radius: 12px;
    border: none;
    padding: 0.7rem 1.2rem;
    box-shadow: 0 6px 16px rgba(31,138,76,0.25);
}
.stButton>button:hover, .stDownloadButton>button:hover {
    background: linear-gradient(135deg, #17703c, #2bab63);
    color: #ffffff !important;
}

/* Footer */
.footer-note {
    text-align: center;
    color: #333333;
    font-size: 0.85rem;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# HERO HEADER
# =====================================================================
st.markdown(f"""
<div class="hero">
    <h1>🥗 {APP_NAME}</h1>
    <p>{APP_TAGLINE} — Calories, Macros, Hydration, BMI & a Full Downloadable Report</p>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# INPUTS
# =====================================================================
with st.sidebar:
    st.header("📋 Your Details")
    name = st.text_input("Name (optional)", value="")
    gender = st.selectbox("Gender", ["Female", "Male"])
    age = st.number_input("Age (years)", min_value=10, max_value=100, value=25, step=1)

    st.divider()
    current_w = st.number_input("Current Weight (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.5)
    goal_w = st.number_input("Goal Weight (kg)", min_value=1.0, max_value=300.0, value=65.0, step=0.5)
    height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.70, step=0.01)

    st.divider()
    meals = st.number_input("Meals Per Day", min_value=1, max_value=10, value=3, step=1)
    activity = st.selectbox(
        "🏃 Activity Level",
        ["sedentary", "light", "moderate", "active", "very active"],
        help="sedentary: little/no exercise · light: 1-3 days/wk · moderate: 3-5 days/wk · "
             "active: 6-7 days/wk · very active: hard exercise + physical job"
    )

    st.divider()
    calculate = st.button("✨ Calculate My Diet Plan", type="primary", use_container_width=True)

if not calculate:
    st.info("👈 Fill in your details in the sidebar and click **Calculate My Diet Plan** to get started.")
    st.markdown(f"""
    <div class="footer-note">🥗 {APP_NAME} — {APP_TAGLINE}</div>
    """, unsafe_allow_html=True)
    st.stop()

# =====================================================================
# CALCULATIONS
# =====================================================================
activity_levels = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very active": 1.9
}
activity_label = activity.title()
height_cm = height * 100

# --- BMR (Mifflin-St Jeor) ---
if gender == "Male":
    bmr = (10 * current_w) + (6.25 * height_cm) - (5 * age) + 5
else:
    bmr = (10 * current_w) + (6.25 * height_cm) - (5 * age) - 161

tdee = bmr * activity_levels[activity]

# --- Goal-adjusted calories ---
weight_diff = current_w - goal_w  # positive = needs to lose
if weight_diff > 0.1:
    goal_type = "Weight Loss"
    kcal = tdee - 500
elif weight_diff < -0.1:
    goal_type = "Weight Gain"
    kcal = tdee + 300
else:
    goal_type = "Maintenance"
    kcal = tdee

kcal = max(kcal, 1200)  # safety floor

# --- Macronutrients ---
protein = goal_w * 1.9
fats = current_w * 0.7
protein_kcal = protein * 4
fats_kcal = fats * 9
carbs = max((kcal - (protein_kcal + fats_kcal)) / 4, 0)
carbs_kcal = carbs * 4

protein_pct = (protein_kcal / kcal) * 100
fats_pct = (fats_kcal / kcal) * 100
carbs_pct = (carbs_kcal / kcal) * 100

# --- Fibre & Water ---
fibres = (kcal / 1000) * 14
water = current_w * 35

# --- BMI ---
bmi = current_w / (height ** 2)
if bmi < 18.5:
    category = "Underweight"
    bmi_color = "#f0a500"
elif bmi < 25:
    category = "Normal weight"
    bmi_color = "#1f8a4c"
elif bmi < 30:
    category = "Overweight"
    bmi_color = "#e07b00"
else:
    category = "Obese"
    bmi_color = "#d64545"

ideal_weight_low = 18.5 * (height ** 2)
ideal_weight_high = 24.9 * (height ** 2)

# --- Per Meal ---
protein_per_meal = protein / meals
calories_per_meal = kcal / meals

# --- Goal Timeline ---
abs_diff = abs(weight_diff)
min_weeks = abs_diff / 1.0
max_weeks = abs_diff / 0.5

# =====================================================================
# RESULTS — ON SCREEN
# =====================================================================
display_name = name.strip() if name.strip() else "there"
st.markdown(f"### 👋 Hey {display_name}, here's your personalized plan")

# --- BMI + Energy summary ---
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚖️ Body Metrics</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="badge-card"><div class="label">BMI</div><div class="value" style="color:{bmi_color}">{bmi:.1f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="badge-card"><div class="label">Category</div><div class="value" style="color:{bmi_color};font-size:1.1rem">{category}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="badge-card"><div class="label">BMR</div><div class="value">{bmr:.0f}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="badge-card"><div class="label">TDEE</div><div class="value">{tdee:.0f}</div></div>', unsafe_allow_html=True)
st.caption(f"💡 A healthy weight range for your height is roughly **{ideal_weight_low:.1f} – {ideal_weight_high:.1f} kg**.")
st.markdown('</div>', unsafe_allow_html=True)

# --- Daily requirements ---
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown(f'<div class="section-title">🔥 Daily Targets — {goal_type}</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="badge-card"><div class="label">Calories</div><div class="value">{kcal:.0f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="badge-card"><div class="label">Protein</div><div class="value">{protein:.0f} g</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="badge-card"><div class="label">Fats</div><div class="value">{fats:.0f} g</div></div>', unsafe_allow_html=True)
st.write("")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="badge-card"><div class="label">Carbs</div><div class="value">{carbs:.0f} g</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="badge-card"><div class="label">Fibre</div><div class="value">{fibres:.0f} g</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="badge-card"><div class="label">Water</div><div class="value">{water/1000:.2f} L</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Macro distribution chart ---
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🍽️ Macro Calorie Distribution</div>', unsafe_allow_html=True)
chart_col, legend_col = st.columns([1.1, 1])
with chart_col:
    fig, ax = plt.subplots(figsize=(4, 4))
    sizes = [protein_pct, fats_pct, carbs_pct]
    labels = ["Protein", "Fats", "Carbs"]
    colors_pie = ["#1f8a4c", "#f0a500", "#34c4c4"]
    wedges, _ = ax.pie(sizes, colors=colors_pie, startangle=90, wedgeprops=dict(width=0.42, edgecolor='white'))
    ax.text(0, 0, f"{kcal:.0f}\nkcal", ha='center', va='center', fontsize=13, fontweight='bold', color="#146c3a")
    ax.set_aspect('equal')
    fig.patch.set_alpha(0)
    st.pyplot(fig, use_container_width=True)
with legend_col:
    st.write("")
    st.markdown(f"🟢 **Protein:** {protein_kcal:.0f} kcal ({protein_pct:.1f}%)")
    st.progress(min(protein_pct / 100, 1.0))
    st.markdown(f"🟠 **Fats:** {fats_kcal:.0f} kcal ({fats_pct:.1f}%)")
    st.progress(min(fats_pct / 100, 1.0))
    st.markdown(f"🔵 **Carbs:** {carbs_kcal:.0f} kcal ({carbs_pct:.1f}%)")
    st.progress(min(carbs_pct / 100, 1.0))
st.markdown('</div>', unsafe_allow_html=True)

# --- Per meal + goal timeline ---
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🍴 Per-Meal Breakdown & Goal Timeline</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown(f'<div class="badge-card"><div class="label">Calories / Meal ({meals} meals)</div><div class="value">{calories_per_meal:.0f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="badge-card"><div class="label">Protein / Meal</div><div class="value">{protein_per_meal:.1f} g</div></div>', unsafe_allow_html=True)

st.write("")
if abs_diff < 0.1:
    st.success("🎉 You're already at your goal weight — this plan is set up to help you **maintain** it.")
else:
    verb = "lose" if weight_diff > 0 else "gain"
    st.info(f"📅 At a safe rate of 0.5–1 kg/week, it will take roughly **{min_weeks:.0f}–{max_weeks:.0f} weeks** to {verb} **{abs_diff:.1f} kg** and reach {goal_w:.1f} kg.")
st.markdown('</div>', unsafe_allow_html=True)

# --- Tips ---
tips = []
if category == "Underweight":
    tips.append("Focus on nutrient-dense, calorie-rich foods (nuts, dairy, whole grains) alongside strength training to build healthy mass.")
elif category == "Normal weight":
    tips.append("You're in a healthy BMI range — prioritize consistency, balanced meals, and regular activity to maintain it.")
elif category == "Overweight":
    tips.append("A moderate calorie deficit combined with regular activity (150+ min/week) is a sustainable way to move toward your goal.")
else:
    tips.append("Consider consulting a healthcare provider to design a safe, structured, and supervised weight-loss plan.")
tips.append(f"Spread your {protein:.0f}g protein target evenly across {meals} meals to support muscle repair and satiety.")
tips.append(f"Sip water throughout the day to reach your {water/1000:.2f} L target — more if you exercise or live somewhere hot.")
tips.append("Prioritize fibre-rich vegetables, fruits, and whole grains to hit your fibre target and support digestion.")

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">💡 Personalized Tips</div>', unsafe_allow_html=True)
for t in tips:
    st.markdown(f"- {t}")
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# PDF REPORT GENERATION
# =====================================================================
def build_pdf_report():
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.6 * cm, bottomMargin=1.6 * cm,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleGreen", parent=styles["Title"],
        textColor=colors.HexColor("#146c3a"), fontSize=24, alignment=TA_CENTER, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        textColor=colors.HexColor("#4a6a58"), fontSize=11, alignment=TA_CENTER, spaceAfter=14
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        textColor=colors.HexColor("#1f8a4c"), fontSize=14, spaceBefore=14, spaceAfter=8
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=10.2, leading=15, alignment=TA_LEFT
    )
    note_style = ParagraphStyle(
        "Note", parent=styles["Normal"], fontSize=8.5, textColor=colors.HexColor("#7a7a7a"),
        alignment=TA_CENTER
    )

    story = []
    story.append(Paragraph(f"🥗 {APP_NAME} — Diet & Nutrition Report", title_style))
    story.append(Paragraph(APP_TAGLINE, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d7f0e0")))
    story.append(Spacer(1, 10))

    gen_date = datetime.now().strftime("%d %B %Y, %I:%M %p")
    who = name.strip() if name.strip() else "N/A"
    story.append(Paragraph(f"<b>Prepared for:</b> {who} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date:</b> {gen_date}", body_style))
    story.append(Spacer(1, 6))

    # --- Personal details table ---
    story.append(Paragraph("1. Personal Details", section_style))
    personal_data = [
        ["Gender", gender, "Age", f"{age} yrs"],
        ["Current Weight", f"{current_w:.1f} kg", "Goal Weight", f"{goal_w:.1f} kg"],
        ["Height", f"{height:.2f} m", "Activity Level", activity_label],
        ["Meals / Day", str(meals), "Goal Type", goal_type],
    ]
    t = Table(personal_data, colWidths=[3.7 * cm, 4.3 * cm, 3.7 * cm, 4.3 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eaf6ee")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#eaf6ee")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d7f0e0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    # --- Body metrics ---
    story.append(Paragraph("2. Body Metrics", section_style))
    body_data = [
        ["Metric", "Value"],
        ["BMI", f"{bmi:.2f} ({category})"],
        ["Healthy Weight Range", f"{ideal_weight_low:.1f} – {ideal_weight_high:.1f} kg"],
        ["BMR (Basal Metabolic Rate)", f"{bmr:.0f} kcal/day"],
        ["TDEE (Maintenance Calories)", f"{tdee:.0f} kcal/day"],
    ]
    t2 = Table(body_data, colWidths=[8 * cm, 8 * cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f8a4c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d7f0e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6fdf8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)

    # --- Daily targets ---
    story.append(Paragraph(f"3. Daily Nutrition Targets — {goal_type}", section_style))
    nut_data = [
        ["Nutrient", "Daily Target", "% of Calories"],
        ["Calories", f"{kcal:.0f} kcal", "100%"],
        ["Protein", f"{protein:.1f} g", f"{protein_pct:.1f}%"],
        ["Fats", f"{fats:.1f} g", f"{fats_pct:.1f}%"],
        ["Carbohydrates", f"{carbs:.1f} g", f"{carbs_pct:.1f}%"],
        ["Fibre", f"{fibres:.1f} g", "—"],
        ["Water", f"{water/1000:.2f} L", "—"],
    ]
    t3 = Table(nut_data, colWidths=[6 * cm, 5 * cm, 5 * cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f8a4c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d7f0e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6fdf8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t3)

    # --- Per meal ---
    story.append(Paragraph("4. Per-Meal Breakdown", section_style))
    story.append(Paragraph(
        f"Split across <b>{meals} meals/day</b>, aim for approximately "
        f"<b>{calories_per_meal:.0f} kcal</b> and <b>{protein_per_meal:.1f} g protein</b> per meal.",
        body_style
    ))

    # --- Goal timeline ---
    story.append(Paragraph("5. Goal Timeline", section_style))
    if abs_diff < 0.1:
        timeline_text = "You are already at your goal weight. This plan is calibrated for healthy maintenance."
    else:
        verb = "losing" if weight_diff > 0 else "gaining"
        timeline_text = (
            f"Going from <b>{current_w:.1f} kg</b> to <b>{goal_w:.1f} kg</b> means {verb} "
            f"<b>{abs_diff:.1f} kg</b>. At a safe, sustainable rate of 0.5–1 kg per week, this is "
            f"estimated to take approximately <b>{min_weeks:.0f}–{max_weeks:.0f} weeks</b>."
        )
    story.append(Paragraph(timeline_text, body_style))

    # --- Tips ---
    story.append(Paragraph("6. Personalized Recommendations", section_style))
    for tip in tips:
        story.append(Paragraph(f"• {tip}", body_style))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d7f0e0")))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Disclaimer: This report is generated using standard estimation formulas (Mifflin-St Jeor equation "
        "and general nutrition guidelines) for informational purposes only. It is not a substitute for advice "
        "from a registered dietitian or physician. Consult a healthcare professional before starting any new "
        "diet or exercise program, especially if you have existing health conditions.",
        note_style
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Generated by {APP_NAME} · {APP_TAGLINE}", note_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

pdf_buffer = build_pdf_report()
file_label = (name.strip().replace(" ", "_") + "_") if name.strip() else ""
pdf_filename = f"{file_label}{APP_NAME.lower()}_diet_report.pdf"

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📥 Download Your Full Report</div>', unsafe_allow_html=True)
st.write("Get a complete, print-ready PDF with all your metrics, targets, and recommendations.")
st.download_button(
    label="⬇️ Download PDF Report",
    data=pdf_buffer,
    file_name=pdf_filename,
    mime="application/pdf",
    use_container_width=True
)
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# FOOTER
# =====================================================================
st.markdown(f"""
<div class="footer-note">🥗 {APP_NAME} — {APP_TAGLINE}<br>Made by Eshwar Miyyapuram</div>
""", unsafe_allow_html=True)
