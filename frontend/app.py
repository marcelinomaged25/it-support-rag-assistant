import os
import base64
import streamlit as st
from api_client import APIClient

# Streamlit Page Config
st.set_page_config(
    page_title="Enterprise IT Support RAG Assistant",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .citation-card {
        background-color: #F3F4F6;
        border-left: 4px solid #2563EB;
        padding: 0.75rem;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .source-badge {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API Client reading from env
api_client = APIClient()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your **Enterprise IT Support RAG Assistant**. I can help you troubleshoot technical issues across Windows Client OS, Active Directory, Cisco Networking, Linux SELinux, AWS Cloud, CISA Security, and more based on authoritative vendor runbooks.\n\nHow can I help you today?",
            "sources": []
        }
    ]

# Sidebar
with st.sidebar:
    st.title("⚙️ RAG Assistant Settings")
    
    # System Health Check
    st.subheader("System Connection")
    health_data = api_client.check_health()
    if health_data.get("status") == "ok":
        st.success(f"Backend API Connected ({api_client.base_url})")
        st.info(f"Vector Database: {health_data.get('collection_count', 0)} chunks loaded")
        st.info(f"LLM Model: {health_data.get('ollama_model', 'llama3.2:1b')}")
    else:
        st.error(f"Backend API Error: {health_data.get('message', 'Disconnected')}")
        st.caption(f"Configured API URL: `{api_client.base_url}`")
        
    st.divider()
    
    # Parameters
    top_k = st.slider("Retrieval Chunks (Top-K)", min_value=1, max_value=10, value=4)
    
    st.divider()
    
    # Extended Track: Optional Image Attachment
    st.subheader("🖼️ Multimodal Log / Image")
    uploaded_file = st.file_uploader("Upload Error Log / BlueScreen Screenshot", type=["png", "jpg", "jpeg"])
    image_b64 = None
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Attached Visual Input", use_column_width=True)
        bytes_data = uploaded_file.getvalue()
        image_b64 = base64.b64encode(bytes_data).decode("utf-8")
        
    st.divider()
    
    # Quick Preset Questions
    st.subheader("💡 Sample Technical Queries")
    presets = [
        "How do I resolve WinDbg memory dump slow performance diagnostics?",
        "How to fix Windows Update Servicing Failure 0x80070002 & DISM Repair?",
        "How to execute TCP/IP Winsock Reset Protocol on Windows Wi-Fi Adapter?",
        "How to fix Red Hat Enterprise Linux SELinux Access Denied error?",
        "How to troubleshoot Active Directory Kerberos Time Skew issues?"
    ]
    
    for q in presets:
        if st.button(q, key=f"btn_{q}"):
            st.session_state.preset_query = q

    st.divider()
    if st.button("🗑️ Clear Conversation History"):
        st.session_state.messages = []
        st.rerun()

# Main UI Header
st.markdown('<div class="main-header">🛠️ Enterprise IT Support RAG Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Retrieval-Augmented Generation Grounded Technical Support Assistant</div>', unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("📚 View Cited Technical Documentation Sources"):
                for idx, src in enumerate(message["sources"], 1):
                    st.markdown(f"""
                    <div class="citation-card">
                        <span class="source-badge">Source {idx}</span> <b>{src.get('source', 'Master PDF')}</b> (Page {src.get('page', 1)})<br/>
                        <i>"{src.get('content_snippet', '')[:250]}..."</i>
                    </div>
                    """, unsafe_allow_html=True)

# Check if preset was clicked
user_query = st.chat_input("Ask a technical IT support question...")
if hasattr(st.session_state, "preset_query") and st.session_state.preset_query:
    user_query = st.session_state.preset_query
    st.session_state.preset_query = None

# Process User Input
if user_query:
    # Append user question to history
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Call Backend API
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base runbooks & generating grounded technical answer..."):
            res = api_client.query(user_query, top_k=top_k, image_data=image_b64)
            
            if res.get("error"):
                st.error(f"❌ {res.get('message')}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ **Error Processing Query:** {res.get('message')}",
                    "sources": []
                })
            else:
                answer = res.get("answer", "No answer generated.")
                sources = res.get("sources", [])
                
                st.markdown(answer)
                
                if sources:
                    with st.expander("📚 View Cited Technical Documentation Sources"):
                        for idx, src in enumerate(sources, 1):
                            st.markdown(f"""
                            <div class="citation-card">
                                <span class="source-badge">Source {idx}</span> <b>{src.get('source', 'Master PDF')}</b> (Page {src.get('page', 1)})<br/>
                                <i>"{src.get('content_snippet', '')[:250]}..."</i>
                            </div>
                            """, unsafe_allow_html=True)
                            
                # Save assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
