import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os
from backend import Difficulty, generate_q_a, make_leaderboard

# Page configuration
st.set_page_config(page_title="MFM ZETAMAC", layout="wide")

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'menu'  # 'menu', 'playing', 'results'
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'mistakes' not in st.session_state:
    st.session_state.mistakes = []
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = None
if 'game_length' not in st.session_state:
    st.session_state.game_length = 120  # 2 minutes in seconds
if 'last_timer_update' not in st.session_state:
    st.session_state.last_timer_update = time.time()
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'game_started' not in st.session_state:  # ADD THIS LINE
    st.session_state.game_started = False

def reset_game():
    st.session_state.game_state = 'menu'
    st.session_state.score = 0
    st.session_state.mistakes = []
    st.session_state.start_time = None
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.current_question_index = 0
    st.session_state.user_input = ""
    st.session_state.game_started = False  # ADD THIS LINE

def generate_questions(difficulty, num_questions=200):
    """Pre-generate a large number of questions"""
    questions = []
    answers = []
    for _ in range(num_questions):
        q, a = generate_q_a(difficulty)
        questions.append(q)
        answers.append(a)
    return questions, answers

def start_game(difficulty, player_name):
    st.session_state.game_state = 'playing'
    st.session_state.difficulty = difficulty
    st.session_state.player_name = player_name
    st.session_state.game_started = False
    st.session_state.score = 0
    st.session_state.mistakes = []
    st.session_state.current_question_index = 0
    st.session_state.user_input = ""

    # Pre-generate questions
    questions, answers = generate_questions(difficulty)
    st.session_state.questions = questions
    st.session_state.answers = answers

def process_answer():
    """Process the submitted answer and move to next question"""
    if st.session_state.user_input.strip():
        if st.session_state.game_started == False:
            st.session_state.start_time = datetime.now()
            st.session_state.game_started = True
        try:
            user_answer = int(st.session_state.user_input.strip())
            correct_answer = st.session_state.answers[st.session_state.current_question_index]
            
            if user_answer == correct_answer:
                # Check if still within time limit
                elapsed = datetime.now() - st.session_state.start_time
                if elapsed.total_seconds() < st.session_state.game_length:
                    st.session_state.score += 1
            else:
                st.session_state.mistakes.append({
                    "q": st.session_state.questions[st.session_state.current_question_index],
                    "correct": correct_answer,
                    "your": user_answer
                })
            
            # Move to next question
            st.session_state.current_question_index += 1
            st.session_state.user_input = ""  # Clear input
            
        except ValueError:
            # Invalid input, just clear and continue
            st.session_state.user_input = ""

def end_game():
    # Save to database
    path_to_db = f"./data/{st.session_state.difficulty.name}_db.csv"
    
    # Create data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)
    
    # Create CSV file with headers if it doesn't exist
    if not os.path.exists(path_to_db):
        with open(path_to_db, "w") as db:
            db.write("Name,Date,Correct,Mistakes\n")
    
    # Format datetime to match what make_leaderboard expects
    formatted_datetime = st.session_state.start_time.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(path_to_db, "a") as db:
        db.write(f"{st.session_state.player_name},{formatted_datetime},{st.session_state.score},{len(st.session_state.mistakes)}\n")
    
    st.session_state.game_state = 'results'

def get_difficulty_specs(difficulty):
    """Return the specifications for each difficulty level"""
    specs = {
        Difficulty.EASY: {
            "Addition Range": "[1-25] + [1-25]",
            "Subtraction Range": "[1-25] - [1-25]",
            "Multiplication Range": "[1-12] × [1-12]",
            "Division Range": "[1-144] ÷ [1-12]"
        },
        Difficulty.MEDIUM: {
            "Addition Range": "[1-50] + [1-50]",
            "Subtraction Range": "[1-50] - [1-50]",
            "Multiplication Range": "[1-18] × [1-12]",
            "Division Range": "[1-216] ÷ [1-12]"
        },
        Difficulty.HARD: {
            "Addition Range": "[1-100] + [1-100]",
            "Subtraction Range": "[1-100] - [1-100]",
            "Multiplication Range": "[1-24] × [1-12]",
            "Division Range": "[1-288] ÷ [1-12]"
        }
    }
    return specs[difficulty]

