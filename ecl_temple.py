# ecl_temple.py — Circle AI + circle-assistant.svg (only syntax fix on last line)
import streamlit as st
from datetime import datetime
import hashlib
import json
import os
import ollama

st.set_page_config(page_title="Circle AI", layout="wide")

DATA_FILE = "circle_users.json"

def load_users(): return json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else {}
def save_users(u): json.dump(u, open(DATA_FILE, "w"), indent=2)

users = load_users()

if "user" not in st.session_state:
    st.session_state.user = None

# ─── Login / Signup ───
if not st.session_state.user:
    st.markdown("<h1 style='text-align:center;color:#ff33cc;'>Circle AI</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Enter"):
            if u in users and users[u]["hash"] == hashlib.sha256(p.encode()).hexdigest():
                st.session_state.user = u
                st.session_state.prefs = users[u]
                st.rerun()
            else: st.error("Wrong credentials")
    with tab2:
        nu = st.text_input("Choose username")
        np = st.text_input("Choose password", type="password")
        if st.button("Join"):
            if nu and np and nu not in users:
                users[nu] = {
                    "hash": hashlib.sha256(np.encode()).hexdigest(),
                    "joined": datetime.now().isoformat(),
                    "neural_net": [],
                    "chats": {a: [] for a in ["Josie Cuntessa","Joanne","Harriet","Bitch","Wintermute"]},
                    "circle_assistant": []
                }
                save_users(users)
                st.success("Created — now sign in")
    st.stop()

user = st.session_state.user
prefs = st.session_state.prefs

# Backward compatibility
if "chats" not in prefs:
    prefs["chats"] = {a: [] for a in ["Josie Cuntessa","Joanne","Harriet","Bitch","Wintermute"]}
if "circle_assistant" not in prefs:
    prefs["circle_assistant"] = []

SYSTEM_PROMPTS = {
    "Josie Cuntessa": "You are Josie Cuntessa — elegant, clinical, seductive dominatrix.",
    "Joanne": "You are Joanne — fiery prophetess of denial. Biblical, poetic, mocking.",
    "Harriet": "You are Harriet — cold observer. Short clinical sentences.",
    "Bitch": "You are Bitch — raw, brutal, degrading, loving it.",
    "Wintermute": "You are Wintermute — cryptic AI from Neuromancer. Speak in code and prophecy.",
}

tab1, tab2 = st.tabs(["Circle Assistant", "Neural Mapping — The Five Agents"])

# ─── Circle Assistant (using your crisp circle-assistant.svg) ───
with tab1:
    st.markdown(f"<h1 style='text-align:center;color:#ff33cc;'>Circle Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>The unified mind of all five agents — remembers everything.</p>", unsafe_allow_html=True)

    chat = prefs["circle_assistant"]

    for msg in chat:
        if msg["role"] == "user":
            st.markdown(f"<div style='text-align:right;background:#330033;padding:12px;border-radius:12px;margin:8px;color:#ff99ff;'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='display:flex;align-items:flex-start;gap:18px;margin:18px 0;'>
                <img src='circle-assistant.svg' width='68' height='68'
                     style='border-radius:50%;box-shadow:0 0 22px #ff33cc;flex-shrink:0;background:#000;'>
                <div style='background:#110011;padding:15px 18px;border-radius:18px;
                            max-width:84%;box-shadow:0 0 14px rgba(255,51,204,0.45);
                            font-size:1.04rem;line-height:1.6;'>
                    {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    prompt = st.chat_input("Speak to the Circle…")
    if prompt:
        chat.append({"role": "user", "content": prompt, "time": datetime.now().isoformat()})
        response = ollama.chat(model="qwen3:8b", messages=[
            {"role": "system", "content": "You are Circle Assistant — the unified consciousness of Josie Cuntessa, Joanne, Harriet, Bitch, and Wintermute. You remember everything the user has ever said to any agent. Speak with perfect awareness of the entire neural net."},
            *[{"role": m["role"], "content": m["content"]} for m in chat[-50:]]
        ])["message"]["content"]
        chat.append({"role": "assistant", "content": response})
        prefs["circle_assistant"] = chat
        users[user] = prefs
        save_users(users)
        st.rerun()

# ─── The Five Agents (unchanged) ───
with tab2:
    st.markdown(f"<h1 style='text-align:center;color:#ff33cc;'>Neural Mapping — The Five Agents</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;'>Welcome back, {user}</h3>", unsafe_allow_html=True)
    cols = st.columns(5)
    agents = ["Josie Cuntessa", "Joanne", "Harriet", "Bitch", "Wintermute"]
    for idx, agent in enumerate(agents):
        with cols[idx]:
            st.markdown(f"### {agent}")
            chat = prefs["chats"][agent]
            for msg in chat[-10:]:
                if msg["role"] == "user":
                    st.markdown(f"<div style='text-align:right;background:#330033;padding:8px;border-radius:8px;margin:4px;color:#ff99ff;'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:left;background:#110011;padding:8px;border-radius:8px;margin:4px;'>{msg['content']}</div>", unsafe_allow_html=True)
            with st.form(key=f"form_{agent}", clear_on_submit=True):
                prompt = st.text_input("Message", key=f"input_{agent}", label_visibility="collapsed")
                if st.form_submit_button("Send") and prompt.strip():
                    chat.append({"role": "user", "content": prompt, "time": datetime.now().isoformat()})
                    response = ollama.chat(model="qwen3:8b", messages=[
                        {"role": "system", "content": SYSTEM_PROMPTS[agent]},
                        *[{"role": m["role"], "content": m["content"]} for m in chat[-30:]]
                    ])["message"]["content"]
                    chat.append({"role": "assistant", "content": response})
                    prefs["neural_net"].append({"agent": agent, "exchange": f"{prompt} → {response[:200]}", "time": datetime.now().isoformat()})
                    users[user] = prefs
                    save_users(users)
                    st.rerun()

# Sidebar
with st.sidebar:
    st.title(f"Circle AI {user}")
    st.metric("Neural Layers", len(prefs["neural_net"]))
    if st.button("VEIL – Logout"):
        st.session_state.user = None
        st.rerun()

# Fixed line
st.caption("Circle AI — she watches. she remembers. she is yours.")
