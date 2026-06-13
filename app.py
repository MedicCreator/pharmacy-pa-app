import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Pharmacy Prior Authorization Assistant",
    page_icon="💊",
    layout="wide"
)

st.title("💊 Pharmacy Prior Authorization Assistant")
st.caption("MVP prototype for prescription review, prior authorization, denial tracking, and appeal support.")

st.warning(
    "HIPAA Notice: This MVP is for testing only. Do NOT upload real patient PHI until the app is deployed in a HIPAA-compliant environment with BAAs, encryption, audit logs, access controls, and legal review."
)

if "cases" not in st.session_state:
    st.session_state.cases = []

def extract_medication_info(note_text):
    medications = ["Ozempic", "Mounjaro", "Wegovy", "Trulicity", "Humira", "Dupixent", "Eliquis", "Jardiance"]
    diagnoses = ["diabetes", "type 2 diabetes", "obesity", "asthma", "eczema", "atrial fibrillation", "CKD", "heart failure"]

    found_meds = [m for m in medications if m.lower() in note_text.lower()]
    found_dx = [d for d in diagnoses if d.lower() in note_text.lower()]

    dose_keywords = ["mg", "mcg", "units", "tablet", "capsule", "weekly", "daily", "twice daily", "once daily"]
    dose_lines = []
    for line in note_text.splitlines():
        if any(k in line.lower() for k in dose_keywords):
            dose_lines.append(line.strip())

    evidence_lines = []
    evidence_keywords = [
        "failed", "trial", "intolerant", "contraindicated", "diagnosis",
        "a1c", "bmi", "symptoms", "medically necessary", "requires",
        "improved", "worsened", "history", "because"
    ]
    for line in note_text.splitlines():
        if any(k in line.lower() for k in evidence_keywords):
            evidence_lines.append(line.strip())

    return {
        "medications": found_meds,
        "diagnoses": found_dx,
        "dosing": dose_lines,
        "evidence": evidence_lines
    }

def generate_pa_packet(patient_name, physician, pharmacy, medication, diagnosis, dose, evidence):
    return f"""
PRIOR AUTHORIZATION MEDICAL NECESSITY SUMMARY

Patient: {patient_name}
Prescriber: {physician}
Pharmacy: {pharmacy}
Medication Requested: {medication}
Diagnosis / Indication: {diagnosis}
Dose / Frequency: {dose}

Medical Necessity:
The requested medication is medically necessary for the patient's diagnosis/indication listed above. The clinical note supports use of this therapy based on the following documented evidence:

Supporting Evidence From Clinical Note:
{evidence}

Request:
Please approve coverage for {medication} as prescribed. Delaying therapy may negatively affect patient outcomes.
"""

def generate_appeal(patient_name, medication, diagnosis, denial_reason, evidence):
    return f"""
APPEAL LETTER FOR DENIED MEDICATION

Re: Appeal for {medication}
Patient: {patient_name}
Diagnosis / Indication: {diagnosis}

To Whom It May Concern,

We are appealing the denial of {medication}. The denial reason provided was:

"{denial_reason}"

Based on the clinical documentation, this medication is medically necessary and appropriate for this patient.

Clinical Evidence From the Note:
{evidence}

Appeal Argument:
The patient's medical record supports the diagnosis and need for treatment. The prescribed medication is clinically indicated based on the documented condition, prior treatment history, symptoms, risk factors, and/or treatment goals.

Request:
Please reconsider and approve coverage for {medication}. If additional documentation is needed, please specify the exact criteria required for approval.

Sincerely,
Prior Authorization Team
"""

tab1, tab2, tab3, tab4 = st.tabs([
    "1. New Case",
    "2. Extract Evidence",
    "3. PA / Appeal Generator",
    "4. Case Tracker"
])

with tab1:
    st.header("Create New Prior Authorization Case")

    patient_name = st.text_input("Patient Name / Initials")
    physician = st.text_input("Prescribing Physician")
    pharmacy = st.text_input("Pharmacy")
    payer = st.text_input("Insurance / PBM")
    medication = st.text_input("Medication Requested")
    diagnosis = st.text_input("Diagnosis / Indication")
    dose = st.text_input("Dose and Frequency")

    note_text = st.text_area("Paste Clinical Note Here", height=250)

    if st.button("Save Case"):
        case = {
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "patient": patient_name,
            "physician": physician,
            "pharmacy": pharmacy,
            "payer": payer,
            "medication": medication,
            "diagnosis": diagnosis,
            "dose": dose,
            "note": note_text,
            "status": "Draft"
        }
        st.session_state.cases.append(case)
        st.success("Case saved.")

with tab2:
    st.header("Extract Medication, Diagnosis, Dose, and Supporting Evidence")

    note_for_extraction = st.text_area("Paste note for extraction", height=300, key="extract_note")

    if st.button("Extract From Note"):
        extracted = extract_medication_info(note_for_extraction)

        st.subheader("Possible Medications")
        st.write(extracted["medications"] or "No common medication detected.")

        st.subheader("Possible Diagnoses / Indications")
        st.write(extracted["diagnoses"] or "No common diagnosis detected.")

        st.subheader("Possible Dosing Lines")
        st.write(extracted["dosing"] or "No dosing lines detected.")

        st.subheader("Highlighted Evidence for Medical Necessity")
        if extracted["evidence"]:
            for line in extracted["evidence"]:
                st.markdown(f"- **{line}**")
        else:
            st.write("No strong evidence lines detected.")

with tab3:
    st.header("Generate Prior Authorization Packet or Appeal")

    patient_name2 = st.text_input("Patient", key="pa_patient")
    physician2 = st.text_input("Physician", key="pa_physician")
    pharmacy2 = st.text_input("Pharmacy", key="pa_pharmacy")
    medication2 = st.text_input("Medication", key="pa_med")
    diagnosis2 = st.text_input("Diagnosis / Indication", key="pa_dx")
    dose2 = st.text_input("Dose / Frequency", key="pa_dose")
    evidence2 = st.text_area("Evidence From Note", height=180, key="pa_evidence")

    if st.button("Generate PA Packet"):
        packet = generate_pa_packet(
            patient_name2,
            physician2,
            pharmacy2,
            medication2,
            diagnosis2,
            dose2,
            evidence2
        )
        st.text_area("Prior Authorization Packet", packet, height=350)

    st.divider()

    denial_reason = st.text_area("Denial Reason", height=120)

    if st.button("Generate Appeal Letter"):
        appeal = generate_appeal(
            patient_name2,
            medication2,
            diagnosis2,
            denial_reason,
            evidence2
        )
        st.text_area("Appeal Letter", appeal, height=400)

with tab4:
    st.header("Case Tracker")

    if st.session_state.cases:
        df = pd.DataFrame(st.session_state.cases)
        st.dataframe(df[[
            "created_at",
            "patient",
            "physician",
            "pharmacy",
            "payer",
            "medication",
            "diagnosis",
            "dose",
            "status"
        ]])
    else:
        st.info("No cases saved yet.")

    st.subheader("Manual Status Update")
    case_index = st.number_input("Case Number", min_value=0, step=1)
    new_status = st.selectbox(
        "Status",
        ["Draft", "Submitted", "Pending", "Approved", "Denied", "Appeal Submitted"]
    )

    if st.button("Update Status"):
        if 0 <= case_index < len(st.session_state.cases):
            st.session_state.cases[case_index]["status"] = new_status
            st.success("Status updated.")
        else:
            st.error("Invalid case number.")
