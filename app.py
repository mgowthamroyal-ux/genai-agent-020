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

st.set_page_config(
    page_title="Product Studio",
    page_icon="💎",
    layout="wide",
)

# ==========================================
# NAVY & GOLD THEME STYLING
# ==========================================

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top right, #182952 0%, #0b132b 55%, #070d1e 100%);
            color: #f8fafc;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #080f24 0%, #0d1836 100%);
            border-right: 1px solid rgba(212, 175, 55, 0.28);
        }

        [data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
        }

        h1, h2, h3 {
            color: #f8e39c !important;
            letter-spacing: -0.02em;
        }

        .stMarkdown p, .stMarkdown li, label, .stCaption {
            color: #e2e8f0 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(15, 25, 54, 0.86);
            border: 1px solid rgba(212, 175, 55, 0.30) !important;
            border-radius: 14px !important;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.32);
        }

        [data-testid="stMetric"] {
            background: rgba(15, 25, 54, 0.82);
            border: 1px solid rgba(212, 175, 55, 0.28);
            border-radius: 12px;
            padding: 14px 16px;
        }

        [data-testid="stMetricLabel"] {
            color: #cbd5e1 !important;
        }

        [data-testid="stMetricValue"] {
            color: #f5c542 !important;
            font-weight: 800 !important;
        }

        input, textarea, select, [data-baseweb="select"] > div, [data-baseweb="input"] > div {
            background-color: #0b142c !important;
            color: #f8fafc !important;
            border-color: rgba(212, 175, 55, 0.32) !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #f5c542, #d4af37) !important;
            color: #0b132b !important;
            border: none !important;
            font-weight: 700 !important;
        }

        .stButton > button[kind="secondary"],
        .stDownloadButton > button {
            background: rgba(22, 36, 74, 0.9) !important;
            color: #f8e39c !important;
            border: 1px solid rgba(212, 175, 55, 0.38) !important;
            font-weight: 600 !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            filter: brightness(1.08);
        }

        [data-testid="stExpander"] {
            background: rgba(15, 25, 54, 0.85);
            border: 1px solid rgba(212, 175, 55, 0.28) !important;
            border-radius: 12px !important;
        }

        .footer {
            margin-top: 40px;
            padding: 18px 0 6px 0;
            border-top: 1px solid rgba(212, 175, 55, 0.25);
            text-align: center;
            color: #cbd5e1;
            font-size: 13px;
            line-height: 1.7;
        }
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
# SESSION STATE & SIDEBAR NAVIGATION
# ==========================================

if "draft" not in st.session_state:
    st.session_state["draft"] = ""

st.sidebar.title("💎 Product Studio")
st.sidebar.caption("AI Marketing Workspace")

page = st.sidebar.radio(
    "Workspace",
    ["Dashboard", "Content Studio", "Saved Content", "Settings"],
)

st.sidebar.divider()

if API_KEY:
    st.sidebar.success("Gemini API configured")
else:
    st.sidebar.error("Gemini API key missing")

st.sidebar.caption(f"Model: {MODEL}")
st.sidebar.caption("GENAI-AGENT-020 · INR ₹")


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
        st.info("Open Content Studio from the sidebar to generate marketing content.")
        st.link_button("Open Aurora 3D Website", "http://127.0.0.1:8000")

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
            st.write("Theme: Navy & Gold")
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
