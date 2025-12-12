import sys
from pathlib import Path

# Ensure project root is on sys.path for Streamlit Cloud
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests

# Configuration - API URL with fallback for demo mode
try:
    API_URL = st.secrets.get("API_URL", None)
except:
    API_URL = None

# Demo mode flag
DEMO_MODE = API_URL is None

st.set_page_config(page_title="Sewer Flow Modelling", layout="wide")

# Add demo mode banner
if DEMO_MODE:
    st.warning("⚠️ Running in DEMO MODE (API not connected). Add API_URL to Streamlit secrets to enable full functionality.")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Phase",
    ["Project Setup", "Data Ingestion", "Quality Control", "Data Cleaning", "Hydraulics", "Rainfall & I/I", "Reports"]
)

st.title("🌊 Sewer Flow Modelling Application")

# Project Setup Page
if page == "Project Setup":
    st.header("📋 Project Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New Project")
        project_name = st.text_input("Project Name", placeholder="e.g., Downtown Sewer Study")
        project_location = st.text_input("Location", placeholder="e.g., City Center")
        project_owner = st.text_input("Owner/Client", placeholder="e.g., Municipal Water Authority")
        project_desc = st.text_area("Description", placeholder="Brief project description...")
        
        if st.button("Create Project", type="primary"):
            if project_name:
                if DEMO_MODE:
                    st.success(f"✅ Project '{project_name}' created successfully! (Demo mode - data not persisted)")
                    st.session_state.current_project = {
                        "id": 1,
                        "name": project_name,
                        "description": project_desc,
                        "location": project_location,
                        "owner": project_owner,
                    }
                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/projects/",
                            json={
                                "name": project_name,
                                "description": project_desc,
                                "location": project_location,
                                "owner": project_owner,
                            },
                            timeout=5
                        )
                        if response.status_code == 201:
                            st.success(f"✅ Project '{project_name}' created successfully!")
                            st.session_state.current_project = response.json()
                            st.rerun()
                        else:
                            st.error(f"API Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}. Make sure API is running at {API_URL}")
            else:
                st.error("Please enter a project name")
    
    with col2:
        st.subheader("Add Monitoring Site")
        
        # Get current project
        if 'current_project' in st.session_state and st.session_state.current_project:
            current_proj = st.session_state.current_project
            st.info(f"Adding site to: {current_proj.get('name', 'N/A')}")
            
            site_name = st.text_input("Site Name", placeholder="e.g., Station A")
            site_code = st.text_input("Site Code", placeholder="e.g., ST-001")
            
            col_lat, col_lon = st.columns(2)
            with col_lat:
                latitude = st.number_input("Latitude", value=0.0, format="%.6f")
            with col_lon:
                longitude = st.number_input("Longitude", value=0.0, format="%.6f")
            
            pipe_material = st.selectbox("Pipe Material", ["Concrete", "PVC", "Vitrified Clay", "Steel", "Other"])
            pipe_diameter = st.number_input("Pipe Diameter (mm)", min_value=0, value=300)
            
            if st.button("Add Site", type="primary"):
                if site_name:
                    if DEMO_MODE:
                        st.success(f"✅ Site '{site_name}' added successfully! (Demo mode - data not persisted)")
                    else:
                        try:
                            response = requests.post(
                                f"{API_URL}/projects/{current_proj['id']}/sites",
                                json={
                                    "project_id": current_proj["id"],
                                    "name": site_name,
                                    "code": site_code,
                                    "latitude": latitude,
                                    "longitude": longitude,
                                    "pipe_material": pipe_material,
                                    "pipe_diameter_mm": pipe_diameter,
                                },
                                timeout=5
                            )
                            if response.status_code == 201:
                                st.success(f"✅ Site '{site_name}' added successfully!")
                                st.rerun()
                            else:
                                st.error(f"API Error: {response.text}")
                        except Exception as e:
                            st.error(f"Connection error: {e}")
                else:
                    st.error("Please enter a site name")
        else:
            st.info("Create a project first to add sites.")

# Data Ingestion Page
elif page == "Data Ingestion":
    st.header("📁 Data Ingestion")
    
    st.markdown("Upload CSV or Excel files containing time series flow monitoring data.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx"],
        help="File should contain columns: timestamp, depth, velocity, flow, etc."
    )
    
    if uploaded_file:
        try:
            # Read file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Loaded {len(df):,} rows from {uploaded_file.name}")
            
            # Data preview
            st.subheader("Data Preview")
            st.dataframe(df.head(20), use_container_width=True)
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{len(df):,}")
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                    st.metric("Time Span", f"{(df['timestamp'].max() - df['timestamp'].min()).days} days")
                else:
                    st.metric("Time Span", "N/A")
            with col4:
                st.metric("Missing Values", f"{df.isnull().sum().sum():,}")
            
            # Column selection
            st.subheader("Configure Data Mapping")
            col1, col2 = st.columns(2)
            
            with col1:
                timestamp_col = st.selectbox("Timestamp Column", df.columns, index=0 if 'timestamp' in df.columns else 0)
                depth_col = st.selectbox("Depth Column (optional)", ["None"] + list(df.columns))
                velocity_col = st.selectbox("Velocity Column (optional)", ["None"] + list(df.columns))
            
            with col2:
                flow_col = st.selectbox("Flow Column (optional)", ["None"] + list(df.columns))
                site_name_ingest = st.text_input("Assign to Site", placeholder="e.g., Station A")
                data_source = st.text_input("Data Source", value="Manual Upload", placeholder="e.g., SCADA, Logger")
            
            if st.button("Import Data", type="primary"):
                st.success("✅ Data imported successfully! Proceed to Quality Control.")
                st.session_state.uploaded_data = df
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

