import streamlit as st
import pandas as pd

st.set_page_config(page_title="Property Distance Sorter", layout="wide")
st.title("Property Distance Sorter")

uploaded = st.file_uploader("Upload your property distance Excel file", type=["xlsx"])

if uploaded:
    df = pd.read_excel(uploaded)

    # Auto-detect columns
    name_col = "Property Name" if "Property Name" in df.columns else st.selectbox("Property name column", df.columns)
    dist_col = "Distance" if "Distance" in df.columns else st.selectbox("Distance column", df.columns)

    # Ensure numeric distance
    df[dist_col] = pd.to_numeric(df[dist_col], errors="coerce")

    st.subheader("Select Properties")
    st.write("Start typing a property name and press **Enter** to add it.")

    selected = st.multiselect(
        "Properties",
        options=df[name_col].dropna().tolist(),
        default=[],
        placeholder="Type a property name…"
    )

    order = st.radio(
        "Sort order",
        ["Closest → Farthest", "Farthest → Closest"],
        horizontal=True
    )
    ascending = order == "Closest → Farthest"

    if st.button("Sort & Analyze", type="primary"):
        if not selected:
            st.warning("Please select at least one property.")
        else:
            result = (
                df[df[name_col].isin(selected)]
                .sort_values(by=dist_col, ascending=ascending)
                .reset_index(drop=True)
            )

            st.subheader("Sorted Results")

            for i, row in result.iterrows():
                st.write(f"**{i+1}. {row[name_col]}** — {row[dist_col]} miles")
