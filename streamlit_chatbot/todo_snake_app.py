import streamlit as st
import random
import time
from datetime import datetime, date, timedelta

# Set page config
st.set_page_config(
    page_title="🐍 Ultimate Todo Gaming Hub",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with green/red theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(45deg, #2E7D32, #C62828);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: bold;
    }
    .todo-container {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #4CAF50 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 32px rgba(76, 175, 80, 0.3);
    }
    .game-container {
        background: linear-gradient(135deg, #C62828 0%, #D32F2F 50%, #F44336 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 32px rgba(244, 67, 54, 0.3);
    }
    .todo-item {
        background: rgba(255,255,255,0.15);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #FFD93D;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .todo-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(255,255,255,0.2);
    }
    .todo-completed {
        background: rgba(76, 175, 80, 0.4);
        text-decoration: line-through;
        opacity: 0.8;
        border-left-color: #4CAF50;
    }
    .todo-overdue {
        background: rgba(244, 67, 54, 0.4);
        border-left-color: #F44336;
        animation: pulse-red 2s infinite;
    }
    .todo-urgent {
        background: rgba(255, 152, 0, 0.4);
        border-left-color: #FF9800;
        animation: pulse-orange 2s infinite;
    }
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 5px rgba(244, 67, 54, 0.5); }
        50% { box-shadow: 0 0 20px rgba(244, 67, 54, 0.8); }
    }
    @keyframes pulse-orange {
        0%, 100% { box-shadow: 0 0 5px rgba(255, 152, 0, 0.5); }
        50% { box-shadow: 0 0 20px rgba(255, 152, 0, 0.8); }
    }
    .category-work { border-left-color: #2196F3; }
    .category-personal { border-left-color: #9C27B0; }
    .category-learning { border-left-color: #FF9800; }
    .category-health { border-left-color: #4CAF50; }
    .game-board {
        background: linear-gradient(45deg, #1B5E20, #2E7D32);
        border: 4px solid #4CAF50;
        border-radius: 15px;
        font-family: monospace;
        font-size: 18px;
        line-height: 22px;
        text-align: center;
        padding: 15px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(76, 175, 80, 0.4);
    }
    .game-stats {
        background: rgba(255,255,255,0.15);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .achievement-badge {
        background: linear-gradient(45deg, #FFD700, #FFA000);
        color: #1B5E20;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        display: inline-block;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        animation: shimmer 2s infinite;
    }
    @keyframes shimmer {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    .reward-unlock {
        background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        animation: celebration 3s infinite;
        color: white;
        font-weight: bold;
    }
    @keyframes celebration {
        0%, 100% { transform: scale(1); }
        25% { transform: scale(1.02) rotate(1deg); }
        75% { transform: scale(1.02) rotate(-1deg); }
    }
    .memory-card {
        width: 60px;
        height: 60px;
        background: #2E7D32;
        border: 3px solid #4CAF50;
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 5px;
        cursor: pointer;
        font-size: 24px;
        transition: all 0.3s ease;
    }
    .memory-card:hover {
        background: #4CAF50;
        transform: scale(1.1);
    }
    .memory-card.flipped {
        background: #FFD93D;
        color: #1B5E20;
    }
    .memory-card.matched {
        background: #4CAF50;
        opacity: 0.7;
    }
    .tic-tac-cell {
        width: 80px;
        height: 80px;
        background: #2E7D32;
        border: 3px solid #4CAF50;
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 2px;
        cursor: pointer;
        font-size: 32px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .tic-tac-cell:hover {
        background: #4CAF50;
        transform: scale(1.05);
    }
    .stats-container {
        background: linear-gradient(135deg, #1B5E20 0%, #C62828 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    # Todo List State
    if 'todos' not in st.session_state:
        st.session_state.todos = []
    if 'completed_today' not in st.session_state:
        st.session_state.completed_today = 0
    if 'last_completion_date' not in st.session_state:
        st.session_state.last_completion_date = date.today()
    
    # Snake Game State
    if 'game_active' not in st.session_state:
        st.session_state.game_active = False
    if 'snake' not in st.session_state:
        st.session_state.snake = [[5, 5]]
    if 'apple' not in st.session_state:
        st.session_state.apple = [10, 10]
    if 'direction' not in st.session_state:
        st.session_state.direction = 'RIGHT'
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'high_score' not in st.session_state:
        st.session_state.high_score = 0
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'board_size' not in st.session_state:
        st.session_state.board_size = 15
    
    # Memory Game State
    if 'memory_cards' not in st.session_state:
        st.session_state.memory_cards = []
    if 'memory_flipped' not in st.session_state:
        st.session_state.memory_flipped = []
    if 'memory_matched' not in st.session_state:
        st.session_state.memory_matched = []
    if 'memory_score' not in st.session_state:
        st.session_state.memory_score = 0
    if 'memory_moves' not in st.session_state:
        st.session_state.memory_moves = 0
    
    # Tic Tac Toe State
    if 'ttt_board' not in st.session_state:
        st.session_state.ttt_board = ['' for _ in range(9)]
    if 'ttt_current_player' not in st.session_state:
        st.session_state.ttt_current_player = 'X'
    if 'ttt_winner' not in st.session_state:
        st.session_state.ttt_winner = None
    if 'ttt_wins' not in st.session_state:
        st.session_state.ttt_wins = {'X': 0, 'O': 0, 'Draw': 0}

class TodoManager:
    """Enhanced Todo Manager with categories and due dates"""
    
    @staticmethod
    def add_todo(task, priority="Medium", category="Personal", due_date=None):
        """Add a new todo item with enhanced features"""
        new_todo = {
            'id': len(st.session_state.todos) + 1,
            'task': task,
            'priority': priority,
            'category': category,
            'completed': False,
            'created_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'due_date': due_date.strftime("%Y-%m-%d") if due_date else None,
            'completed_date': None
        }
        st.session_state.todos.append(new_todo)
    
    @staticmethod
    def complete_todo(todo_id):
        """Mark a todo as completed"""
        for todo in st.session_state.todos:
            if todo['id'] == todo_id and not todo['completed']:
                todo['completed'] = True
                todo['completed_date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Update daily completion count
                today = date.today()
                if st.session_state.last_completion_date != today:
                    st.session_state.completed_today = 0
                    st.session_state.last_completion_date = today
                
                st.session_state.completed_today += 1
                return True
        return False
    
    @staticmethod
    def delete_todo(todo_id):
        """Delete a todo item"""
        st.session_state.todos = [todo for todo in st.session_state.todos if todo['id'] != todo_id]
    
    @staticmethod
    def get_todos_by_category(category=None):
        """Get todos filtered by category"""
        if category:
            return [todo for todo in st.session_state.todos if todo['category'] == category and not todo['completed']]
        return [todo for todo in st.session_state.todos if not todo['completed']]
    
    @staticmethod
    def get_overdue_todos():
        """Get overdue todos"""
        today = date.today()
        overdue = []
        for todo in st.session_state.todos:
            if (not todo['completed'] and todo['due_date'] and 
                datetime.strptime(todo['due_date'], "%Y-%m-%d").date() < today):
                overdue.append(todo)
        return overdue
    
    @staticmethod
    def get_urgent_todos():
        """Get todos due within 3 days"""
        today = date.today()
        urgent_date = today + timedelta(days=3)
        urgent = []
        for todo in st.session_state.todos:
            if (not todo['completed'] and todo['due_date'] and 
                today <= datetime.strptime(todo['due_date'], "%Y-%m-%d").date() <= urgent_date):
                urgent.append(todo)
        return urgent
    
    @staticmethod
    def get_completed_todos():
        """Get all completed todos"""
        return [todo for todo in st.session_state.todos if todo['completed']]

class EnhancedSnakeGame:
    """Enhanced Snake Game with productivity-based rewards"""
    
    @staticmethod
    def get_max_snake_length():
        """Calculate max snake length based on completed tasks"""
        base_length = 5
        bonus_length = st.session_state.completed_today * 2
        return base_length + bonus_length
    
    @staticmethod
    def get_board_size():
        """Dynamic board size based on productivity"""
        base_size = 12
        if st.session_state.completed_today >= 5:
            return base_size + 6  # Larger board for high productivity
        elif st.session_state.completed_today >= 3:
            return base_size + 3
        return base_size
    
    @staticmethod
    def reset_game():
        """Reset the game with productivity modifications"""
        st.session_state.snake = [[5, 5]]
        st.session_state.board_size = EnhancedSnakeGame.get_board_size()
        st.session_state.apple = EnhancedSnakeGame.generate_apple()
        st.session_state.direction = 'RIGHT'
        st.session_state.score = 0
        st.session_state.game_over = False
        st.session_state.game_active = True
    
    @staticmethod
    def generate_apple():
        """Generate a random apple position"""
        size = st.session_state.board_size
        while True:
            apple_pos = [random.randint(0, size-1), random.randint(0, size-1)]
            if apple_pos not in st.session_state.snake:
                return apple_pos
    
    @staticmethod
    def move_snake():
        """Enhanced snake movement with length limits"""
        if st.session_state.game_over or not st.session_state.game_active:
            return
        
        max_length = EnhancedSnakeGame.get_max_snake_length()
        
        head = st.session_state.snake[0].copy()
        
        # Move head based on direction
        if st.session_state.direction == 'UP':
            head[0] -= 1
        elif st.session_state.direction == 'DOWN':
            head[0] += 1
        elif st.session_state.direction == 'LEFT':
            head[1] -= 1
        elif st.session_state.direction == 'RIGHT':
            head[1] += 1
        
        # Check boundaries and collisions
        size = st.session_state.board_size
        if (head[0] < 0 or head[0] >= size or 
            head[1] < 0 or head[1] >= size or 
            head in st.session_state.snake):
            st.session_state.game_over = True
            if st.session_state.score > st.session_state.high_score:
                st.session_state.high_score = st.session_state.score
            return
        
        st.session_state.snake.insert(0, head)
        
        # Check if apple is eaten
        if head == st.session_state.apple:
            # Productivity bonus scoring
            base_points = 10
            productivity_multiplier = 1 + (st.session_state.completed_today * 0.5)
            st.session_state.score += int(base_points * productivity_multiplier)
            st.session_state.apple = EnhancedSnakeGame.generate_apple()
            
            # Check max length limit
            if len(st.session_state.snake) > max_length:
                st.session_state.snake.pop()
        else:
            st.session_state.snake.pop()
    
    @staticmethod
    def render_game_board():
        """Render the enhanced game board"""
        size = st.session_state.board_size
        board = []
        
        for row in range(size):
            row_str = ""
            for col in range(size):
                if [row, col] in st.session_state.snake:
                    if [row, col] == st.session_state.snake[0]:
                        row_str += "🐍"  # Snake head
                    else:
                        row_str += "🟢"  # Snake body
                elif [row, col] == st.session_state.apple:
                    row_str += "🍎"  # Apple
                else:
                    row_str += "⬛"  # Empty space
            board.append(row_str)
        
        return "\n".join(board)

class MemoryGame:
    """Memory card matching game"""
    
    @staticmethod
    def initialize_game():
        """Initialize a new memory game"""
        emojis = ['🍎', '🍌', '🍊', '🍇', '🍓', '🥝', '🍑', '🍍']
        cards = emojis + emojis  # Duplicate for pairs
        random.shuffle(cards)
        st.session_state.memory_cards = cards
        st.session_state.memory_flipped = []
        st.session_state.memory_matched = []
        st.session_state.memory_score = 0
        st.session_state.memory_moves = 0
    
    @staticmethod
    def flip_card(index):
        """Flip a card and check for matches"""
        if index in st.session_state.memory_flipped or index in st.session_state.memory_matched:
            return
        
        st.session_state.memory_flipped.append(index)
        
        if len(st.session_state.memory_flipped) == 2:
            st.session_state.memory_moves += 1
            card1, card2 = st.session_state.memory_flipped
            if st.session_state.memory_cards[card1] == st.session_state.memory_cards[card2]:
                st.session_state.memory_matched.extend([card1, card2])
                st.session_state.memory_score += 10
            
            # Clear flipped after a delay (simulated here)
            if len(st.session_state.memory_matched) < len(st.session_state.memory_cards):
                time.sleep(0.1)  # Brief pause for effect
                if len(st.session_state.memory_flipped) == 2 and st.session_state.memory_flipped[-2:] not in [[card1, card2] for card1, card2 in zip(st.session_state.memory_matched[::2], st.session_state.memory_matched[1::2])]:
                    st.session_state.memory_flipped = []

class TicTacToe:
    """Tic Tac Toe game"""
    
    @staticmethod
    def reset_game():
        """Reset the tic tac toe game"""
        st.session_state.ttt_board = ['' for _ in range(9)]
        st.session_state.ttt_current_player = 'X'
        st.session_state.ttt_winner = None
    
    @staticmethod
    def make_move(position):
        """Make a move on the board"""
        if st.session_state.ttt_board[position] == '' and not st.session_state.ttt_winner:
            st.session_state.ttt_board[position] = st.session_state.ttt_current_player
            
            # Check for winner
            winner = TicTacToe.check_winner()
            if winner:
                st.session_state.ttt_winner = winner
                st.session_state.ttt_wins[winner] += 1
            elif '' not in st.session_state.ttt_board:
                st.session_state.ttt_winner = 'Draw'
                st.session_state.ttt_wins['Draw'] += 1
            else:
                # Switch player
                st.session_state.ttt_current_player = 'O' if st.session_state.ttt_current_player == 'X' else 'X'
    
    @staticmethod
    def check_winner():
        """Check if there's a winner"""
        board = st.session_state.ttt_board
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        
        for combo in winning_combinations:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] != '':
                return board[combo[0]]
        return None

def display_enhanced_todo_section():
    """Display the enhanced todo list section"""
    st.markdown("<div class='todo-container'>", unsafe_allow_html=True)
    st.markdown("## 📝 Enhanced Todo List Manager")
    
    # Add new todo with enhanced features
    with st.expander("➕ Add New Task", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            new_task = st.text_input("Task Description:", placeholder="What needs to be done?")
            category = st.selectbox("Category", ["Work", "Personal", "Learning", "Health"])
        with col2:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            due_date = st.date_input("Due Date (Optional)", value=None)
        
        if st.button("🎯 Add Task", use_container_width=True):
            if new_task.strip():
                TodoManager.add_todo(new_task.strip(), priority, category, due_date)
                st.success("Task added successfully! 🎉")
                st.rerun()
    
    # Display urgent and overdue tasks
    overdue_todos = TodoManager.get_overdue_todos()
    urgent_todos = TodoManager.get_urgent_todos()
    
    if overdue_todos:
        st.markdown("### 🚨 Overdue Tasks")
        for todo in overdue_todos:
            display_todo_item(todo, "todo-overdue")
    
    if urgent_todos:
        st.markdown("### ⚡ Urgent Tasks (Due Within 3 Days)")
        for todo in urgent_todos:
            display_todo_item(todo, "todo-urgent")
    
    # Display tasks by category
    categories = ["Work", "Personal", "Learning", "Health"]
    for category in categories:
        category_todos = TodoManager.get_todos_by_category(category)
        if category_todos:
            st.markdown(f"### 📂 {category} Tasks")
            for todo in category_todos:
                if todo not in overdue_todos and todo not in urgent_todos:
                    display_todo_item(todo, f"category-{category.lower()}")
    
    # Display completed tasks
    completed_todos = TodoManager.get_completed_todos()
    if completed_todos:
        with st.expander(f"✅ Completed Tasks ({len(completed_todos)})", expanded=False):
            for todo in completed_todos[-10:]:  # Show last 10 completed
                display_completed_todo(todo)
    
    # Enhanced productivity stats
    display_productivity_stats()
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_todo_item(todo, css_class="todo-item"):
    """Display a single todo item"""
    col1, col2, col3 = st.columns([4, 1, 1])
    
    priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
    category_icons = {"Work": "💼", "Personal": "🏠", "Learning": "📚", "Health": "💪"}
    
    with col1:
        due_date_text = ""
        if todo['due_date']:
            due_date_obj = datetime.strptime(todo['due_date'], "%Y-%m-%d").date()
            days_until = (due_date_obj - date.today()).days
            if days_until < 0:
                due_date_text = f"<br><small style='color: #FF5722;'>⏰ Overdue by {abs(days_until)} days</small>"
            elif days_until == 0:
                due_date_text = f"<br><small style='color: #FF9800;'>⏰ Due today!</small>"
            else:
                due_date_text = f"<br><small>⏰ Due in {days_until} days</small>"
        
        st.markdown(f"""
        <div class='{css_class}'>
            {priority_colors.get(todo['priority'], '🟡')} {category_icons.get(todo['category'], '📝')} <strong>{todo['task']}</strong><br>
            <small>Created: {todo['created_date']} | Priority: {todo['priority']} | Category: {todo['category']}</small>
            {due_date_text}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("✅", key=f"complete_{todo['id']}", help="Complete Task", use_container_width=True):
            if TodoManager.complete_todo(todo['id']):
                st.success("Task completed! 🎉")
                st.rerun()
    
    with col3:
        if st.button("🗑️", key=f"delete_{todo['id']}", help="Delete Task", use_container_width=True):
            TodoManager.delete_todo(todo['id'])
            st.rerun()

def display_completed_todo(todo):
    """Display a completed todo item"""
    category_icons = {"Work": "💼", "Personal": "🏠", "Learning": "📚", "Health": "💪"}
    st.markdown(f"""
    <div class='todo-item todo-completed'>
        ✅ {category_icons.get(todo['category'], '📝')} {todo['task']}<br>
        <small>Completed: {todo['completed_date']} | Category: {todo['category']}</small>
    </div>
    """, unsafe_allow_html=True)

def display_productivity_stats():
    """Display enhanced productivity statistics"""
    completed_todos = TodoManager.get_completed_todos()
    overdue_count = len(TodoManager.get_overdue_todos())
    urgent_count = len(TodoManager.get_urgent_todos())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Today's Tasks", st.session_state.completed_today)
    with col2:
        st.metric("Total Completed", len(completed_todos))
    with col3:
        st.metric("Overdue Tasks", overdue_count, delta=-overdue_count if overdue_count > 0 else None)
    with col4:
        st.metric("Urgent Tasks", urgent_count, delta=-urgent_count if urgent_count > 0 else None)
    
    # Productivity level
    productivity_level = "🔥 Highly Productive" if st.session_state.completed_today >= 5 else \
                        "💪 Productive" if st.session_state.completed_today >= 3 else \
                        "👍 Getting Started" if st.session_state.completed_today >= 1 else \
                        "😴 Time to Start!"
    
    st.markdown(f"""
    <div class='game-stats'>
        <h4>📊 Productivity Level: {productivity_level}</h4>
        <p>Keep completing tasks to unlock more game features! 🎮</p>
    </div>
    """, unsafe_allow_html=True)

def display_enhanced_games_section():
    """Display all available games with unlock conditions"""
    st.markdown("<div class='game-container'>", unsafe_allow_html=True)
    st.markdown("## 🎮 Gaming Hub - Productivity Rewards!")
    
    # Game unlock conditions
    games_unlocked = {
        'snake': st.session_state.completed_today >= 1,
        'memory': st.session_state.completed_today >= 2,
        'tictactoe': st.session_state.completed_today >= 3
    }
    
    # Display unlock status
    unlock_status = f"""
    <div class='reward-unlock'>
        <h3>🎯 Game Unlock Status</h3>
        <p>🐍 Snake Game: {'✅ UNLOCKED' if games_unlocked['snake'] else '🔒 Complete 1 task'}</p>
        <p>🧠 Memory Game: {'✅ UNLOCKED' if games_unlocked['memory'] else '🔒 Complete 2 tasks'}</p>
        <p>⭕ Tic-Tac-Toe: {'✅ UNLOCKED' if games_unlocked['tictactoe'] else '🔒 Complete 3 tasks'}</p>
    </div>
    """
    st.markdown(unlock_status, unsafe_allow_html=True)
    
    # Game selection
    if any(games_unlocked.values()):
        available_games = []
        if games_unlocked['snake']:
            available_games.append("🐍 Enhanced Snake")
        if games_unlocked['memory']:
            available_games.append("🧠 Memory Match")
        if games_unlocked['tictactoe']:
            available_games.append("⭕ Tic-Tac-Toe")
        
        selected_game = st.selectbox("Choose Your Game:", available_games)
        
        if "Snake" in selected_game:
            display_enhanced_snake_game()