def display_leaderboard(difficulty):
    """Display leaderboard for given difficulty"""
    path_to_db = f"./data/{difficulty.name}_db.csv"
    
    if os.path.exists(path_to_db):
        try:
            # Check if file has content beyond headers
            with open(path_to_db, 'r') as f:
                lines = f.readlines()
                if len(lines) <= 1:  # Only header or empty
                    st.info("No games played yet!")
                    return
            
            leaderboard = make_leaderboard(path_to_db)
            if not leaderboard.empty:
                # Format datetime for display
                leaderboard_display = leaderboard.copy()
                if 'datetime' in leaderboard_display.columns:
                    leaderboard_display['Date'] = pd.to_datetime(leaderboard_display['Date']).dt.strftime('%Y-%m-%d %H:%M')
                
                st.dataframe(
                    leaderboard_display[['Rank', 'Name', 'Date', 'Correct', 'Mistakes']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No games played yet!")
        except Exception as e:
            st.error(f"Error loading leaderboard: {str(e)}")
            # Debug: show what's in the file
            if os.path.exists(path_to_db):
                with open(path_to_db, 'r') as f:
                    content = f.read()
                    st.text(f"File content: {content[:200]}...")
    else:
        st.info("No games played yet!")

# Main UI
st.title("MFM ZETAMAC")

if st.session_state.game_state == 'menu':
    # Create tabs for different difficulties
    tab1, tab2, tab3 = st.tabs(["Easy", "Medium", "Hard"])
    
    difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
    tabs = [tab1, tab2, tab3]
    
    for tab, difficulty in zip(tabs, difficulties):
        with tab:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Game start section
                st.header("Start Game")
                player_name = st.text_input(f"Enter your name:", key=f"name_{difficulty.name}", placeholder="Steve Cohen")
                st.markdown("The timer will start once you enter your first answer.")
                if st.button(f"Start {difficulty.name.title()} Game", key=f"start_{difficulty.name}"):
                    if player_name.strip():
                        start_game(difficulty, player_name.strip())
                        st.rerun()
                    else:
                        st.error("Please enter your name!")

                st.subheader(f"{difficulty.name.title()} Mode Specifications")
                specs = get_difficulty_specs(difficulty)
                
                # Create metrics for each specification with custom containers
                spec_col1, spec_col2 = st.columns(2)
                spec_items = list(specs.items())
                
                with spec_col1:
                    with st.container():
                        st.metric(label=spec_items[0][0], value=spec_items[0][1])
                    if len(spec_items) > 2:
                        with st.container():
                            st.metric(label=spec_items[2][0], value=spec_items[2][1])
                
                with spec_col2:
                    with st.container():
                        st.metric(label=spec_items[1][0], value=spec_items[1][1])
                    if len(spec_items) > 3:
                        with st.container():
                            st.metric(label=spec_items[3][0], value=spec_items[3][1])
                
                # Game info metrics
                st.metric(label="Game Duration", value="120 seconds")
                            
            with col2:
                st.header(f"{difficulty.name.title()} Leaderboard")
                display_leaderboard(difficulty)

elif st.session_state.game_state == 'playing':
    # Calculate remaining time - FIX THE LOGIC HERE
    if not st.session_state.game_started or st.session_state.start_time is None:
        remaining = st.session_state.game_length  # Show full time before game starts
    else:
        elapsed = datetime.now() - st.session_state.start_time
        remaining = st.session_state.game_length - elapsed.total_seconds()
    
    if remaining <= 0 and st.session_state.game_started:
        end_game()
        st.rerun()
    
    # Display game info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", st.session_state.score)
    with col2:
        st.metric("Mistakes", len(st.session_state.mistakes))
    with col3:
        st.metric("Time Left", f"{int(max(0, remaining))}s")
    
    # Display current question
    current_question = st.session_state.questions[st.session_state.current_question_index]
    st.markdown(f"## {current_question} = ?")
    
    # Create a form for seamless Enter key submission
    with st.form(key="answer_form", clear_on_submit=True):
        answer_input = st.text_input(
            "Your answer:",
            value="",
            key="game_input",
            label_visibility="collapsed",
            placeholder="Type your answer and press Enter..."
        )
        
        # This submit button is hidden with CSS but processes Enter key presses
        submitted = st.form_submit_button("Submit", type="primary")
        
        if submitted and answer_input:
            # Start the timer on first answer
            if not st.session_state.game_started:
                st.session_state.start_time = datetime.now()
                st.session_state.game_started = True
                
            try:
                user_answer = int(answer_input)
                correct_answer = st.session_state.answers[st.session_state.current_question_index]
                
                if user_answer == correct_answer:
                    # Check if still within time limit
                    elapsed = datetime.now() - st.session_state.start_time
                    if elapsed.total_seconds() < st.session_state.game_length:
                        st.session_state.score += 1
                else:
                    st.session_state.mistakes.append({
                        "q": current_question,
                        "correct": correct_answer,
                        "your": user_answer
                    })
                
                # Move to next question
                st.session_state.current_question_index += 1
                st.rerun()
                
            except ValueError:
                st.error("Please enter a valid number!")
    
    # Auto-focus JavaScript
    st.markdown("""
    <script>
    setTimeout(function() {
        const input = window.parent.document.querySelector('input[data-testid="textinput-game_input"]');
        if (input) {
            input.focus();
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    
    # Timer update logic - only refresh every second to update the timer
    current_time = time.time()
    if current_time - st.session_state.last_timer_update >= 1:
        st.session_state.last_timer_update = current_time
        st.rerun()

elif st.session_state.game_state == 'results':
    st.subheader("🎉 Game Complete!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Final Score", st.session_state.score)
    with col2:
        st.metric("Total Mistakes", len(st.session_state.mistakes))
    
    if st.session_state.mistakes:
        st.subheader("Review Your Mistakes:")
        for i, mistake in enumerate(st.session_state.mistakes, 1):
            with st.expander(f"Mistake {i}: {mistake['q']}"):
                st.write(f"**Correct Answer:** {mistake['correct']}")
                st.write(f"**Your Answer:** {mistake['your']}")
    
    # Display updated leaderboard
    st.subheader(f"{st.session_state.difficulty.name.title()} Leaderboard")
    display_leaderboard(st.session_state.difficulty)
    
    if st.button("Play Again"):
        reset_game()
        st.rerun()

# Add some custom CSS for better UX
st.markdown("""
<style>
.stTextInput > div > div > input {
    font-size: 20px !important;
}

/* Custom metric container styling */
.custom-metric-container {
    background-color: #f0f2f6 !important;
    border: 1px solid #e1e5e9 !important;
    padding: 1rem !important;
    border-radius: 0.5rem !important;
    margin: 0.25rem 0 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
}

.stMetric {
    background-color: #1A1D29 !important;
    border: 1px solid #00D4AA !important;
    padding: 1rem !important;
    border-radius: 0.5rem !important;
    margin: 0.25rem 0 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
}

/* Hide the submit button since we only want Enter key submission */
.stForm button[type="submit"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)