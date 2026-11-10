import streamlit as st

def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root { --tlc-blue: #07599f; --tlc-yellow: #f4c542; --ink: #172033; --muted: #52657d; --panel: #f7f9fc; }
        .stApp, [data-testid="stAppViewContainer"] { background: #ffffff; color: var(--ink); }
        .block-container { max-width: 1500px; padding: 2rem 3rem 4rem; }
        [data-testid="stHeader"] { background: #ffffff; }
        [data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid #d6e0eb; }
        [data-testid="stSidebar"] * { color: var(--ink); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label { color: var(--muted) !important; font-weight: 600; }
        [data-testid="stSidebar"] a { color: var(--tlc-blue) !important; }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] { padding: .5rem .65rem 1rem; }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a { font-size: .98rem; font-weight: 700; padding: .78rem .9rem; margin: .2rem 0; border: 1px solid transparent; border-radius: .65rem; transition: all .2s ease; }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover { background: #e8f1fb; border-color: #c8dced; color: var(--tlc-blue) !important; transform: translateX(3px); }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] { background: var(--tlc-blue); color: #ffffff !important; border-color: var(--tlc-blue); box-shadow: 0 4px 10px rgba(7,89,159,.2); }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] span { color: #ffffff !important; }
        [data-testid="stSidebar"] input, [data-testid="stSidebar"] button,
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div { background: #ffffff !important; color: var(--ink) !important; border-color: #c8d5e3 !important; }
        [data-testid="stSidebar"] input::placeholder { color: #7b8ba0 !important; }
        [data-testid="stSidebar"] [data-baseweb="select"] svg { fill: var(--tlc-blue); }
        [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] { background: var(--tlc-blue); border-color: var(--tlc-blue); }
        h1, h2, h3 { color: var(--ink) !important; letter-spacing: -0.02em; }
        p, li, [data-testid="stCaptionContainer"] { color: var(--muted); }
        .sidebar-brand { padding: .8rem .8rem 1rem; margin: .4rem .65rem .6rem; border-bottom: 1px solid #d6e0eb; }
        .sidebar-mark { display: inline-flex; background: var(--tlc-yellow); color: var(--ink); font-weight: 900; border-radius: .45rem; padding: .3rem .5rem; margin-bottom: .55rem; }
        .sidebar-title { color: var(--ink); font-size: 1.1rem; font-weight: 800; line-height: 1.15; }
        .sidebar-caption { color: var(--muted); font-size: .75rem; margin-top: .35rem; }
        .hero { background: linear-gradient(110deg, #f1f7fd 0%, #ffffff 68%); border: 1px solid #dce8f3; border-left: 6px solid var(--tlc-blue); border-bottom: 5px solid var(--tlc-yellow); border-radius: .85rem; padding: 1.5rem 1.7rem 1.65rem; margin-bottom: 1.7rem; box-shadow: 0 5px 16px rgba(23,32,51,.06); }
        .eyebrow { display: inline-block; color: #ffffff; background: var(--tlc-blue); border-radius: 999px; padding: .35rem .75rem; font-size: .72rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
        .hero h1 { font-size: clamp(2.1rem, 4vw, 3.45rem); line-height: 1.05; margin: .8rem 0 .55rem; }
        .subtitle { color: var(--muted); font-size: 1.08rem; }
        .feature-card { min-height: 145px; background: #ffffff; border: 1px solid #dce6f0; border-top: 4px solid var(--tlc-blue); border-radius: .7rem; padding: 1.15rem; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(23,32,51,.06); }
        .feature-card:hover { border-top-color: var(--tlc-yellow); box-shadow: 0 7px 18px rgba(23,32,51,.1); transform: translateY(-2px); }
        .feature-number { color: var(--tlc-blue); font-size: .75rem; font-weight: 800; letter-spacing: .12em; }
        .feature-title { color: var(--ink); font-size: 1.05rem; font-weight: 800; margin: .35rem 0 .45rem; }
        .feature-copy { color: var(--muted); font-size: .9rem; line-height: 1.45; }
        [data-testid="stMetric"] { min-height: 112px; background: #ffffff; border: 1px solid #dfe7f1; border-top: 4px solid var(--tlc-blue); padding: 1.15rem; border-radius: .7rem; box-shadow: 0 3px 12px rgba(23,32,51,.07); }
        [data-testid="stMetricLabel"] { color: var(--muted) !important; }
        [data-testid="stMetricValue"] { color: var(--ink) !important; }
        [data-testid="stMetricDelta"] { color: var(--muted) !important; }
        [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"] div { background: transparent !important; color: inherit !important; }
        [data-testid="stPlotlyChart"] { background: #ffffff; border: 1px solid #e3eaf2; border-radius: .6rem; padding: .35rem; box-shadow: 0 2px 8px rgba(23,32,51,.04); }
        [data-testid="stDataFrame"] { border: 1px solid #dfe7f1; }
        [data-testid="stAlert"] { border-radius: .5rem; }
        .stButton > button, .stDownloadButton > button { border-radius: .4rem; border: 1px solid var(--tlc-blue); color: var(--tlc-blue); background: #ffffff; }
        .stButton > button:hover, .stDownloadButton > button:hover { color: #ffffff; background: var(--tlc-blue); }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="sidebar-brand"><div class="sidebar-mark">TLC</div>'
        '<div class="sidebar-title">Urban Mobility<br>Intelligence</div>'
        '<div class="sidebar-caption">NYC transportation analytics</div></div>',
        unsafe_allow_html=True,
    )

def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><div class="eyebrow">NYC TLC | Urban Mobility Intelligence</div>'
        f'<h1>{title}</h1><div class="subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )
