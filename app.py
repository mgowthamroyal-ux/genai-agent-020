import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from google import genai
import streamlit as st

# ==========================================
# PAGE & ENVIRONMENT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
MODEL = (os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite").strip()
DB_PATH = BASE_DIR / "studio.db"
PAGES = ["Dashboard", "Content Studio", "Saved Content", "Settings"]

st.set_page_config(
    page_title="Product Studio",
    page_icon="💎",
    layout="wide",
)

# ==========================================
# SESSION STATE & THEME
# ==========================================

if "draft" not in st.session_state:
    st.session_state["draft"] = ""

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Dashboard"

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"


def _sync_from_sidebar() -> None:
    st.session_state["active_page"] = st.session_state["sidebar_nav"]


def _set_page(target: str) -> None:
    st.session_state["active_page"] = target
    st.session_state["sidebar_nav"] = target


# ==========================================
# NAVY & GOLD / LIGHT THEME STYLING
# ==========================================

is_dark = st.session_state["theme_mode"] == "Dark"

if is_dark:
    app_bg = "radial-gradient(circle at top right, #182952 0%, #0b132b 55%, #070d1e 100%)"
    ink = "#f8fafc"
    muted = "#cbd5e1"
    heading_color = "#f8e39c"
    gold_accent = "#f5c542"
    sidebar_bg = "linear-gradient(180deg, #080f24 0%, #0d1836 100%)"
    sidebar_text = "#f1f5f9"
    card_bg = "rgba(15, 25, 54, 0.86)"
    metric_bg = "rgba(15, 25, 54, 0.82)"
    border_gold = "rgba(212, 175, 55, 0.30)"
    input_bg = "#0b142c"
    sec_btn_bg = "rgba(22, 36, 74, 0.90)"
    sec_btn_text = "#f8e39c"
    nav_ctrl_bg = "rgba(15, 25, 54, 0.95)"
    nav_ctrl_color = "#f8e39c"
    nav_ctrl_border = "rgba(212, 175, 55, 0.65)"
    success_bg, success_fg, success_border = "#0b3b24", "#bbf7d0", "#22c55e"
    info_bg, info_fg, info_border = "#0f294a", "#dbeafe", "#38bdf8"
    warn_bg, warn_fg, warn_border = "#3b2806", "#fef3c7", "#f59e0b"
    err_bg, err_fg, err_border = "#45121b", "#fecaca", "#f87171"
else:
    app_bg = "radial-gradient(circle at top right, #e6eefc 0%, #f5f7fb 55%, #eef2f9 100%)"
    ink = "#0f1c3f"
    muted = "#475569"
    heading_color = "#0f1c3f"
    gold_accent = "#b48312"
    sidebar_bg = "linear-gradient(180deg, #ffffff 0%, #f1f5fb 100%)"
    sidebar_text = "#0f1c3f"
    card_bg = "rgba(255, 255, 255, 0.94)"
    metric_bg = "rgba(255, 255, 255, 0.94)"
    border_gold = "rgba(180, 131, 18, 0.35)"
    input_bg = "#ffffff"
    sec_btn_bg = "#edf2ff"
    sec_btn_text = "#0f1c3f"
    nav_ctrl_bg = "rgba(255, 255, 255, 0.98)"
    nav_ctrl_color = "#0f1c3f"
    nav_ctrl_border = "rgba(180, 131, 18, 0.65)"
    success_bg, success_fg, success_border = "#dcfce7", "#14532d", "#16a34a"
    info_bg, info_fg, info_border = "#dbeafe", "#1e3a8a", "#2563eb"
    warn_bg, warn_fg, warn_border = "#fef3c7", "#78350f", "#d97706"
    err_bg, err_fg, err_border = "#fee2e2", "#7f1d1d", "#dc2626"

st.markdown(
    f"""
    <style>
        .stApp {{
            background: {app_bg};
            color: {ink};
            overflow-x: hidden;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
            z-index: 999 !important;
            pointer-events: auto !important;
        }}

        /* Keep stToolbar container visible because stExpandSidebarButton lives inside it,
           and hide only the unwanted toolbar action items */
        [data-testid="stToolbar"] {{
            background: transparent !important;
        }}

        [data-testid="stToolbarActions"],
        [data-testid="stToolbarActionButton"],
        [data-testid="stShareButton"],
        [data-testid="stFavoriteButton"],
        [data-testid="stMainMenu"],
        #MainMenu,
        [data-testid="stAppDeployButton"],
        .stDeployButton,
        [data-testid="stDecoration"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* Hide Streamlit footer, branding badges, and Manage app button */
        footer,
        [data-testid="stFooter"],
        [data-testid="manage-app-button"],
        [class*="viewerBadge"],
        a[href*="streamlit.io"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* Hide heading anchor link icons */
        [data-testid="stHeaderActionElements"],
        a.header-anchor,
        [data-testid="stMarkdownContainer"] h1 a[href^="#"],
        [data-testid="stMarkdownContainer"] h2 a[href^="#"],
        [data-testid="stMarkdownContainer"] h3 a[href^="#"],
        [data-testid="stHeadingWithActionElements"] a[href^="#"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* Restore & highlight sidebar expand and collapse arrow buttons on desktop & mobile touch */
        [data-testid="stSidebarHeader"],
        [data-testid="stExpandSidebarButton"],
        [data-testid="stExpandSidebarButton"] button,
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="collapsedControl"],
        [data-testid="collapsedControl"] button {{
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
        }}

        [data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="collapsedControl"] button {{
            display: inline-flex !important;
            min-width: 44px !important;
            min-height: 44px !important;
            border-radius: 10px !important;
            background: {nav_ctrl_bg} !important;
            border: 1px solid {nav_ctrl_border} !important;
            color: {nav_ctrl_color} !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22) !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        [data-testid="stExpandSidebarButton"] *,
        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="collapsedControl"] * {{
            color: {nav_ctrl_color} !important;
            fill: currentColor !important;
            opacity: 1 !important;
            visibility: visible !important;
        }}

        [data-testid="stSidebar"] {{
            background: {sidebar_bg};
            border-right: 1px solid {border_gold};
            padding-top: env(safe-area-inset-top, 0px);
        }}

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stRadio *,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] *,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {{
            color: {sidebar_text} !important;
        }}

        h1, h2, h3 {{
            color: {heading_color} !important;
            letter-spacing: -0.02em;
            overflow-wrap: anywhere;
        }}

        .stMarkdown p, .stMarkdown li, label, .stCaption {{
            color: {ink} !important;
            overflow-wrap: anywhere;
        }}

        /* High-contrast Alert / Status Boxes (Success, Info, Warning, Error) in Dark & Light modes */
        .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]),
        .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]),
        [data-testid="stSidebar"] [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) {{
            background-color: {success_bg} !important;
            border: 1px solid {success_border} !important;
            border-radius: 10px !important;
        }}
        .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) *,
        .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) *,
        [data-testid="stSidebar"] [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) * {{
            color: {success_fg} !important;
            fill: currentColor !important;
        }}

        .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]),
        .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]),
        [data-testid="stSidebar"] [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) {{
            background-color: {info_bg} !important;
            border: 1px solid {info_border} !important;
            border-radius: 10px !important;
        }}
        .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) *,
        .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) *,
        [data-testid="stSidebar"] [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) * {{
            color: {info_fg} !important;
            fill: currentColor !important;
        }}

        .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]),
        .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]),
        [data-testid="stSidebar"] [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) {{
            background-color: {warn_bg} !important;
            border: 1px solid {warn_border} !important;
            border-radius: 10px !important;
        }}
        .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) *,
        .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) *,
        [data-testid="stSidebar"] [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) * {{
            color: {warn_fg} !important;
            fill: currentColor !important;
        }}

        .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentError"]),
        .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]),
        [data-testid="stSidebar"] [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) {{
            background-color: {err_bg} !important;
            border: 1px solid {err_border} !important;
            border-radius: 10px !important;
        }}
        .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) *,
        .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) *,
        [data-testid="stSidebar"] [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) * {{
            color: {err_fg} !important;
            fill: currentColor !important;
        }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: {card_bg};
            border: 1px solid {border_gold} !important;
            border-radius: 14px !important;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16);
        }}

        [data-testid="stMetric"] {{
            background: {metric_bg};
            border: 1px solid {border_gold};
            border-radius: 12px;
            padding: 14px 16px;
        }}

        [data-testid="stMetricLabel"] {{
            color: {muted} !important;
        }}

        [data-testid="stMetricValue"] {{
            color: {gold_accent} !important;
            font-weight: 800 !important;
        }}

        input, textarea, select, [data-baseweb="select"] > div, [data-baseweb="input"] > div {{
            background-color: {input_bg} !important;
            color: {ink} !important;
            border-color: {border_gold} !important;
        }}

        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, #f5c542, #d4af37) !important;
            color: #0b132b !important;
            border: none !important;
            font-weight: 700 !important;
        }}

        .stButton > button[kind="secondary"],
        .stDownloadButton > button {{
            background: {sec_btn_bg} !important;
            color: {sec_btn_text} !important;
            border: 1px solid {border_gold} !important;
            font-weight: 600 !important;
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            filter: brightness(1.06);
        }}

        [data-testid="stExpander"] {{
            background: {card_bg};
            border: 1px solid {border_gold} !important;
            border-radius: 12px !important;
        }}

        .footer {{
            margin-top: 40px;
            padding: 18px 0 6px 0;
            border-top: 1px solid {border_gold};
            text-align: center;
            color: {muted};
            font-size: 13px;
            line-height: 1.7;
        }}

        /* Hide mobile quick-nav bar on desktop so desktop design stays unchanged */
        @media (min-width: 769px) {{
            [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .mobile-nav-anchor) {{
                display: none !important;
            }}
        }}

        /* Mobile responsiveness (360px, 390px, 430px, <= 768px) */
        @media (max-width: 768px) {{
            [data-testid="stHeader"] {{
                height: calc(env(safe-area-inset-top, 0px) + 3.25rem) !important;
                min-height: 3.25rem !important;
            }}

            [data-testid="stMainBlockContainer"] {{
                padding-left: 0.85rem !important;
                padding-right: 0.85rem !important;
                padding-top: calc(env(safe-area-inset-top, 0px) + 3.25rem) !important;
                padding-bottom: 1.5rem !important;
                max-width: 100% !important;
            }}

            [data-testid="stSidebar"] {{
                z-index: 1000005 !important;
            }}

            [data-testid="stExpandSidebarButton"] {{
                position: fixed !important;
                top: calc(env(safe-area-inset-top, 0px) + 0.4rem) !important;
                left: calc(env(safe-area-inset-left, 0px) + 0.75rem) !important;
                display: inline-flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                z-index: 1000000 !important;
            }}

            [data-testid="stSidebarCollapseButton"],
            [data-testid="stSidebarCollapseButton"] button {{
                display: inline-flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                z-index: 1000010 !important;
            }}

            [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .mobile-nav-anchor) {{
                margin-bottom: 0.25rem !important;
                gap: 0.45rem !important;
            }}

            .stButton > button {{
                white-space: normal !important;
                overflow: visible !important;
                text-overflow: clip !important;
                line-height: 1.2 !important;
                min-height: 44px !important;
                padding: 0.45rem 0.65rem !important;
            }}

            h1 {{
                font-size: clamp(1.4rem, 5.8vw, 1.9rem) !important;
                line-height: 1.2 !important;
                margin-top: 0.25rem !important;
                padding-top: 0.25rem !important;
            }}

            h2 {{
                font-size: clamp(1.15rem, 4.8vw, 1.4rem) !important;
            }}

            [data-testid="stHorizontalBlock"] {{
                flex-wrap: wrap !important;
                gap: 0.55rem !important;
            }}

            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                flex: 1 1 calc(50% - 0.45rem) !important;
                min-width: calc(50% - 0.45rem) !important;
            }}

            [data-testid="stMetric"] {{
                padding: 12px !important;
            }}

            [data-testid="stMetricValue"] {{
                font-size: clamp(1.2rem, 5vw, 1.65rem) !important;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# DATABASE HELPERS (PRESERVING studio.db)
# ==========================================


def fetch_drafts() -> list[tuple[int, str, str, str]]:
    """Read existing saved drafts without mutating studio.db."""
    if not DB_PATH.exists():
        return []
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
        table_exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='drafts'"
        ).fetchone()
        if not table_exists:
            return []
        return conn.execute(
            "SELECT id, product, kind, content FROM drafts ORDER BY id DESC"
        ).fetchall()


def insert_draft(product: str, kind: str, content: str) -> None:
    """Save a generated draft to the drafts table in studio.db."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT,
                kind TEXT,
                content TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO drafts (product, kind, content) VALUES (?, ?, ?)",
            (product, kind, content),
        )
        conn.commit()


def remove_draft(draft_id: int) -> None:
    """Delete a saved draft by ID from studio.db."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
        conn.commit()


# ==========================================
# GEMINI AI CONTENT GENERATION
# ==========================================


def generate_content(
    name: str,
    price: float,
    features: str,
    kind: str,
    tone: str,
    instructions: str,
) -> str:
    """Generate marketing content using Google Gemini."""
    client = genai.Client(api_key=API_KEY)

    prompt = f"""
You are a professional product marketing content agent.

Product name: {name}
Price: INR {price}
Product features: {features}
Content type: {kind}
Brand tone: {tone}
Additional instructions: {instructions}

Generate professional, accurate and engaging marketing content.
Use Indian rupees (INR) for pricing.
Do not invent product specifications.
Return only the requested marketing content.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    if not response.text:
        raise ValueError("Gemini returned empty content.")

    return response.text


# ==========================================
# SIDEBAR & MOBILE QUICK NAVIGATION
# ==========================================

st.sidebar.title("💎 Product Studio")
st.sidebar.caption("AI Marketing Workspace")

if "sidebar_nav" not in st.session_state:
    st.session_state["sidebar_nav"] = st.session_state["active_page"]

st.sidebar.radio(
    "Workspace",
    PAGES,
    key="sidebar_nav",
    on_change=_sync_from_sidebar,
)

st.sidebar.divider()

theme_choice = st.sidebar.radio(
    "Theme",
    ["Dark", "Light"],
    key="theme_mode",
    horizontal=True,
)

if API_KEY:
    st.sidebar.success("Gemini API configured")
else:
    st.sidebar.error("Gemini API key missing")

st.sidebar.caption(f"Model: {MODEL}")
st.sidebar.caption("GENAI-AGENT-020 · INR ₹")

# Visible mobile quick-navigation bar (hidden on desktop via CSS)
with st.container():
    st.markdown('<div class="mobile-nav-anchor"></div>', unsafe_allow_html=True)
    m_cols = st.columns(4)
    for idx, label in enumerate(PAGES):
        with m_cols[idx]:
            st.button(
                label,
                key=f"mob_nav_{label}",
                type="primary" if st.session_state["active_page"] == label else "secondary",
                width="stretch",
                on_click=_set_page,
                args=(label,),
            )

page = st.session_state["active_page"]


# ==========================================
# PAGES
# ==========================================

if page == "Dashboard":
    st.title("💎 Product Studio Dashboard")
    st.write("AI-powered product content generation system")

    drafts = fetch_drafts()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Saved Drafts", len(drafts))
    col2.metric("Content Types", 6)
    col3.metric("AI Provider", "Gemini")
    col4.metric("Currency", "INR ₹")

    st.divider()

    with st.container(border=True):
        st.subheader("About this workspace")
        st.write(
            """
            Product Studio uses Google Gemini to create product descriptions,
            SEO titles, meta descriptions, social media captions, marketing emails,
            and FAQs with Indian Rupee (INR) pricing and SQLite draft storage.
            """
        )
        st.info("Open Content Studio from the sidebar or navigation menu to generate marketing content.")
        st.link_button("Open Aurora 3D Website", "https://product-studio-aurora.onrender.com")

    if drafts:
        st.subheader("Recent Saved Drafts")
        for draft_id, product, kind, content in drafts[:3]:
            with st.expander(f"{product} · {kind} (#{draft_id})", expanded=False):
                st.markdown(content)


elif page == "Content Studio":
    st.title("✨ Content Studio")
    st.write("Generate professional marketing content using Gemini AI.")

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.subheader("Product Information")

            name = st.text_input("Product name")
            price = st.number_input("Price (INR)", min_value=0.0, step=100.0)
            features = st.text_area("Product features", height=140)
            kind = st.selectbox(
                "Content type",
                [
                    "Product description",
                    "SEO title",
                    "Meta description",
                    "Instagram caption",
                    "Marketing email",
                    "FAQs",
                ],
            )
            tone = st.selectbox(
                "Brand tone",
                ["Professional", "Friendly", "Luxury", "Persuasive", "Minimal"],
            )
            instructions = st.text_area("Additional instructions")
            consent = st.checkbox(
                "Allow sending product details to Gemini API (charges may apply)"
            )

            if st.button("Generate AI Content", type="primary", width="stretch"):
                if not name.strip():
                    st.warning("Enter the product name.")
                elif not features.strip():
                    st.warning("Enter the product features.")
                elif not API_KEY:
                    st.error("GEMINI_API_KEY is missing in .env.")
                elif not consent:
                    st.warning("Approve the API request first.")
                else:
                    try:
                        with st.spinner("Generating AI content..."):
                            result = generate_content(
                                name, price, features, kind, tone, instructions
                            )
                            st.session_state["draft"] = result
                        st.success("Content generated successfully!")
                    except Exception as e:
                        error_message = str(e)
                        if API_KEY:
                            error_message = error_message.replace(API_KEY, "[HIDDEN]")
                        st.error(f"Generation failed: {type(e).__name__}")
                        st.code(error_message)

    with right:
        with st.container(border=True):
            st.subheader("Generated Content")
            text = st.text_area("Editable draft", key="draft", height=420)

            save_col, download_col = st.columns(2)
            with save_col:
                if st.button("Save Draft", width="stretch"):
                    if not name.strip():
                        st.warning("Enter a product name.")
                    elif not text.strip():
                        st.warning("Generate content before saving.")
                    else:
                        insert_draft(name.strip(), kind, text)
                        st.success("Draft saved to SQLite!")

            with download_col:
                st.download_button(
                    "Download Draft",
                    data=text,
                    file_name="product_content.txt",
                    mime="text/plain",
                    disabled=not bool(text.strip()),
                    width="stretch",
                )


elif page == "Saved Content":
    st.title("📁 Saved Content")

    rows = fetch_drafts()

    if not rows:
        st.info("No saved drafts yet.")
    else:
        st.success(f"Total saved drafts: {len(rows)}")

        for draft_id, product, kind, content in rows:
            with st.expander(f"{product} · {kind}", expanded=True):
                st.markdown(content)

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download",
                        data=content,
                        file_name=f"draft_{draft_id}.txt",
                        mime="text/plain",
                        key=f"download_{draft_id}",
                    )
                with col2:
                    if st.button("Delete", key=f"delete_{draft_id}"):
                        remove_draft(draft_id)
                        st.rerun()


