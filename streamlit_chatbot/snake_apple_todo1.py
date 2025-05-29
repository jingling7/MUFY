import streamlit as st
import json
import random
from datetime import datetime

# Set page config
st.set_page_config(page_title="🐍🍎 Snake & Apple To-Do", layout="centered")

# --- Snake & Apple themed styles ---
snake_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

html, body {
    background: linear-gradient(135deg, #5DAE4A, #C03221);
    font-family: 'Press Start 2P', monospace;
    color: #FFF;
}

h1, h2, h3 {
    color: #F7F757;
}

.stButton > button {
    background-color: #4A772B;
    color: white;
    border: 2px solid #D94F3D;
    border-radius: 10px;
    padding: 8px 20px;
}

.stButton > button:hover {
    background-color: #D94F3D;
    color: black;
}

.task-box {
    background-color: #1E3D1A;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 10px;
    border: 2px solid #FF4444;
    font-size: 14px;
}

.done {
    text-decoration: line-through;
    color: #aaa;
}
</style>
"""
st.markdown(snake_css, unsafe_allow_html=True)

# Page title
st.title("🐍🍎 Snake & Apple To-Do List")

# Data setup
TASK_FILE = "tasks.json"

def load_tasks():
    try:
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f)

# Load tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

# New task form
with st.form("add_task", clear_on_submit=True):
    new_task = st.text_input("New task")
    submitted = st.form_submit_button("Add Task")
    if submitted and new_task.strip():
        st.session_state.tasks.append({"task": new_task.strip(), "done": False})
        save_tasks(st.session_state.tasks)

# Display tasks
st.subheader("📋 Your Tasks")

snake_emojis = ["🐍", "🍎", "🌟", "🔥", "💥", "💚"]

for i, task in enumerate(st.session_state.tasks):
    cols = st.columns([0.1, 0.7, 0.2])
    was_done = task["done"]

    # Checkbox
    new_done = cols[0].checkbox("", value=task["done"], key=i)
    st.session_state.tasks[i]["done"] = new_done

    # Show task
    task_class = "done" if new_done else ""
    cols[1].markdown(f"<div class='task-box {task_class}'>{task['task']}</div>", unsafe_allow_html=True)

    # Delete
    if cols[2].button("🗑️", key=f"delete_{i}"):
        st.session_state.tasks.pop(i)
        save_tasks(st.session_state.tasks)
        st.experimental_rerun()

    # 🎉 Reward: Show snake emojis only when a task was just marked as done
    if new_done and not was_done:
        st.success("✅ Task completed! Here’s your reward:")
        st.markdown("".join(random.choices(snake_emojis, k=20)))
        st.balloons()

# Save changes
save_tasks(st.session_state.tasks)


