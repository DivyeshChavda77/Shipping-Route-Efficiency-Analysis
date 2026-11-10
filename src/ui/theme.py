"""Design tokens shared by the stylesheet and the Plotly charts.

Single source of truth for colours and typography so the CSS (assets/style.css)
and every chart in charts.py always stay visually consistent in both themes.
"""

import streamlit as st

FONT_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500;600;700;800&display=swap"
)
FONT_STACK = (
    "'Inter', 'Segoe UI', system-ui, -apple-system, "
    "'Helvetica Neue', Arial, sans-serif"
)

PALETTES = {
    "dark": {
        "bg": "#0B1120",
        "surface": "#111A2E",
        "surface_2": "#17223B",
        "sidebar": "#0D1426",
        "border": "rgba(148,163,184,0.16)",
        "border_strong": "rgba(148,163,184,0.30)",
        "text": "#E6EAF3",
        "text_2": "#B4BDD0",
        "muted": "#8793AB",
        "primary": "#6366F1",
        "primary_2": "#8B5CF6",
        "primary_soft": "rgba(99,102,241,0.16)",
        "chip_text": "#C7D2FE",
        "glow": "rgba(99,102,241,0.14)",
        "grid": "rgba(148,163,184,0.12)",
        "shadow": "0 1px 2px rgba(0,0,0,.40), 0 8px 24px rgba(0,0,0,.28)",
        "shadow_hover": "0 2px 4px rgba(0,0,0,.40), 0 16px 36px rgba(0,0,0,.42)",
        "scheme": "dark",
    },
    "light": {
        "bg": "#F4F6FB",
        "surface": "#FFFFFF",
        "surface_2": "#F1F4F9",
        "sidebar": "#FFFFFF",
        "border": "rgba(15,23,42,0.08)",
        "border_strong": "rgba(15,23,42,0.18)",
        "text": "#0F172A",
        "text_2": "#334155",
        "muted": "#64748B",
        "primary": "#4F46E5",
        "primary_2": "#7C3AED",
        "primary_soft": "rgba(79,70,229,0.10)",
        "chip_text": "#4338CA",
        "glow": "rgba(79,70,229,0.10)",
        "grid": "rgba(15,23,42,0.07)",
        "shadow": "0 1px 2px rgba(15,23,42,.05), 0 8px 24px rgba(15,23,42,.06)",
        "shadow_hover": "0 2px 4px rgba(15,23,42,.06), 0 16px 36px rgba(15,23,42,.12)",
        "scheme": "light",
    },
}

# Semantic colours (identical in both themes)
SEMANTIC = {
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#F43F5E",
    "info": "#0EA5E9",
}

# Accent colours used by KPI cards (name -> hex)
ACCENTS = {
    "indigo": "#6366F1",
    "emerald": "#10B981",
    "sky": "#0EA5E9",
    "violet": "#8B5CF6",
    "amber": "#F59E0B",
    "teal": "#14B8A6",
    "rose": "#F43F5E",
}

# Sequential colour scales (light -> dark). Mid-tones keep contrast on both themes.
SCALES = {
    "indigo": ["#A5B4FC", "#6366F1", "#4338CA"],
    "emerald": ["#6EE7B7", "#10B981", "#047857"],
    "amber": ["#FCD34D", "#F59E0B", "#B45309"],
    "rose": ["#FDA4AF", "#F43F5E", "#BE123C"],
    "teal": ["#5EEAD4", "#14B8A6", "#0F766E"],
    "violet": ["#C4B5FD", "#8B5CF6", "#6D28D9"],
    "sky": ["#7DD3FC", "#0EA5E9", "#0369A1"],
}

# Categorical colours for pies / grouped scatter plots
CATEGORICAL = [
    "#6366F1",
    "#10B981",
    "#F59E0B",
    "#F43F5E",
    "#06B6D4",
    "#8B5CF6",
]


# ----------------------------------------------------------------------
# Theme state
# ----------------------------------------------------------------------
def is_dark() -> bool:
    """Current appearance, driven by the sidebar toggle (default: dark)."""
    return bool(st.session_state.get("dark_mode", True))


def mode() -> str:
    return "dark" if is_dark() else "light"


def palette() -> dict:
    return PALETTES[mode()]


# ----------------------------------------------------------------------
# CSS helpers
# ----------------------------------------------------------------------
def css_variables() -> str:
    """CSS custom properties for the active theme."""
    p = palette()

    pairs = {
        "--bg": p["bg"],
        "--surface": p["surface"],
        "--surface-2": p["surface_2"],
        "--sidebar": p["sidebar"],
        "--border": p["border"],
        "--border-strong": p["border_strong"],
        "--text": p["text"],
        "--text-2": p["text_2"],
        "--muted": p["muted"],
        "--primary": p["primary"],
        "--primary-2": p["primary_2"],
        "--primary-soft": p["primary_soft"],
        "--chip-text": p["chip_text"],
        "--glow": p["glow"],
        "--shadow": p["shadow"],
        "--shadow-hover": p["shadow_hover"],
        "--success": SEMANTIC["success"],
        "--warning": SEMANTIC["warning"],
        "--danger": SEMANTIC["danger"],
        "--info": SEMANTIC["info"],
        "--font": FONT_STACK,
        "color-scheme": p["scheme"],
    }
    body = ";".join(f"{k}:{v}" for k, v in pairs.items())
    return f":root{{{body}}}"


# Streamlit's own base theme, pinned in .streamlit/config.toml (base = "dark").
NATIVE_BASE = "dark"


def native_widget_fix() -> str:
    """Canvas-based widgets (st.dataframe) follow Streamlit's own theme.

    When the dashboard theme differs from Streamlit's base theme, flip those
    widgets so tables always match the rest of the page.
    """
    if NATIVE_BASE == mode():
        return ""
    return (
        '[data-testid="stDataFrame"]'
        "{filter:invert(1) hue-rotate(180deg)}"
    )


def build_css(stylesheet: str) -> str:
    """Full <style> payload: font import must come first."""
    return (
        f"@import url('{FONT_URL}');"
        f"{css_variables()}"
        f"{stylesheet}"
        f"{native_widget_fix()}"
    )
