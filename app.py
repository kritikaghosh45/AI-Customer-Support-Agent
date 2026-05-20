import streamlit as st
from agent import CommerceAgent

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ShopEase Support",
    page_icon="🛍️",
    layout="centered",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1rem;
    }
    .header-box h1 { margin: 0; font-size: 1.8rem; }
    .header-box p { margin: 0.3rem 0 0; opacity: 0.9; font-size: 0.95rem; }
    .badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin: 4px 4px 0 0;
    }
    .hint-box {
        background: #eef2ff;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        color: #4a5568;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>🛍️ ShopEase Support</h1>
    <p>AI-powered customer support — available 24/7</p>
    <br>
    <span class="badge">📦 Order Tracking</span>
    <span class="badge">↩️ Returns & Refunds</span>
    <span class="badge">🔍 Product Q&A</span>
    <span class="badge">🎫 Complaints</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get your free key at aistudio.google.com",
    )
    st.caption("🆓 Free at [aistudio.google.com](https://aistudio.google.com)")
    st.divider()
    st.markdown("**🧪 Demo Order IDs**")
    st.markdown("""
| Order ID | Status |
|----------|--------|
| ORD-1001 | Shipped |
| ORD-1002 | Processing |
| ORD-1003 | Delivered ✅ |
| ORD-1004 | Cancelled |
""")
    st.divider()
    st.markdown("**🛒 Available Products**")
    st.markdown("""
- Wireless Headphones
- Running Shoes
- Coffee Maker
- Bluetooth Speaker
- Sports Socks
""")
    st.divider()
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        if "agent" in st.session_state:
            st.session_state.agent.reset()
        st.rerun()

# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None

# ─────────────────────────────────────────────
# Hint Box
# ─────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
<div class="hint-box">
💡 <strong>Try asking:</strong>
"Where is my order ORD-1001?" &nbsp;|&nbsp;
"I want to return ORD-1003" &nbsp;|&nbsp;
"Tell me about the Wireless Headphones" &nbsp;|&nbsp;
"What is your return policy?"
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Chat History
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🛍️"):
        st.markdown(msg["content"])

# ─────────────────────────────────────────────
# Chat Input
# ─────────────────────────────────────────────
if prompt := st.chat_input("How can we help you today?"):
    if not api_key:
        st.error("⚠️ Please enter your Google Gemini API key in the sidebar. Get it free at aistudio.google.com")
        st.stop()

    if st.session_state.agent is None:
        st.session_state.agent = CommerceAgent(api_key=api_key)

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🛍️"):
        with st.spinner("Looking into that for you..."):
            try:
                response = st.session_state.agent.ask(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
