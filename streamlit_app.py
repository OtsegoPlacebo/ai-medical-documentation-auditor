
import streamlit as st
import pandas as pd
from datetime import datetime
from io import StringIO

st.set_page_config(
    page_title="AI Medical Documentation Auditor",
    page_icon="🩺",
    layout="wide"
)

# -----------------------------
# Project Notes
# -----------------------------
DISCLAIMER = """
Educational HIM portfolio project only. This tool does not provide final medical coding, billing,
legal, compliance, or clinical advice. It is designed to demonstrate AI-assisted documentation
review concepts for Health Information Management.
"""

SAMPLE_CASES = {
    "Chest Pain / EKG": {
        "note": "Patient presents with chest pain and shortness of breath. EKG performed. Aspirin administered. Patient discharged home in stable condition.",
        "diagnosis": "Chest Pain",
        "procedure": "EKG"
    },
    "Diabetes Follow-Up": {
        "note": "Patient here for diabetes follow-up. Reports taking medication. Labs reviewed. Continue current treatment. Follow up in 3 months.",
        "diagnosis": "Diabetes",
        "procedure": "Office Visit"
    },
    "Minor Laceration Repair": {
        "note": "Patient cut finger while cooking. Wound cleaned and sutures placed. Patient tolerated procedure well.",
        "diagnosis": "Finger laceration",
        "procedure": "Laceration repair"
    },
    "UTI Symptoms": {
        "note": "Patient reports burning with urination for 3 days. Urinalysis positive for leukocytes. Antibiotics prescribed. Patient advised to return if symptoms worsen.",
        "diagnosis": "Urinary tract infection",
        "procedure": "Urinalysis"
    },
    "Hypertension Visit": {
        "note": "Patient seen for hypertension. Blood pressure elevated today. Medication adjusted due to uncontrolled readings. Patient instructed to monitor blood pressure at home and follow up in 4 weeks.",
        "diagnosis": "Hypertension",
        "procedure": "Office Visit"
    }
}

CHECKS = {
    "Chief complaint / reason for visit": ["chief complaint", "presents", "reports", "seen for", "here for"],
    "Symptom duration / onset": ["duration", "for", "hours", "days", "weeks", "started", "onset"],
    "Symptom severity": ["severity", "mild", "moderate", "severe", "pain scale", "10/10", "rated"],
    "Relevant history or risk factors": ["history", "risk", "smoker", "diabetes", "hypertension", "family history", "medication"],
    "Objective findings / test results": ["normal", "abnormal", "findings", "results", "reviewed", "positive", "negative", "blood pressure", "urinalysis", "ekg"],
    "Assessment and plan": ["assessment", "plan", "continue", "prescribed", "adjusted", "treatment", "antibiotics"],
    "Medical decision-making rationale": ["because", "due to", "rationale", "decision", "uncontrolled", "worsen", "stable"],
    "Procedure support / interpretation": ["interpreted", "repair", "suturing", "sutures", "performed", "tolerated", "administered"],
    "Discharge or follow-up instructions": ["follow up", "return", "pcp", "primary care", "instructions", "monitor", "advised"],
    "Patient response / outcome": ["tolerated", "stable", "improved", "worsen", "discharged"]
}

