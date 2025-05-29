import streamlit as st
import json
import base64
from datetime import datetime
import requests
from io import BytesIO
import time

# Page configuration
st.set_page_config(
    page_title="🐱 Cat To-Do List",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colorful cat theme
def load_css():
    st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        background-attachment: fixed;
    }
    
    /* Header styling */
    .cat-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .cat-title {
        font-size: 3rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0;
        font-family: 'Comic Sans MS', cursive;
    }
    
    /* To-do item styling */
    .todo-item {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 3px solid #ff6b6b;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .todo-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Completed item styling */
    .completed-item {
        background: linear-gradient(135deg, #c3f0ca 0%, #fce38a 100%);
        opacity: 0.7;
        text-decoration: line-through;
    }
    
    /* Cat decorations */
    .cat-decoration {
        font-size: 2rem;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        border: none;
        border-radius: 25px;
        color: white;
        font-weight: bold;
        transition: transform 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 15px;
        border: 2px solid #ff9a9e;
    }
    
    .stSelectbox > div > div > div {
        border-radius: 15px;
        border: 2px solid #ff9a9e;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'todos' not in st.session_state:
        st.session_state.todos = []
    if 'cat_sounds' not in st.session_state:
        st.session_state.cat_sounds = True

# Cat sound function
def play_meow_sound():
    if st.session_state.cat_sounds:
        # HTML5 audio with base64 encoded meow sound (placeholder)
        st.markdown("""
        <audio autoplay>
            <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgM" type="audio/wav">
        </audio>
        """, unsafe_allow_html=True)

# Cat images (using placeholder cat images)
def get_random_cat_image():
    cat_images = [
        "🐱", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾"
    ]
    import random
    return random.choice(cat_images)

# Load and display header
def display_header():
    st.markdown("""
    <div class="cat-header">
        <h1 class="cat-title">🐱 Meow-nificent To-Do List 🐱</h1>
        <p style="color: white; font-size: 1.2rem;">Stay paw-ductive with your feline friend!</p>
    </div>
    """, unsafe_allow_html=True)

# Add new todo
def add_todo():
    with st.form("add_todo_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_task = st.text_input("What needs to be done? 🎯", placeholder="Feed the cat, clean litter box...")
        
        with col2:
            priority = st.selectbox("Priority", ["🔴 High", "🟡 Medium", "🟢 Low"])
        
        category = st.selectbox("Category", ["🏠 Personal", "💼 Work", "🛒 Shopping", "🎯 Goals", "🐱 Cat Care"])
        
        submit_button = st.form_submit_button("Add Task 🐾")
        
        if submit_button and new_task:
            todo_item = {
                "id": len(st.session_state.todos),
                "task": new_task,
                "priority": priority,
                "category": category,
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cat_emoji": get_random_cat_image()
            }
            st.session_state.todos.append(todo_item)
            play_meow_sound()
            st.success("Task added! Your cat is proud! 🐱✨")
            st.rerun()

# Display todos
def display_todos():
    if not st.session_state.todos:
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2>🐱 No tasks yet!</h2>
            <p style="font-size: 1.2rem;">Your cat is waiting for some tasks to pounce on!</p>
            <div class="cat-decoration">😴</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Filter options
    st.sidebar.markdown("### 🎛️ Filter Tasks")
    show_completed = st.sidebar.checkbox("Show completed tasks", value=True)
    category_filter = st.sidebar.selectbox("Filter by category", 
                                         ["All"] + list(set([todo["category"] for todo in st.session_state.todos])))
    priority_filter = st.sidebar.selectbox("Filter by priority", 
                                         ["All", "🔴 High", "🟡 Medium", "🟢 Low"])
    
    # Filter todos
    filtered_todos = st.session_state.todos.copy()
    
    if not show_completed:
        filtered_todos = [todo for todo in filtered_todos if not todo["completed"]]
    
    if category_filter != "All":
        filtered_todos = [todo for todo in filtered_todos if todo["category"] == category_filter]
    
    if priority_filter != "All":
        filtered_todos = [todo for todo in filtered_todos if todo["priority"] == priority_filter]
    
    # Display filtered todos
    for i, todo in enumerate(filtered_todos):
        with st.container():
            col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])
            
            with col1:
                st.markdown(f"<div class='cat-decoration'>{todo['cat_emoji']}</div>", unsafe_allow_html=True)
            
            with col2:
                checkbox_key = f"todo_{todo['id']}"
                completed = st.checkbox("", value=todo["completed"], key=checkbox_key)
                
                if completed != todo["completed"]:
                    st.session_state.todos[todo['id']]["completed"] = completed
                    if completed:
                        play_meow_sound()
                        st.balloons()
                    st.rerun()
                
                task_style = "completed-item" if todo["completed"] else "todo-item"
                st.markdown(f"""
                <div class="{task_style}">
                    <h4>{todo['task']}</h4>
                    <p><strong>Priority:</strong> {todo['priority']} | <strong>Category:</strong> {todo['category']}</p>
                    <small>Created: {todo['created_at']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if st.button("🗑️", key=f"delete_{todo['id']}", help="Delete task"):
                    st.session_state.todos = [t for t in st.session_state.todos if t['id'] != todo['id']]
                    st.rerun()
            
            with col4:
                if st.button("📝", key=f"edit_{todo['id']}", help="Edit task"):
                    st.session_state.editing_todo = todo['id']

# Statistics
def display_stats():
    if st.session_state.todos:
        total_tasks = len(st.session_state.todos)
        completed_tasks = len([todo for todo in st.session_state.todos if todo["completed"]])
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tasks", total_tasks, delta=None)
        
        with col2:
            st.metric("Completed", completed_tasks, delta=None)
        
        with col3:
            st.metric("Remaining", total_tasks - completed_tasks, delta=None)
        
        with col4:
            st.metric("Completion Rate", f"{completion_rate:.1f}%", delta=None)
        
        # Progress bar
        st.progress(completion_rate / 100)
        
        if completion_rate == 100 and total_tasks > 0:
            st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <h2>🎉 Congratulations! 🎉</h2>
                <p style="font-size: 1.5rem;">Your cat is purring with pride! All tasks completed! 🐱💖</p>
                <div class="cat-decoration">😸🎊😸</div>
            </div>
            """, unsafe_allow_html=True)

# Sidebar options
def display_sidebar():
    st.sidebar.markdown("### 🐾 Cat Settings")
    
    # Sound toggle
    st.session_state.cat_sounds = st.sidebar.checkbox("Enable meow sounds 🔊", value=st.session_state.cat_sounds)
    
    # Clear all tasks
    if st.sidebar.button("🗑️ Clear All Tasks"):
        if st.sidebar.button("⚠️ Confirm Clear All"):
            st.session_state.todos = []
            st.sidebar.success("All tasks cleared! 🐱")
            st.rerun()
    
    # Export/Import
    st.sidebar.markdown("### 📁 Data Management")
    
    if st.sidebar.button("📥 Export Tasks"):
        if st.session_state.todos:
            json_data = json.dumps(st.session_state.todos, indent=2)
            st.sidebar.download_button(
                label="💾 Download JSON",
                data=json_data,
                file_name=f"cat_todos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    uploaded_file = st.sidebar.file_uploader("📤 Import Tasks", type="json")
    if uploaded_file is not None:
        try:
            imported_todos = json.load(uploaded_file)
            st.session_state.todos.extend(imported_todos)
            st.sidebar.success("Tasks imported successfully! 🐱")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error importing tasks: {e}")

# Main app
def main():
    load_css()
    init_session_state()
    
    display_header()
    display_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📝 Tasks", "📊 Statistics", "🎨 Cat Gallery"])
    
    with tab1:
        st.markdown("### ✨ Add New Task")
        add_todo()
        
        st.markdown("### 📋 Your Tasks")
        display_todos()
    
    with tab2:
        st.markdown("### 📊 Task Statistics")
        display_stats()
        
        # Additional charts could go here
        if st.session_state.todos:
            st.markdown("### 📈 Category Breakdown")
            categories = {}
            for todo in st.session_state.todos:
                cat = todo["category"]
                categories[cat] = categories.get(cat, 0) + 1
            
            st.bar_chart(categories)
    
    with tab3:
        st.markdown("### 🎨 Cat Gallery")
        st.markdown("Here are some cute cats to motivate you! 🐱")
        
        # Display a grid of cat emojis
        cat_cols = st.columns(6)
        cats = ["🐱", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾", "🐈", "🐈‍⬛", "🦁"]
        
        for i, cat in enumerate(cats):
            with cat_cols[i % 6]:
                if st.button(cat, key=f"cat_{i}"):
                    play_meow_sound()
                    st.toast(f"Meow! {cat}")

if __name__ == "__main__":
    main()