elif page == "Settings":
    st.title("⚙️ Settings")

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.subheader("🤖 AI Engine Configuration")
            st.write("Provider: Google Gemini")
            st.write(f"Model: {MODEL}")
            if API_KEY:
                st.success("API key configured")
            else:
                st.error("API key not configured")

    with c2:
        with st.container(border=True):
            st.subheader("💻 System Information")
            st.write("Framework: Streamlit")
            st.write("Language: Python")
            st.write("Database: SQLite")
            st.write("Currency: INR ₹")
            st.write(f"Theme: Navy & Gold ({st.session_state['theme_mode']})")
            st.write("Application Icon: 💎")

    st.divider()

    st.subheader("About this project")
    st.write(
        """
        Product Studio is a Generative AI-powered
        product content generation system developed
        for the GENAI-AGENT-020 internship project.

        The application uses Google Gemini to generate
        product descriptions, SEO content, social media
        captions, marketing emails and advertisement copy.
        """
    )

    st.subheader("Technology Stack")
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Language", "Python")
    t2.metric("Framework", "Streamlit")
    t3.metric("AI Engine", "Gemini")
    t4.metric("Storage", "SQLite")

    st.link_button(
        "View GitHub Repository",
        "https://github.com/mgowthamroyal-ux/genai-agent-020",
    )


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="footer">
        💎 PRODUCT STUDIO AI · NAVY & GOLD EDITION
        <br>
        GENAI-AGENT-020 | Powered by Google Gemini
    </div>
    """,
    unsafe_allow_html=True,
)
