import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "http://localhost:8001/api"

st.set_page_config(page_title="RFQ Procurement Dashboard", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stCard {
        border-radius: 10px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🏢 Procurement RFQ")
st.sidebar.divider()

# Fetch Categories
try:
    resp = requests.get(f"{API_BASE_URL}/categories")
    categories = resp.json()
except:
    categories = ["Plumbing", "Electrical", "HVAC", "Finishing", "Structural"]

selected_category = st.sidebar.radio("Select Material Category", categories)

# State Management for workflow
if 'workflow_step' not in st.session_state:
    st.session_state.workflow_step = 'selecting' # 'selecting' or 'composing'

# Main Section
st.title(f"📦 RFQ Management - {selected_category}")

# File Upload for Materials (Fallback)
st.sidebar.divider()
st.sidebar.subheader("📤 Material Data")
uploaded_file = st.sidebar.file_uploader("Upload Extracted Materials (Excel/CSV)", type=["xlsx", "csv"])

materials_data = []
if uploaded_file:
    try:
        import numpy as np
        if uploaded_file.name.endswith('.csv'):
            df_mats = pd.read_csv(uploaded_file)
        else:
            df_mats = pd.read_excel(uploaded_file)
        
        # FIXED: Clean out-of-range float values (NaN, Inf) that cause JSON error
        df_mats = df_mats.replace([np.inf, -np.inf], 0)
        
        # Ensure we don't count completely empty rows
        df_mats = df_mats.dropna(how='all')
        df_mats = df_mats.fillna("")
        
        # Standardize columns for API compatibility
        materials_data = df_mats.to_dict(orient="records")
        st.sidebar.success(f"Loaded {len(materials_data)} materials")
        
        # Capture raw file bytes for original attachment
        import base64
        uploaded_file.seek(0)
        st.session_state.original_file_base64 = base64.b64encode(uploaded_file.read()).decode()
        st.session_state.original_filename = uploaded_file.name

        # Allow user to "open" and see the data
        with st.sidebar.expander("👁️ View Uploaded Materials"):
            st.dataframe(df_mats, hide_index=True)
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")

if st.session_state.workflow_step == 'selecting':
    st.write(f"Manage vendors and send RFQs for **{selected_category}** materials.")
    
    # Fetch Vendors for Category
    vendors_resp = requests.get(f"{API_BASE_URL}/vendors", params={"category": selected_category})
    if vendors_resp.status_code == 200:
        vendors_data = vendors_resp.json()
        if not vendors_data:
            st.info(f"No vendors found for category: {selected_category}")
        else:
            df_vendors = pd.DataFrame(vendors_data)
            
            st.subheader("Select Vendors")
            df_vendors['Select'] = False
            
            selected_rows = st.data_editor(
                df_vendors[['Select', 'name', 'email', 'city', 'rating']],
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select", default=False),
                    "rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐")
                },
                disabled=["name", "email", "city", "rating"],
                key="vendor_selector",
                hide_index=True,
                use_container_width=True
            )

            # Get actual selected vendor IDs and Names
            selected_indices = selected_rows[selected_rows['Select']].index
            st.session_state.selected_vendor_ids = df_vendors.iloc[selected_indices]['id'].tolist()
            st.session_state.selected_vendor_names = df_vendors.iloc[selected_indices]['name'].tolist()

            st.divider()
            
            if st.button("📝 PROCEED TO COMPOSE EMAIL", type="primary"):
                if not st.session_state.selected_vendor_ids:
                    st.warning("Please select at least one vendor.")
                elif not materials_data:
                    st.warning("Please upload a material file in the sidebar first.")
                else:
                    st.session_state.materials_to_send = materials_data
                    st.session_state.workflow_step = 'composing'
                    st.rerun()

elif st.session_state.workflow_step == 'composing':
    st.subheader("✉️ Compose RFQ Email")
    st.info(f"You are sending this to **{len(st.session_state.selected_vendor_names)} vendors**: " + ", ".join(st.session_state.selected_vendor_names))

    default_body = f"""Dear {{{{Vendor Name}}}},

We are requesting a quotation for the materials listed in the attached RFQ document.

Project: Commercial Complex A
Category: {selected_category}

Please provide your quotation including:

* Unit price
* Delivery timeline
* Payment terms

Kindly respond with your quotation at the earliest.

Best regards
Procurement Team"""

    email_body = st.text_area("Email Content", value=default_body, height=300, help="Placeholders: {{Vendor Name}}, {{Category}}, {{Project Name}}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Selection"):
            st.session_state.workflow_step = 'selecting'
            st.rerun()
    
    with col2:
        if st.button("🚀 CONFIRM & SEND RFQ", type="primary"):
            with st.spinner("Pushing emails to vendors..."):
                payload = {
                    "category": selected_category,
                    "vendor_ids": st.session_state.selected_vendor_ids,
                    "materials": st.session_state.materials_to_send,
                    "project_name": "Commercial Complex A",
                    "original_file_base64": st.session_state.get('original_file_base64'),
                    "original_filename": st.session_state.get('original_filename')
                }
                # Pass custom body as query param or include in payload (if endpoint updated)
                rfq_resp = requests.post(
                    f"{API_BASE_URL}/send-rfq", 
                    json=payload, 
                    params={"category": selected_category, "email_body": email_body}
                )
                
                if rfq_resp.status_code == 200:
                    res = rfq_resp.json()
                    st.success(f"✅ Successfully sent RFQ emails to {res['emails_sent']} vendors!")
                    if st.button("Send Another RFQ"):
                        st.session_state.workflow_step = 'selecting'
                        st.rerun()
                else:
                    st.error(f"❌ Failed to send RFQs: {rfq_resp.text}")

else:
    st.error("Could not fetch vendors from the backend.")

st.sidebar.divider()
st.sidebar.caption("v1.0 - Professional Procurement Interface")
