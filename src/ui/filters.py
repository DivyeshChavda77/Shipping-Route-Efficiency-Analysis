import streamlit as st
import pandas as pd


def _label(text):
    st.sidebar.markdown(
        f'<div class="side-label">{text}</div>',
        unsafe_allow_html=True
    )


def sidebar_filters(df):
    """
    Creates sidebar filters and returns filtered dataframe.
    """

    _label("🔍 Filters")

    # Region
    region = st.sidebar.multiselect(
        "Region",
        options=sorted(df["Region"].dropna().unique()),
        default=sorted(df["Region"].dropna().unique())
    )

    filtered = df[df["Region"].isin(region)]

    # Ship Mode
    ship_mode = st.sidebar.multiselect(
        "Ship Mode",
        options=sorted(filtered["Ship Mode"].dropna().unique()),
        default=sorted(filtered["Ship Mode"].dropna().unique())
    )

    filtered = filtered[
        filtered["Ship Mode"].isin(ship_mode)
    ]

    # State
    state = st.sidebar.multiselect(
        "State",
        options=sorted(filtered["State/Province"].dropna().unique()),
        default=sorted(filtered["State/Province"].dropna().unique())
    )

    filtered = filtered[
        filtered["State/Province"].isin(state)
    ]

    # Division
    division = st.sidebar.multiselect(
        "Division",
        options=sorted(filtered["Division"].dropna().unique()),
        default=sorted(filtered["Division"].dropna().unique())
    )

    filtered = filtered[
        filtered["Division"].isin(division)
    ]

    # Order Date
    _label("📅 Date Filter")

    filtered = filtered.copy()

    filtered["Order Date"] = pd.to_datetime(
        filtered["Order Date"],
        errors="coerce"
    )

    valid_dates = filtered["Order Date"].dropna()

    if not valid_dates.empty:

        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        date_range = st.sidebar.date_input(
            "Order Date",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if len(date_range) == 2:

            start_date, end_date = date_range

            filtered = filtered[
                filtered["Order Date"].between(
                    pd.Timestamp(start_date),
                    pd.Timestamp(end_date)
                )
            ]

        elif len(date_range) == 1:

            selected_date = date_range[0]

            filtered = filtered[
                filtered["Order Date"].dt.date == selected_date
            ]
    return filtered
