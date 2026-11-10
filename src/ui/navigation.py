import streamlit as st

_LOGO_SVG = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<circle cx="5" cy="18" r="2.2"/>'
    '<circle cx="19" cy="6" r="2.2"/>'
    '<path d="M7.2 18H14a3.5 3.5 0 0 0 0-7h-4a3.5 3.5 0 0 1 0-7h6.8"/>'
    '</svg>'
)


def create_tabs():
    return st.tabs([
        "📊 Overview",
        "🚚 Route Analysis",
        "💰 Sales Analysis",
        "📦 Product Analysis",
        "⏱️ Delivery Analytics",
        "👥 Customers & Destinations",
        "📄 Data Explorer"
    ])


def sidebar_brand():
    st.sidebar.markdown(
        f"""
        <div class="brand">
            <div class="brand-logo">{_LOGO_SVG}</div>
            <div>
                <div class="brand-name">Shipping Dashboard</div>
                <div class="brand-sub">Logistics &amp; Supply Chain Analytics</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def theme_toggle():
    """Dark / light switch. State lives in st.session_state['dark_mode']."""
    st.sidebar.markdown(
        '<div class="side-label">Appearance</div>',
        unsafe_allow_html=True
    )

    st.session_state.setdefault("dark_mode", True)
    dark_mode = st.session_state["dark_mode"]

    with st.sidebar.container(key="appearance_switch"):
        dark_column, light_column = st.columns(2, gap="small")

        with dark_column:
            st.button(
                "☾ Dark",
                type="primary" if dark_mode else "secondary",
                use_container_width=True,
                on_click=_set_theme,
                args=(True,),
                key="dark_mode_button",
            )

        with light_column:
            st.button(
                "☼ Light",
                type="secondary" if dark_mode else "primary",
                use_container_width=True,
                on_click=_set_theme,
                args=(False,),
                key="light_mode_button",
            )


def _set_theme(dark_mode):
    st.session_state["dark_mode"] = dark_mode


def sidebar_summary(shown, total):
    st.sidebar.markdown(
        f"""
        <div class="side-stat">
            <span>Records shown</span>
            <span><b>{shown:,}</b> / {total:,}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