def evaluate_documentation(note, diagnosis, procedure):
    note_lower = note.lower()

    present = []
    missing = []

    for element, keywords in CHECKS.items():
        if any(keyword in note_lower for keyword in keywords):
            present.append(element)
        else:
            missing.append(element)

    score = max(0, 100 - (len(missing) * 6))

    if score >= 90:
        risk = "Low Risk"
    elif score >= 70:
        risk = "Moderate Risk"
    else:
        risk = "High Risk"

    coding_concerns = []
    compliance_concerns = []
    provider_queries = []
    improvement_suggestions = []

    if not diagnosis.strip():
        coding_concerns.append("Diagnosis is missing.")
    elif len(diagnosis.split()) <= 2:
        coding_concerns.append("Diagnosis may need greater specificity to support accurate code assignment.")

    if procedure.strip() and "Procedure support / interpretation" in missing:
        coding_concerns.append("Procedure is listed, but the note may not fully support procedure performance or interpretation.")

    if "Symptom duration / onset" in missing:
        provider_queries.append("Please clarify symptom onset or duration.")
        improvement_suggestions.append("Add when symptoms began and how long they have been present.")

    if "Symptom severity" in missing:
        provider_queries.append("Please clarify symptom severity when clinically relevant.")
        improvement_suggestions.append("Include severity, pain scale, or description of symptom intensity.")

    if "Objective findings / test results" in missing:
        provider_queries.append("Please document relevant objective findings, test results, or interpretation.")
        improvement_suggestions.append("Include diagnostic findings that support the diagnosis and treatment plan.")

    if "Medical decision-making rationale" in missing:
        compliance_concerns.append("Medical decision-making may not be fully supported.")
        provider_queries.append("Please clarify the rationale for the assessment, treatment, discharge, or follow-up plan.")
        improvement_suggestions.append("Document why the selected treatment or disposition was appropriate.")

    if "Discharge or follow-up instructions" in missing:
        compliance_concerns.append("Follow-up or discharge instructions may be incomplete.")
        provider_queries.append("Please document follow-up instructions, return precautions, or patient education.")
        improvement_suggestions.append("Add patient instructions, follow-up timing, and return precautions.")

    if not coding_concerns:
        coding_concerns.append("No major coding support concern detected by the rule-based review.")
    if not compliance_concerns:
        compliance_concerns.append("No major compliance concern detected by the rule-based review.")
    if not provider_queries:
        provider_queries.append("No provider query suggested based on current rule checks.")
    if not improvement_suggestions:
        improvement_suggestions.append("Documentation appears generally complete based on current rule checks.")

    return {
        "audit_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "score": score,
        "risk": risk,
        "present": present,
        "missing": missing,
        "coding_concerns": coding_concerns,
        "compliance_concerns": compliance_concerns,
        "provider_queries": provider_queries,
        "improvement_suggestions": improvement_suggestions
    }

def create_report_text(note, diagnosis, procedure, result):
    lines = []
    lines.append("AI MEDICAL DOCUMENTATION AUDITOR REPORT")
    lines.append("=" * 52)
    lines.append(f"Audit Date: {result['audit_date']}")
    lines.append(f"Diagnosis: {diagnosis}")
    lines.append(f"Procedure: {procedure}")
    lines.append(f"Documentation Quality Score: {result['score']}/100")
    lines.append(f"Risk Level: {result['risk']}")
    lines.append("")
    lines.append("PATIENT NOTE")
    lines.append("-" * 52)
    lines.append(note)
    lines.append("")
    lines.append("PRESENT DOCUMENTATION ELEMENTS")
    lines.append("-" * 52)
    lines.extend([f"- {x}" for x in result["present"]] or ["- None detected"])
    lines.append("")
    lines.append("MISSING DOCUMENTATION ELEMENTS")
    lines.append("-" * 52)
    lines.extend([f"- {x}" for x in result["missing"]] or ["- None detected"])
    lines.append("")
    lines.append("CODING SUPPORT CONCERNS")
    lines.append("-" * 52)
    lines.extend([f"- {x}" for x in result["coding_concerns"]])
    lines.append("")
    lines.append("COMPLIANCE CONCERNS")
    lines.append("-" * 52)
    lines.extend([f"- {x}" for x in result["compliance_concerns"]])
    lines.append("")
    lines.append("SUGGESTED PROVIDER QUERIES")
    lines.append("-" * 52)
    lines.extend([f"- {x}" for x in result["provider_queries"]])
    lines.append("")
    lines.append("DOCUMENTATION IMPROVEMENT SUGGESTIONS")
    lines.append("-" * 52)
    lines.extend([f"- {x}" for x in result["improvement_suggestions"]])
    lines.append("")
    lines.append("DISCLAIMER")
    lines.append("-" * 52)
    lines.append(DISCLAIMER.strip())
    return "\n".join(lines)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Project Menu")
page = st.sidebar.radio(
    "Choose a section",
    ["Run Audit", "Sample Cases", "Scoring Rubric", "Portfolio Summary"]
)

st.sidebar.markdown("---")
st.sidebar.info("Created by Janyce Viero | HIM + AI Portfolio Project")

# -----------------------------
# Main UI
# -----------------------------
st.title("🩺 AI Medical Documentation Auditor")
st.caption("Healthcare documentation quality review using AI-inspired rule-based auditing")

st.warning(DISCLAIMER)

