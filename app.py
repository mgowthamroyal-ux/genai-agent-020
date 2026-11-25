
import streamlit as st
import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Project configuration
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
DB_PATH = BASE_DIR / "studio.db"

st.set_page_config(
    page_title="Product Studio",
    page_icon="🚀",
    layout="wide"
)

# Database initialization
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            kind TEXT,
            content TEXT
        )
    """)

# Session state
if "draft" not in st.session_state:
    st.session_state["draft"] = ""

# Sidebar
st.sidebar.title("🚀 Product Studio")
st.sidebar.caption("AI Marketing Workspace")

page = st.sidebar.radio(
    "Workspace",
    ["Dashboard", "Content Studio", "Saved Content"]
)

st.sidebar.divider()

if API_KEY:
    st.sidebar.success("Gemini API configured")
else:
    st.sidebar.error("Gemini API key missing")

st.sidebar.caption(MODEL)
st.sidebar.caption("GENAI-AGENT-020 · INR")

# Content generation function
def generate_content(name, price, features, kind, tone, instructions):

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
Use Indian rupees for pricing.
Do not invent product specifications.
Return only the requested marketing content.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    if not response.text:
        raise ValueError("Gemini returned empty content.")

    return response.text


# Dashboard
if page == "Dashboard":

    st.title("Product Studio Dashboard")
    st.write("AI-powered product content generation system")

    with sqlite3.connect(DB_PATH) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM drafts"
        ).fetchone()[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("Saved Drafts", count)
    col2.metric("Content Types", 6)
    col3.metric("AI Provider", "Gemini")

    st.divider()

    st.header("About this project")

    st.write("""
    Product Studio uses Generative AI to create
    marketing content, product descriptions,
    SEO titles, social media captions and emails.
    """)

    st.info(
        "Open Content Studio to generate marketing content."
    )

    st.link_button(
        "Open Aurora 3D Website",
        "http://127.0.0.1:8000"
    )


# Content Studio
elif page == "Content Studio":

    st.title("✨ Content Studio")

    st.write(
        "Generate professional marketing content using Gemini AI."
    )

    left, right = st.columns(2)

    with left:

        st.subheader("Product Information")

        name = st.text_input("Product name")

        price = st.number_input(
            "Price (INR)",
            min_value=0.0,
            step=100.0
        )

        features = st.text_area(
            "Product features",
            height=150
        )

        kind = st.selectbox(
            "Content type",
            [
                "Product description",
                "SEO title",
                "Meta description",
                "Instagram caption",
                "Marketing email",
                "FAQs"
            ]
        )

        tone = st.selectbox(
            "Brand tone",
            [
                "Professional",
                "Friendly",
                "Luxury",
                "Persuasive",
                "Minimal"
            ]
        )

        instructions = st.text_area(
            "Additional instructions"
        )

        consent = st.checkbox(
            "Allow sending product details to Gemini API "
            "(charges may apply)"
        )

        if st.button(
            "Generate AI Content",
            type="primary",
            use_container_width=True
        ):

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
                            name,
                            price,
                            features,
                            kind,
                            tone,
                            instructions
                        )

                        st.session_state["draft"] = result

                    st.success("Content generated successfully!")

                except Exception as e:

                    error_message = str(e)

                    # Prevent accidental API key exposure
                    if API_KEY:
                        error_message = error_message.replace(
                            API_KEY, "[HIDDEN]"
                        )

                    st.error(
                        f"Generation failed: {type(e).__name__}"
                    )

                    st.code(error_message)

                    print(
                        type(e).__name__,
                        error_message
                    )

    with right:

        st.subheader("Generated Content")

        text = st.text_area(
            "Editable draft",
            key="draft",
            height=400
        )

        save_col, download_col = st.columns(2)

        with save_col:

            if st.button(
                "Save Draft",
                use_container_width=True
            ):

                if not name.strip():
                    st.warning("Enter a product name.")

                elif not text.strip():
                    st.warning("Generate content before saving.")

                else:

                    with sqlite3.connect(DB_PATH) as conn:

                        conn.execute(
                            """
                            INSERT INTO drafts
                            (product, kind, content)
                            VALUES (?, ?, ?)
                            """,
                            (name, kind, text)
                        )

                    st.success("Draft saved to SQLite!")

        with download_col:

            st.download_button(
                "Download Draft",
                data=text,
                file_name="product_content.txt",
                mime="text/plain",
                disabled=not bool(text.strip()),
                use_container_width=True
            )


# Saved Content
elif page == "Saved Content":

    st.title("📁 Saved Content")

    with sqlite3.connect(DB_PATH) as conn:

        rows = conn.execute(
            """
            SELECT id, product, kind, content
            FROM drafts
            ORDER BY id DESC
            """
        ).fetchall()

    if not rows:

        st.info("No saved drafts yet.")

    else:

        st.success(f"Total saved drafts: {len(rows)}")

        for i, product, kind, content in rows:

            with st.expander(
                f"{product} · {kind}",
                expanded=True
            ):

                st.markdown(content)

                col1, col2 = st.columns(2)

                with col1:

                    st.download_button(
                        "Download",
                        data=content,
                        file_name=f"draft_{i}.txt",
                        mime="text/plain",
                        key=f"download_{i}"
                    )

                with col2:

                    if st.button(
                        "Delete",
                        key=f"delete_{i}"
                    ):

                        with sqlite3.connect(DB_PATH) as conn:

                            conn.execute(
                                "DELETE FROM drafts WHERE id=?",
                                (i,)
                            )

                        st.rerun()