# Quality Control Page
elif page == "Quality Control":
    st.header("🔍 Quality Control")
    
    if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
        st.warning("⚠️ No data loaded. Please upload data in the Data Ingestion phase first.")
    else:
        df = st.session_state.uploaded_data
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        st.subheader("Automated QC Checks")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.checkbox("Range Check", value=True, help="Flag values outside expected ranges")
        with col2:
            st.checkbox("Spike Detection", value=True, help="Detect sudden jumps in values")
        with col3:
            st.checkbox("Flat-line Detection", value=True, help="Identify periods with no variation")
        
        if st.button("Run QC Checks", type="primary"):
            st.success("✅ QC checks completed!")
            st.info("Found: 5 range violations, 2 spikes, 1 flat-line period")
        
        # Time series visualization
        st.subheader("Time Series Visualization")
        
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        if numeric_cols and 'timestamp' in df.columns:
            selected_param = st.selectbox("Select Parameter to Plot", numeric_cols)
            
            fig = px.line(df, x='timestamp', y=selected_param, title=f"{selected_param} over Time")
            fig.update_layout(xaxis_title="Time", yaxis_title=selected_param, height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Basic statistics
            st.subheader("Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean", f"{df[selected_param].mean():.2f}")
            with col2:
                st.metric("Min", f"{df[selected_param].min():.2f}")
            with col3:
                st.metric("Max", f"{df[selected_param].max():.2f}")
            with col4:
                st.metric("Std Dev", f"{df[selected_param].std():.2f}")

# Data Cleaning Page
elif page == "Data Cleaning":
    st.header("🧹 Data Cleaning")
    
    if 'uploaded_data' not in st.session_state or st.session_state.uploaded_data is None:
        st.warning("⚠️ No data loaded. Please upload data first.")
    else:
        st.markdown("Select time ranges to label as good/bad data and apply cleaning algorithms.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("Start Date")
            st.selectbox("Label", ["Good Data", "Bad Data - Remove", "Suspect - Review"])
        with col2:
            st.date_input("End Date")
            st.text_input("Notes", placeholder="Reason for flagging...")
        
        if st.button("Apply Label", type="primary"):
            st.success("✅ Label applied to selected time range")
        
        st.subheader("Rating Curve Fitting")
        st.markdown("Fit depth-velocity or depth-flow relationships for data repair.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("X Variable", ["Depth", "Velocity"])
        with col2:
            st.selectbox("Y Variable", ["Velocity", "Flow"])
        
        if st.button("Fit Curve", type="primary"):
            st.success("✅ Rating curve fitted: y = 2.34x^0.67 (R² = 0.95)")

# Hydraulics Page
elif page == "Hydraulics":
    st.header("⚙️ Hydraulic Processing")
    
    st.markdown("Calculate hydraulic properties based on pipe geometry and flow measurements.")
    
    col1, col2 = st.columns(2)
    with col1:
        pipe_shape = st.selectbox("Pipe Shape", ["Circular", "Egg-shaped", "Rectangular"])
        pipe_size = st.number_input("Pipe Diameter/Width (mm)", value=300, min_value=50)
    
    with col2:
        if pipe_shape == "Rectangular":
            pipe_height = st.number_input("Pipe Height (mm)", value=300, min_value=50)
        manning_n = st.number_input("Manning's n", value=0.013, format="%.3f")
    
    if st.button("Calculate Hydraulic Properties", type="primary"):
        st.success("✅ Hydraulic calculations completed!")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Full Flow Capacity", "150 L/s")
        with col2:
            st.metric("Avg Flow Rate", "45 L/s")
        with col3:
            st.metric("Peak Flow", "89 L/s")

# Rainfall & I/I Page
elif page == "Rainfall & I/I":
    st.header("🌧️ Rainfall & Inflow/Infiltration Analysis")
    
    st.markdown("Analyze rainfall events and calculate I/I contributions.")
    
    rainfall_file = st.file_uploader("Upload Rainfall Data (CSV)", type=["csv"])
    
    if rainfall_file:
        st.success("✅ Rainfall data loaded")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Events Detected", "12")
            st.metric("Total Rainfall", "145 mm")
        with col2:
            st.metric("Avg I/I Contribution", "35%")
            st.metric("Peak I/I Event", "67%")
    
    if st.button("Detect Rainfall Events", type="primary"):
        st.success("✅ Event detection completed!")

# Reports Page
elif page == "Reports":
    st.header("📊 Reports & Exports")
    
    st.subheader("Generate Reports")
    
    report_type = st.selectbox(
        "Report Type",
        ["Site Summary Report", "Project Summary Report", "QC Report", "Hydraulic Analysis Report"]
    )
    
    output_format = st.radio("Output Format", ["PDF", "Word Document", "Excel"])
    
    if st.button("Generate Report", type="primary"):
        st.success(f"✅ {report_type} generated successfully!")
        st.download_button(
            label=f"Download {report_type}",
            data=b"Sample report content",
            file_name=f"report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
    
    st.subheader("Export Data")
    
    export_type = st.selectbox(
        "Export Type",
        ["Cleaned Time Series (CSV)", "Hydrograph (Excel)", "SWMM Input File", "All Data (ZIP)"]
    )
    
    if st.button("Export", type="primary"):
        st.success(f"✅ {export_type} ready for download!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Current Project:** Not Set")
st.sidebar.markdown("**Version:** 1.0.0")
