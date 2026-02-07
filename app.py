import streamlit as st
import pandas as pd

st.set_page_config(page_title="Property Distance Sorter", layout="wide")
st.title("Property Distance Sorter")

st.caption("Uploads: CSV works everywhere. XLSX may require `openpyxl` depending on the environment.")

uploaded = st.file_uploader(
    "Upload your property distance file",
    type=["csv", "xlsx"],
)

def guess_column(cols, keywords):
    """Return the first column whose name contains any keyword (case-insensitive)."""
    cols_l = {c: str(c).lower() for c in cols}
    for kw in keywords:
        for c, cl in cols_l.items():
            if kw in cl:
                return c
    return None

def load_file(file):
    name = file.name.lower()
    if name.endswith(".csv"):
        # Try utf-8 first, fall back to latin-1 if needed
        try:
            return pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, encoding="latin-1")
    else:
        # XLSX: may fail in Streamlit Playground if openpyxl isn't installed
        try:
            return pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            raise RuntimeError(
                "This environment can't read .xlsx (missing openpyxl). "
                "Please export your file as CSV and upload that instead."
            ) from e

if uploaded:
    try:
        df = load_file(uploaded)
    except Exception as e:
        st.error(str(e))
        st.stop()

    if df.empty:
        st.warning("That file loaded, but it appears to be empty.")
        st.stop()

    st.subheader("1) Map your columns")

    # Reasonable guesses
    guessed_name = guess_column(df.columns, ["property", "name", "home", "listing", "title"])
    guessed_dist = guess_column(df.columns, ["distance", "miles", "mi", "km"])

    c1, c2 = st.columns(2)
    with c1:
        name_col = st.selectbox(
            "Property name column",
            options=list(df.columns),
            index=list(df.columns).index(guessed_name) if guessed_name in df.columns else 0,
        )
    with c2:
        dist_col = st.selectbox(
            "Distance column",
            options=list(df.columns),
            index=list(df.columns).index(guessed_dist) if guessed_dist in df.columns else min(1, len(df.columns)-1),
        )

    # Clean distance
    df[dist_col] = pd.to_numeric(df[dist_col], errors="coerce")

    st.subheader("2) Choose properties")

    # Search filter to make long lists manageable
    search = st.text_input("Search (optional)", placeholder="Type part of a property name…")
    options = df[name_col].dropna().astype(str).unique().tolist()
    options.sort()

    if search.strip():
        s = search.strip().lower()
        options = [o for o in options if s in o.lower()]

    selected = st.multiselect(
        "Properties (type + Enter)",
        options=options,
        default=[],
        placeholder="Start typing a property name…",
    )

    order = st.radio(
        "Sort order",
        ["Closest → Farthest", "Farthest → Closest"],
        horizontal=True,
    )
    ascending = order == "Closest → Farthest"

    st.subheader("3) Results")

    if st.button("Sort & Analyze", type="primary"):
        if not selected:
            st.warning("Please select at least one property.")
            st.stop()

        result = (
            df[df[name_col].astype(str).isin([str(x) for x in selected])]
            .copy()
        )

        # Drop rows where distance is missing (optional; comment out if you want to keep them)
        result = result.dropna(subset=[dist_col])

        result = result.sort_values(by=dist_col, ascending=ascending).reset_index(drop=True)

        if result.empty:
            st.warning("No rows matched your selections (or distances were blank).")
            st.stop()

        # Show table
        st.dataframe(
            result[[name_col, dist_col]],
            use_container_width=True,
            hide_index=True,
        )

        # Numbered summary
        st.markdown("#### Numbered list")
        for i, row in result.iterrows():
            st.write(f"**{i+1}. {row[name_col]}** — {row[dist_col]} miles")

        # Download CSV
        out = result[[name_col, dist_col]].copy()
        csv_bytes = out.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download sorted results (CSV)",
            data=csv_bytes,
            file_name="sorted_property_distances.csv",
            mime="text/csv",
        )

