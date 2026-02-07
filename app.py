import streamlit as st
import pandas as pd

st.set_page_config(page_title="Property Distance Sorter", layout="wide")
st.title("Property Distance Sorter")


# Notes box
notes = st.text_area(
    "Notes",
    placeholder="Jot down routing ideas, priorities, or reminders…",
    height=120
)

uploaded = st.file_uploader(
    "Upload your property distance file",
    type=["csv", "xlsx"]
)

if uploaded:
    # Load file
    try:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded, engine="openpyxl")
    except:
        st.error("If uploading Excel, openpyxl must be installed. CSV always works.")
        st.stop()

    # Auto-detect columns (simple)
    name_col = "Property Name" if "Property Name" in df.columns else st.selectbox("Property name column", df.columns)
    dist_col = "Distance" if "Distance" in df.columns else st.selectbox("Distance column", df.columns)
    neigh_col = "Neighborhood" if "Neighborhood" in df.columns else st.selectbox("Neighborhood column", df.columns)

    df[dist_col] = pd.to_numeric(df[dist_col], errors="coerce")

    st.subheader("Select Properties")

    selected = st.multiselect(
        "Properties",
        options=df[name_col].dropna().tolist(),
        placeholder="Type a property name…"
    )

    order = st.radio(
        "Sort order",
        ["Closest → Farthest", "Farthest → Closest"],
        horizontal=True
    )

    ascending = order == "Closest → Farthest"

    if st.button("Sort"):
        if not selected:
            st.warning("Please select at least one property.")
        else:
            result = (
                df[df[name_col].isin(selected)]
                .sort_values(by=dist_col, ascending=ascending)
                .reset_index(drop=True)
            )

            st.subheader("Sorted Results")
            
            table = result[[name_col, dist_col, neigh_col]].copy()
            table.columns = ["Property", "Miles", "Neighborhood"]
            
            st.dataframe(table, use_container_width=True, hide_index=True)



