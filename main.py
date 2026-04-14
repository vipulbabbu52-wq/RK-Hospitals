import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- DATABASE PERSISTENCE ---
DB_FILE = 'rk_hospital_data.csv'

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['Name', 'Age', 'Room', 'Symptoms', 'Doctor', 'Designation', 'Tests', 'Diagnosis', 'Notes', 'Bill', 'Status'])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- APP CONFIG ---
st.set_page_config(page_title="RK HOSPITALS", page_icon="🏥", layout="wide")

# Professional Print Styling
st.markdown("""
    <style>
    .report-box { 
        border: 2px solid #000; padding: 30px; background-color: white; color: black; 
        font-family: 'Times New Roman', serif; line-height: 1.5;
    }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏥 RK HOSPITALS | Staff Login")
    user = st.text_input("Username")
    pin = st.text_input("Security PIN", type="password")
    if st.button("Login"):
        if user == "admin" and pin == "rk123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# --- CLINICAL ASSETS (INDIAN CONTEXT) ---
DOCTORS = {
    "Dr. Rathi": "Chief Doctor",
    "Dr. Vikram Sarabhai": "Senior Consultant",
    "Dr. Anjali Menon": "Senior Consultant",
    "Dr. Rajesh Khanna": "Senior Intern",
    "Dr. Priya Sharma": "Senior Intern",
    "Dr. Amitav Ghosh": "Junior Intern",
    "Dr. Sunita Williams": "Junior Intern"
}

SYMPTOMS_LIST = ["High Fever", "Persistent Cough", "Chest Pain", "Abdominal Pain", "Joint Pain", "Headache", "Vomiting", "Breathlessness", "Skin Rash", "Weakness"]
TESTS_LIST = {"CBC": 500, "X-Ray Chest": 1200, "ECG": 800, "MRI Brain": 9000, "CT Scan": 5000, "Liver Function Test": 1800, "Lipid Profile": 1500, "Dengue NS1": 1200, "Widal Test": 600}
DIAGNOSIS_LIST = ["Dengue Fever", "Typhoid", "Hypertension", "Type 2 Diabetes", "Viral Pneumonia", "Acute Gastroenteritis", "Malaria", "Urinary Tract Infection"]

# --- APP NAVIGATION ---
df = load_data()
menu = st.sidebar.radio("Navigation", ["Ward Overview", "New Admission", "Update Clinical Chart", "Discharge & Billing", "Discharge Archive"])

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()

# --- 1. WARD OVERVIEW ---
if menu == "Ward Overview":
    st.header("📍 Current In-Patients")
    active = df[df['Status'] == 'Admitted']
    if active.empty:
        st.info("The wards are currently empty. No patient names pre-loaded.")
    else:
        st.table(active[['Name', 'Age', 'Room', 'Doctor', 'Designation', 'Diagnosis', 'Bill']])

# --- 2. NEW ADMISSION ---
elif menu == "New Admission":
    st.header("📋 Patient Intake Form")
    with st.form("admission_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", 0, 110)
            room = st.text_input("Room/Ward No.")
        with col2:
            doc_choice = st.selectbox("Assign Doctor", list(DOCTORS.keys()))
            symptoms = st.multiselect("Presenting Symptoms", SYMPTOMS_LIST)
        
        notes = st.text_area("Initial Physician Notes")
        
        if st.form_submit_button("Confirm Admission"):
            if name and room:
                new_entry = pd.DataFrame([[
                    name, age, room, ", ".join(symptoms), doc_choice, DOCTORS[doc_choice], "", "Awaiting Examination", notes, 1500.0, "Admitted"
                ]], columns=df.columns)
                df = pd.concat([df, new_entry], ignore_index=True)
                save_data(df)
                st.success(f"Patient {name} admitted successfully under {doc_choice}.")

# --- 3. CLINICAL CHART ---
elif menu == "Update Clinical Chart":
    st.header("🩺 Charting & Lab Updates")
    active_names = df[df['Status'] == 'Admitted']['Name'].tolist()
    if not active_names:
        st.warning("No patients currently in wards.")
    else:
        target = st.selectbox("Select Patient", active_names)
        idx = df[df['Name'] == target].index[0]
        
        col1, col2 = st.columns(2)
        with col1:
            tests = st.multiselect("Select Lab Tests Done", list(TESTS_LIST.keys()))
            diag = st.selectbox("Final Diagnosis", DIAGNOSIS_LIST)
        with col2:
            add_notes = st.text_area("Add Daily Round Notes")
            
        if st.button("Update Record"):
            test_total = sum([TESTS_LIST[t] for t in tests])
            df.at[idx, 'Tests'] = (str(df.at[idx, 'Tests']) + ", " + ", ".join(tests)).strip(", ")
            df.at[idx, 'Diagnosis'] = diag
            df.at[idx, 'Notes'] = (str(df.at[idx, 'Notes']) + " | " + add_notes).strip(" | ")
            df.at[idx, 'Bill'] += test_total
            save_data(df)
            st.success("Record updated and saved.")

# --- 4. DISCHARGE & BILLING ---
elif menu == "Discharge & Billing":
    st.header("💸 Settlement & Final Print")
    active_names = df[df['Status'] == 'Admitted']['Name'].tolist()
    if not active_names:
        st.info("No patients pending discharge.")
    else:
        target = st.selectbox("Select for Discharge", active_names)
        p = df[df['Name'] == target].iloc[0]
        
        st.markdown(f"""
            <div class="report-box">
                <h1 style="text-align:center; margin:0;">RK HOSPITALS</h1>
                <p style="text-align:center; margin-top:0;">Advanced Healthcare Services, India</p>
                <hr style="border:1px solid black;">
                <h3 style="text-align:center;">OFFICIAL DISCHARGE SUMMARY</h3>
                <p><b>PATIENT NAME:</b> {p['Name']} &nbsp;&nbsp;&nbsp;&nbsp; <b>AGE:</b> {p['Age']}</p>
                <p><b>ATTENDING DOCTOR:</b> {p['Doctor']} ({p['Designation']})</p>
                <hr>
                <p><b>CHIEF COMPLAINTS:</b> {p['Symptoms']}</p>
                <p><b>FINAL DIAGNOSIS:</b> {p['Diagnosis']}</p>
                <p><b>LAB INVESTIGATIONS:</b> {p['Tests'] if p['Tests'] else 'N/A'}</p>
                <p><b>CLINICAL COURSE:</b> {p['Notes']}</p>
                <hr>
                <h2 style="text-align:right;">TOTAL PAYABLE: ₹{p['Bill']:,.2f}</h2>
                <br><br><br>
                <table style="width:100%;">
                    <tr>
                        <td style="text-align:left;">____________________<br>Patient Signature</td>
                        <td style="text-align:right;">____________________<br>Authorized Signatory</td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Finalize Payment & Discharge"):
            df.loc[df['Name'] == target, 'Status'] = 'Discharged'
            save_data(df)
            st.balloons()
            st.success("Patient discharged and archive updated.")

# --- 5. DISCHARGE ARCHIVE ---
elif menu == "Discharge Archive":
    st.header("📜 Past Discharge List")
    past = df[df['Status'] == 'Discharged']
    if past.empty:
        st.text("No archived records found.")
    else:
        st.table(past[['Name', 'Doctor', 'Designation', 'Diagnosis', 'Bill']])