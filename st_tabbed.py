import streamlit as st
import pandas as pd
from pydantic import BaseModel, Field, ValidationError

# --- 1. DATA VALIDATION MODELS ---
# These replace manual "if/else" checks with robust engineering constraints.

class AreaInput(BaseModel):
    basin_id: str
    land_use: str
    # ge = Greater than or Equal to | le = Less than or Equal to
    impervious_fraction: float = Field(
        ge=0.0, 
        le=1.0, 
        description="Imperviousness must be between 0 and 1.0 (0% to 100%)"
    )
    area_acres: float = Field(
        gt=0.0, 
        description="Area must be greater than zero"
    )

class BasinInput(BaseModel):
    basin_id: str = Field(min_length=1)
    tc_min: float = Field(ge=5.0, le=60.0)


# --- 2. STREAMLIT UI SETUP ---

st.set_page_config(layout="wide")
st.title("MHFD Rational Method - Hydrologic Inputs")

# Initialize Session State DataFrames
if 'df_basins' not in st.session_state:
    st.session_state.df_basins = pd.DataFrame(columns=['Basin ID', 'Tc (min)'])
if 'df_areas' not in st.session_state:
    st.session_state.df_areas = pd.DataFrame(columns=['Basin ID', 'Land Use', 'Imperv', 'Area (ac)'])

# --- 3. INPUT FORMS ---

col1, col2 = st.columns(2)

with col1:
    with st.expander("Subcatchment Management", expanded=True):
        with st.form("basin_form", clear_on_submit=True):
            st.subheader("Add/Update Basin")
            b_id = st.text_input("Unique Basin ID (e.g., 'A1')")
            tc = st.number_input("Time of Concentration (5-60 min)", value=5.0, step=0.1)
            
            submit_basin = st.form_submit_button("Save Basin")
            
            if submit_basin:
                try:
                    # Validate using Pydantic
                    valid_basin = BasinInput(basin_id=b_id, tc_min=tc)
                    
                    new_row = pd.DataFrame([[valid_basin.basin_id, valid_basin.tc_min]], 
                                           columns=st.session_state.df_basins.columns)
                    
                    # Update if exists, otherwise add
                    st.session_state.df_basins = pd.concat([st.session_state.df_basins, new_row]).drop_duplicates('Basin ID', keep='last')
                    st.success(f"Basin {b_id} saved.")
                except ValidationError as e:
                    st.error(f"Validation Error: {e.errors()[0]['msg']}")

with col2:
    with st.expander("Area & Land Use Management", expanded=True):
        # Prevent adding areas if no basins exist
        existing_basins = st.session_state.df_basins['Basin ID'].unique()
        
        if len(existing_basins) == 0:
            st.warning("Please add at least one Basin on the left first.")
        else:
            with st.form("area_form", clear_on_submit=True):
                st.subheader("Add Constituent Area")
                target_b = st.selectbox("Assign to Basin", existing_basins)
                l_use = st.selectbox("Land Use Type", ["Pavement", "Roofs", "Lawn", "Pasture", "Driveways"])
                imp = st.number_input("Impervious Fraction (0.0-1.0)", value=0.0, step=0.01)
                area = st.number_input("Area (acres)", value=0.1, step=0.1)
                
                submit_area = st.form_submit_button("Add Area to Basin")
                
                if submit_area:
                    try:
                        # Validate using Pydantic
                        valid_data = AreaInput(
                            basin_id=target_b, 
                            land_use=l_use, 
                            impervious_fraction=imp, 
                            area_acres=area
                        )
                        
                        new_area_row = pd.DataFrame([[
                            valid_data.basin_id, 
                            valid_data.land_use, 
                            valid_data.impervious_fraction, 
                            valid_data.area_acres
                        ]], columns=st.session_state.df_areas.columns)
                        
                        st.session_state.df_areas = pd.concat([st.session_state.df_areas, new_area_row], ignore_index=True)
                        st.success(f"Added {l_use} to Basin {target_b}.")
                    except ValidationError as e:
                        # This catches errors like strings in numeric fields or numbers out of range
                        st.error(f"Input Error: {e.errors()[0]['msg']}")

# --- 4. DATA DISPLAY ---

st.divider()
tab1, tab2 = st.tabs(["Subcatchment Table", "Area Breakdown"])

with tab1:
    st.dataframe(st.session_state.df_basins, use_container_width=True, hide_index=True)

with tab2:
    st.dataframe(st.session_state.df_areas, use_container_width=True, hide_index=True)