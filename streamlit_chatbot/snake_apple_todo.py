import streamlit as st
import json
import time
import datetime
import random

st.set_page_config(page_title="🐍🍎 Snake & Apple To-Do", layout="centered")

# --- CSS Styling ---
snake_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
html, body {
    background: linear-gradient(135deg, #5DAE4A, #C03221);
    font-family: 'Press Start 2P', monospace;
    color: #FFF;
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

st.title("🐍🍎 Snake & Apple To-Do List")

# --- Helper Functions ---
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

def count_weekly(tasks):
    now = datetime.datetime.now()
    one_week_ago = now - datetime.timedelta(days=7)
    return sum(1 for task in tasks if task['done'] and datetime.datetime.strptime(task['done_time'], "%Y-%m-%d %H:%M:%S") > one_week_ago)

# --- Initialize Session ---
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()
if "pomodoro_running" not in st.session_state:
    st.session_state.pomodoro_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# --- Add New Task ---
st.subheader("➕ Add a Task")
with st.form("new_task_form", clear_on_submit=True):
    task_text = st.text_input("Task")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    submit = st.form_submit_button("Add Task")
    if submit and task_text.strip():
        st.session_state.tasks.append({
            "task": task_text.strip(),
            "priority": priority,
            "done": False,
            "done_time": ""
        })
        save_tasks(st.session_state.tasks)

# --- Display Tasks ---
st.subheader("📋 Tasks")
priorities = {"High": "🔥", "Medium": "🍏", "Low": "🐛"}
snake_emojis = ["🐍", "🍎", "🌟", "🔥", "💥", "💚"]

for i, task in enumerate(st.session_state.tasks):
    cols = st.columns([0.1, 0.6, 0.2, 0.1])
    new_done = cols[0].checkbox("", value=task["done"], key=f"check_{i}")
    st.session_state.tasks[i]["done"] = new_done

    task_display = f"{priorities[task['priority']]} {task['task']}"
    css_class = "done" if new_done else ""
    cols[1].markdown(f"<div class='task-box {css_class}'>{task_display}</div>", unsafe_allow_html=True)

    if cols[2].button("🗑️", key=f"del_{i}"):
        st.session_state.tasks.pop(i)
        save_tasks(st.session_state.tasks)
        st.experimental_rerun()

    if new_done and not task["done_time"]:
        st.session_state.tasks[i]["done_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success("✅ Task completed! Reward: " + "".join(random.choices(snake_emojis, k=10)))
        st.balloons()

save_tasks(st.session_state.tasks)

# --- Pomodoro Timer ---
st.subheader("⏲️ Pomodoro Timer")
if st.button("Start Pomodoro"):
    st.session_state.pomodoro_running = True
    st.session_state.start_time = time.time()

if st.session_state.pomodoro_running:
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = 25 * 60 - elapsed
    if remaining > 0:
        mins, secs = divmod(remaining, 60)
        st.info(f"Focus Time Remaining: {mins:02d}:{secs:02d}")
    else:
        st.success("⏰ Pomodoro complete! Take a 5-min break!")
        st.session_state.pomodoro_running = False

# --- Weekly Analysis ---
st.subheader("📊 Weekly Summary")
weekly_done = count_weekly(st.session_state.tasks)
st.metric("Tasks Completed This Week", weekly_done)

# --- Reminder ---
st.subheader("🔔 Reminder")
st.caption("Don’t forget to check your High Priority tasks today!")