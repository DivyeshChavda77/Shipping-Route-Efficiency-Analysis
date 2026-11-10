import hashlib
import inspect
from contextlib import contextmanager

import streamlit as st


# st.plotly_chart gained `width` after use_container_width was deprecated
_PLOTLY_WIDTH = (
    {"width": "stretch"}
    if "width" in inspect.signature(st.plotly_chart).parameters
    else {"use_container_width": True}
)


def _uid(title, subtitle=""):
    return hashlib.md5(f"{title}|{subtitle}".encode()).hexdigest()[:8]


def display_chart(fig, key=None):
    """Render a Plotly figure using our own theme (not Streamlit's).

    Pass a unique `key` when several charts could be identical (e.g. empty
    placeholders), otherwise Streamlit raises a duplicate-element error.
    """
    st.plotly_chart(
        fig,
        key=key,
        theme=None,
        config={"displayModeBar": False},
        **_PLOTLY_WIDTH
    )


@contextmanager
def chart_card(title, subtitle=""):
    """Card container: `with chart_card(title, subtitle): ...`

    A keyed container is used so the card styling in style.css wraps the
    chart itself (the old open/close HTML tags could not).
    """
    with st.container(key=f"card-{_uid(title, subtitle)}"):
        st.markdown(
            f"""
            <div class="chart-head">
                <div class="chart-title">{title}</div>
                <div class="chart-subtitle">{subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        yield


def chart_grid(df, specs, cols=2):
    """Lay out chart cards in rows of `cols`.

    specs: list of (title, subtitle, chart_function) — each chart function
    takes the dataframe and returns a Plotly figure.
    """
    for start in range(0, len(specs), cols):
        row = specs[start:start + cols]

        for column, (title, subtitle, chart_fn) in zip(
            st.columns(cols, gap="medium"), row
        ):
            with column:
                with chart_card(title, subtitle):
                    display_chart(chart_fn(df), key=f"chart-{_uid(title, subtitle)}")