if page == "Run Audit":
    st.header("Run Documentation Audit")

    selected_case = st.selectbox(
        "Load a sample case or choose blank input",
        ["Blank Input"] + list(SAMPLE_CASES.keys())
    )

    if selected_case != "Blank Input":
        default_note = SAMPLE_CASES[selected_case]["note"]
        default_diagnosis = SAMPLE_CASES[selected_case]["diagnosis"]
        default_procedure = SAMPLE_CASES[selected_case]["procedure"]
    else:
        default_note = ""
        default_diagnosis = ""
        default_procedure = ""

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Clinical Documentation Input")
        patient_note = st.text_area("Patient Note", value=default_note, height=240)
        diagnosis = st.text_input("Diagnosis", value=default_diagnosis)
        procedure = st.text_input("Procedure", value=default_procedure)

        run = st.button("Run Audit", type="primary")

    with col2:
        st.subheader("Audit Dashboard")

        if run:
            result = evaluate_documentation(patient_note, diagnosis, procedure)

            m1, m2, m3 = st.columns(3)
            m1.metric("Quality Score", f"{result['score']}/100")
            m2.metric("Risk Level", result["risk"])
            m3.metric("Missing Elements", len(result["missing"]))

            st.progress(result["score"] / 100)

            st.markdown("### Documentation Elements")
            element_df = pd.DataFrame({
                "Element": result["present"] + result["missing"],
                "Status": ["Present"] * len(result["present"]) + ["Missing"] * len(result["missing"])
            })
            st.dataframe(element_df, use_container_width=True, hide_index=True)

            st.markdown("### Coding Support Concerns")
            for item in result["coding_concerns"]:
                st.write(f"- {item}")

            st.markdown("### Compliance Concerns")
            for item in result["compliance_concerns"]:
                st.write(f"- {item}")

            st.markdown("### Suggested Provider Queries")
            for item in result["provider_queries"]:
                st.info(item)

            st.markdown("### Improvement Suggestions")
            for item in result["improvement_suggestions"]:
                st.success(item)

            report_text = create_report_text(patient_note, diagnosis, procedure, result)
            st.download_button(
                label="Download Audit Report",
                data=report_text,
                file_name="documentation_audit_report.txt",
                mime="text/plain"
            )
        else:
            st.info("Enter documentation and click Run Audit.")

elif page == "Sample Cases":
    st.header("Sample Case Library")
    st.write("These sample cases are fictional and designed for HIM portfolio demonstration.")

    rows = []
    for name, data in SAMPLE_CASES.items():
        result = evaluate_documentation(data["note"], data["diagnosis"], data["procedure"])
        rows.append({
            "Case": name,
            "Diagnosis": data["diagnosis"],
            "Procedure": data["procedure"],
            "Score": result["score"],
            "Risk": result["risk"],
            "Missing Elements": len(result["missing"])
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("### Case Details")
    case_name = st.selectbox("Select a case", list(SAMPLE_CASES.keys()))
    st.write("**Patient Note:**")
    st.write(SAMPLE_CASES[case_name]["note"])
    st.write("**Diagnosis:**", SAMPLE_CASES[case_name]["diagnosis"])
    st.write("**Procedure:**", SAMPLE_CASES[case_name]["procedure"])

elif page == "Scoring Rubric":
    st.header("Scoring Rubric")
    st.write("The score begins at 100. Each missing documentation element subtracts 6 points.")

    rubric = pd.DataFrame({
        "Score Range": ["90–100", "70–89", "0–69"],
        "Risk Level": ["Low Risk", "Moderate Risk", "High Risk"],
        "Meaning": [
            "Documentation is generally complete based on selected review elements.",
            "Documentation has gaps that may require clarification or improvement.",
            "Documentation has significant gaps that may impact coding support or compliance review."
        ]
    })
    st.dataframe(rubric, use_container_width=True, hide_index=True)

    st.markdown("### Review Elements")
    st.write("The auditor checks for:")
    for element in CHECKS.keys():
        st.write(f"- {element}")

elif page == "Portfolio Summary":
    st.header("Portfolio Summary")

    st.markdown("""
    ### Project Name
    **AI Medical Documentation Auditor**

    ### Project Description
    Developed an AI-assisted healthcare documentation review tool that evaluates sample clinical notes for documentation completeness, coding support, compliance concerns, and provider query opportunities.

    ### Problem Addressed
    Incomplete healthcare documentation can affect coding accuracy, reimbursement, compliance, continuity of care, and healthcare data quality.

    ### Tools Used
    - Python
    - Streamlit
    - Pandas
    - Health Information Management concepts
    - AI prompt and rule-based logic design

    ### Skills Demonstrated
    - Health Information Management
    - Documentation integrity
    - Clinical Documentation Improvement awareness
    - Coding support review
    - Compliance awareness
    - Quality assurance
    - AI workflow design
    - Data analysis and dashboard presentation

    ### Professional Value
    This project demonstrates how AI-assisted tools can support HIM professionals by identifying documentation gaps and improving healthcare data quality without replacing human review.
    """)
