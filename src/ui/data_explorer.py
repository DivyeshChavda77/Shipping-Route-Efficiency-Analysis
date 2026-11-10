import streamlit as st

from src.ui.cards import section_title

def data_explorer(df):
    
    section_title(
        "📄", "Data Explorer",
        "Search, filter and download the shipping dataset."
    )

    filtered = df.copy()

    # ======================
    # Metrics
    # ======================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Records",
        f"{len(filtered):,}"
    )

    c2.metric(
        "Unique Orders",
        f"{filtered['Order ID'].nunique():,}"
    )

    c3.metric(
        "Missing Values",
        f"{int(filtered.isna().sum().sum()):,}"
    )

    memory = filtered.memory_usage(deep=True).sum() / 1024**2

    c4.metric(
        "Memory Usage",
        f"{memory:.2f} MB"
    )

    st.write("")

    # ======================
    # Search + Download
    # ======================

    left, right = st.columns([5,1], vertical_alignment="center")

    with left:
        search = st.text_input(
            "Search",
            placeholder="🔍 Search product, city, state or order ID...",
            key="data_explorer_search",
            label_visibility="collapsed"
        )

        if search:
            search = search.strip()

            if search:
                search_mask = (
                    filtered["Product Name"]
                    .astype(str)
                    .str.contains(search, case=False, na=False, regex=False)
                    |
                    filtered["City"]
                    .astype(str)
                    .str.contains(search, case=False, na=False, regex=False)
                    |
                    filtered["State/Province"]
                    .astype(str)
                    .str.contains(search, case=False, na=False, regex=False)
                    |
                    filtered["Order ID"]
                    .astype(str)
                    .str.contains(search, case=False, na=False, regex=False)
                )

                filtered = filtered[search_mask]

    with right:
        csv = filtered.to_csv(index=False)

        st.download_button(
            "📥 Download CSV",
            csv,
            "filtered_shipping_data.csv",
            "text/csv",
            width="stretch"
        )

    st.write("")

    if filtered.empty:
        st.info(
            "🔍 No records found. Try a different search term or adjust the filters."
        )
    else:
        st.dataframe(
            filtered,
            width="stretch",
            hide_index=True,
            height=500
        )

