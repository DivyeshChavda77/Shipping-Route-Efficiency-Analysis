import streamlit as st

from src.ui.theme import ACCENTS


def section_title(icon, title, subtitle=""):
    """Page / tab heading with an icon tile."""
    sub = f'<div class="section-sub">{subtitle}</div>' if subtitle else ""

    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-icon">{icon}</div>
            <div>
                <div class="section-title">{title}</div>
                {sub}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def hero_banner(title, subtitle, pills=(), eyebrow=""):
    """Gradient page banner with optional info pills."""
    eyebrow_html = f'<div class="hero-eyebrow">{eyebrow}</div>' if eyebrow else ""
    pills_html = "".join(f'<span class="hero-pill">{p}</span>' for p in pills)
    pills_html = f'<div class="hero-pills">{pills_html}</div>' if pills_html else ""

    st.markdown(
        f"""
        <div class="hero">
            {eyebrow_html}
            <div class="hero-title" role="heading" aria-level="1">{title}</div>
            <div class="hero-sub">{subtitle}</div>
            {pills_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def _kpi_html(icon, title, value, accent="indigo", hint=""):
    color = ACCENTS.get(accent, accent)
    hint_html = f'<div class="kpi-hint">{hint}</div>' if hint else ""

    return (
        f'<div class="kpi" style="--accent:{color}">'
        f'<div class="kpi-top">'
        f'<div class="kpi-icon">{icon}</div>'
        f'<div class="kpi-title">{title}</div>'
        f'</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{hint_html}'
        f'</div>'
    )


def kpi_card(icon, title, value, accent="indigo", hint=""):
    """Single KPI card."""
    st.markdown(
        f'<div class="kpi-grid">{_kpi_html(icon, title, value, accent, hint)}</div>',
        unsafe_allow_html=True
    )


def kpi_grid(items):
    """Responsive KPI row. items: (icon, title, value, accent, hint) tuples."""
    cards = "".join(_kpi_html(*item) for item in items)

    st.markdown(
        f'<div class="kpi-grid">{cards}</div>',
        unsafe_allow_html=True
    )


def callout(text, tone="info", icon="ℹ️"):
    """Inline note. tone: info / warning / success."""
    st.markdown(
        f"""
        <div class="callout callout-{tone}">
            <span class="callout-icon">{icon}</span>
            <span>{text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
