import streamlit as st

st.set_page_config(page_title="Sewer Flow Modelling", layout="wide")
st.title("Sewer Flow Modelling")

st.markdown(
    """
    **Phases**
    1. Ingest (CSV/Excel upload)
    2. QC (range/spike/flat/missing)
    3. Cleaning (label good/bad, rating curves)
    4. Hydraulics (geometry + flow)
    5. Rainfall & I/I (event stats)
    6. Export & Reporting
    """
)

st.info("UI placeholder – wire up API endpoints and visualizations as features land.")
