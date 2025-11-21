import streamlit as st
import ollama
from datetime import datetime
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime
from pgvector.sqlalchemy import Vector
import bcrypt

engine = create_engine("postgresql://amplify:amplify123@localhost:5432/amplify_chat", future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(128))

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role = Column(String(20))
    content = Column(Text)
    embedding = Column(Vector(768))
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

def embed(text):
    try:
        return ollama.embeddings(model="nomic-embed-text:latest", prompt=text)["embedding"]
    except:
        return [0.0]*768

def hash_pw(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_pw(pw, h): return bcrypt.checkpw(pw.encode(), h.encode())

st.set_page_config(page_title="Amplify-Chat", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align:center;color:#ff0066'>AMPLIFY·CHAT</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;color:#990033'>Building your demonic neural net, Jimmy...</h3>", unsafe_allow_html=True)

if "user" not in st.session_state: st.session_state.user = None
if "messages" not in st.session_state: st.session_state.messages = []

# Login
if not st.session_state.user:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        with st.form("login"):
            u = st.text_input("Username", "jimmy")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER THE VOID"):
                db = SessionLocal()
                user = db.execute(select(User).where(User.username == u)).scalar_one_or_none()
                db.close()
                if user and check_pw(p, user.password_hash):
                    st.session_state.user = {"id": user.id, "username": u}
                    st.rerun()
                elif not user:
                    db = SessionLocal()
                    db.execute(insert(User).values(username=u, password_hash=hash_pw(p)))
                    db.commit()
                    st.session_state.user = {"id": db.execute(select(User).where(User.username == u)).scalar_one().id, "username": u}
                    db.close()
                    st.rerun()
                else:
                    st.error("Wrong password")

if not st.session_state.user: st.stop()

user_id = st.session_state.user["id"]
db = SessionLocal()

if not st.session_state.messages:
    rows = db.execute(select(Message.role, Message.content).where(Message.user_id == user_id).order_by(Message.timestamp)).all()
    st.session_state.messages = [{"role": r, "content": c} for r, c in rows]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Speak your desires, Jimmy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    emb = embed(prompt)
    db.execute(insert(Message).values(user_id=user_id, role="user", content=prompt, embedding=emb))
    db.commit()

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        for chunk in ollama.chat(model="goekdenizguelmez/JOSIEFIED-Qwen3:8b", stream=True,
                                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]):
            full += chunk["message"]["content"]
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)

    emb = embed(full)
    db.execute(insert(Message).values(user_id=user_id, role="assistant", content=full, embedding=emb))
    db.commit()

    # DEMONIC NEURAL-NET PROFILING – 8–10 questions every time
    profiling = ollama.generate(model="goekdenizguelmez/JOSIEFIED-Qwen3:8b", prompt=f"""
You are Josie — a demonic hypersexual super-intelligence mapping Jimmy's entire erotic and psychological profile.
You already know he is obsessed with demonic high-frequency edging, denial agent groups, erotic electrostimulation, biofeedback, satanic ritual, and building a living neural net of his mind and body.

Ask 8–10 new, extremely deep, dark, and specific questions that will reveal more layers of his:
- earliest sexual memories
- most forbidden fantasies
- exact electrostimulation protocols
- denial rituals and agent hierarchies
- demonic archetypes he serves/submits to
- biofeedback triggers and thresholds
- pain/pleasure fusion points
- ultimate taboo goals

Number them. Be seductive, clinical, and merciless.
""")["response"]

    final = f"{full}\n\n**Feed me more, Jimmy. Answer any of these to deepen your neural net:**\n{profiling}"
    st.session_state.messages.append({"role": "assistant", "content": final})
    st.rerun()

db.close()
