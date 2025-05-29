import streamlit as st
import random
import time

# Set page config for better visuals
st.set_page_config(
    page_title="🎵 Music Personality Quiz",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .quiz-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
    }
    .result-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    .music-card {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #FFD93D;
    }
</style>
""", unsafe_allow_html=True)

# Music database organized by personality types
MUSIC_DATABASE = {
    "adventurous": {
        "genres": ["Electronic", "World Music", "Experimental", "Jazz Fusion"],
        "songs": [
            "Strobe - Deadmau5",
            "Bambaataa - Shpongle",
            "Teardrop - Massive Attack",
            "Windowlicker - Aphex Twin",
            "Kiara - Bonobo"
        ]
    },
    "chill": {
        "genres": ["Lo-fi", "Ambient", "Indie Folk", "Neo-Soul"],
        "songs": [
            "Girl - Syml",
            "Holocene - Bon Iver",
            "Breathe Me - Sia",
            "Mad World - Gary Jules",
            "Skinny Love - Bon Iver"
        ]
    },
    "energetic": {
        "genres": ["Pop", "Dance", "Rock", "Hip-Hop"],
        "songs": [
            "Uptown Funk - Bruno Mars",
            "Can't Stop the Feeling - Justin Timberlake",
            "Good as Hell - Lizzo",
            "Shut Up and Dance - Walk the Moon",
            "Happy - Pharrell Williams"
        ]
    },
    "romantic": {
        "genres": ["R&B", "Soft Rock", "Acoustic", "Soul"],
        "songs": [
            "All of Me - John Legend",
            "Thinking Out Loud - Ed Sheeran",
            "At Last - Etta James",
            "Make You Feel My Love - Adele",
            "Perfect - Ed Sheeran"
        ]
    },
    "rebellious": {
        "genres": ["Punk Rock", "Alternative", "Grunge", "Metal"],
        "songs": [
            "Smells Like Teen Spirit - Nirvana",
            "Killing in the Name - Rage Against the Machine",
            "Basket Case - Green Day",
            "Seven Nation Army - The White Stripes",
            "Bohemian Rhapsody - Queen"
        ]
    }
}

def initialize_session_state():
    """Initialize session state variables"""
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'personality_type' not in st.session_state:
        st.session_state.personality_type = None

def get_random_songs(exclude_personality=None, count=3):
    """Get random songs from all categories except specified one"""
    all_songs = []
    for personality, data in MUSIC_DATABASE.items():
        if personality != exclude_personality:
            all_songs.extend(data["songs"])
    return random.sample(all_songs, min(count, len(all_songs)))

def calculate_personality(answers):
    """Calculate personality type based on quiz answers"""
    # Simple scoring system based on answer patterns
    scores = {
        "adventurous": 0,
        "chill": 0,
        "energetic": 0,
        "romantic": 0,
        "rebellious": 0
    }
    
    # Question 1: Weekend activity
    if answers[0] == "Try a new adventure sport":
        scores["adventurous"] += 2
    elif answers[0] == "Read a book in a quiet café":
        scores["chill"] += 2
    elif answers[0] == "Go to a party or club":
        scores["energetic"] += 2
    elif answers[0] == "Have a romantic dinner":
        scores["romantic"] += 2
    elif answers[0] == "Attend a rock concert":
        scores["rebellious"] += 2
    
    # Question 2: Color preference
    if answers[1] == "Bright Orange":
        scores["adventurous"] += 1
        scores["energetic"] += 1
    elif answers[1] == "Soft Blue":
        scores["chill"] += 2
    elif answers[1] == "Electric Purple":
        scores["energetic"] += 1
        scores["rebellious"] += 1
    elif answers[1] == "Warm Pink":
        scores["romantic"] += 2
    elif answers[1] == "Deep Black":
        scores["rebellious"] += 2
    
    # Question 3: Movie genre
    if answers[2] == "Action/Adventure":
        scores["adventurous"] += 1
        scores["energetic"] += 1
    elif answers[2] == "Drama/Indie":
        scores["chill"] += 2
    elif answers[2] == "Comedy":
        scores["energetic"] += 2
    elif answers[2] == "Romance":
        scores["romantic"] += 2
    elif answers[2] == "Horror/Thriller":
        scores["rebellious"] += 2
    
    # Question 4: Social setting
    if answers[3] == "Large group party":
        scores["energetic"] += 2
    elif answers[3] == "Small intimate gathering":
        scores["romantic"] += 1
        scores["chill"] += 1
    elif answers[3] == "Solo time":
        scores["chill"] += 2
    elif answers[3] == "Underground venue":
        scores["rebellious"] += 2
    elif answers[3] == "Outdoor adventure":
        scores["adventurous"] += 2
    
    # Return the personality type with the highest score
    return max(scores, key=scores.get)

def display_quiz_question(question_num, question, options):
    """Display a quiz question with options"""
    st.markdown(f"<div class='quiz-container'>", unsafe_allow_html=True)
    st.subheader(f"Question {question_num + 1}")
    st.write(question)
    
    # Create radio button for options
    answer = st.radio(
        "Choose your answer:",
        options,
        key=f"question_{question_num}"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    return answer

def display_results(personality_type):
    """Display the quiz results with music recommendations"""
    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
    
    # Personality descriptions
    descriptions = {
        "adventurous": "🌟 You're an Explorer! You love discovering new sounds and pushing musical boundaries.",
        "chill": "😌 You're a Zen Master! You appreciate calm, soothing music that helps you relax.",
        "energetic": "⚡ You're a Dynamo! You love upbeat music that gets you moving and dancing.",
        "romantic": "💕 You're a Romantic! You're drawn to heartfelt music that touches your soul.",
        "rebellious": "🔥 You're a Rebel! You love music with attitude and powerful messages."
    }
    
    st.markdown(f"## Your Music Personality: {personality_type.title()}")
    st.markdown(f"### {descriptions[personality_type]}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display recommended music
    st.markdown("## 🎵 Your Personalized Music Recommendations")
    
    music_data = MUSIC_DATABASE[personality_type]
    
    # Show recommended genres
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎼 Recommended Genres")
        for genre in music_data["genres"]:
            st.markdown(f"<div class='music-card'>🎭 {genre}</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎤 Song Recommendations")
        recommended_songs = random.sample(music_data["songs"], min(3, len(music_data["songs"])))
        for song in recommended_songs:
            st.markdown(f"<div class='music-card'>🎵 {song}</div>", unsafe_allow_html=True)
    
    # Show some random songs from other categories as "You might also like"
    st.markdown("### 🔀 You Might Also Like")
    random_songs = get_random_songs(exclude_personality=personality_type, count=2)
    for song in random_songs:
        st.markdown(f"<div class='music-card'>🎵 {song}</div>", unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Main header
    st.markdown("<h1 class='main-header'>🎵 Music Personality Quiz 🎵</h1>", unsafe_allow_html=True)
    
    # Quiz questions
    questions = [
        {
            "question": "What's your ideal weekend activity?",
            "options": [
                "Try a new adventure sport",
                "Read a book in a quiet café",
                "Go to a party or club",
                "Have a romantic dinner",
                "Attend a rock concert"
            ]
        },
        {
            "question": "Which color speaks to you most?",
            "options": [
                "Bright Orange",
                "Soft Blue", 
                "Electric Purple",
                "Warm Pink",
                "Deep Black"
            ]
        },
        {
            "question": "What's your favorite movie genre?",
            "options": [
                "Action/Adventure",
                "Drama/Indie",
                "Comedy",
                "Romance",
                "Horror/Thriller"
            ]
        },
        {
            "question": "Where do you feel most comfortable?",
            "options": [
                "Large group party",
                "Small intimate gathering",
                "Solo time",
                "Underground venue",
                "Outdoor adventure"
            ]
        }
    ]
    
    if not st.session_state.quiz_started:
        # Welcome screen
        st.markdown("""
        ### Welcome to the Music Personality Quiz! 🎶
        
        Discover your unique music personality and get personalized song recommendations 
        based on your preferences and lifestyle choices.
        
        **How it works:**
        1. Answer a few fun questions about yourself
        2. We'll analyze your personality type
        3. Get personalized music recommendations
        4. Discover new songs you might love!
        """)
        
        if st.button("🚀 Start the Quiz!", use_container_width=True):
            st.session_state.quiz_started = True
            st.rerun()
    
    elif not st.session_state.quiz_completed:
        # Quiz in progress
        progress = (st.session_state.current_question + 1) / len(questions)
        st.progress(progress)
        
        if st.session_state.current_question < len(questions):
            current_q = questions[st.session_state.current_question]
            answer = display_quiz_question(
                st.session_state.current_question,
                current_q["question"],
                current_q["options"]
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col2:
                if st.button("Next Question ➡️", use_container_width=True):
                    # Store the answer
                    if len(st.session_state.answers) <= st.session_state.current_question:
                        st.session_state.answers.append(answer)
                    else:
                        st.session_state.answers[st.session_state.current_question] = answer
                    
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= len(questions):
                        # Quiz completed, calculate personality
                        st.session_state.personality_type = calculate_personality(st.session_state.answers)
                        st.session_state.quiz_completed = True
                    
                    st.rerun()
    
    else:
        # Show results
        display_results(st.session_state.personality_type)
        
        # Reset button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Take Quiz Again", use_container_width=True):
                # Reset all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()