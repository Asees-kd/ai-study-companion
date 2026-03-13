import streamlit as st
# import google.generativeai as genai
from datetime import datetime
import json
import random
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
print(os.getenv("OPENROUTER_API_KEY"))

# client = OpenAI(
#     api_key=os.getenv("OPENROUTER_API_KEY"),
#     base_url="https://openrouter.ai/api/v1"
# )
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AI Study Companion"
    }
)


# # Load environment variables
# load_dotenv()

# # Configure OpenAI AP
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize session state
if 'user_points' not in st.session_state:
    st.session_state.user_points = 0
if 'user_level' not in st.session_state:
    st.session_state.user_level = 1
if 'quiz_history' not in st.session_state:
    st.session_state.quiz_history = []
if 'current_quiz' not in st.session_state:
    st.session_state.current_quiz = None
if 'badges' not in st.session_state:
    st.session_state.badges = []

# Badge system
BADGES = {
    "First Steps": {"requirement": 10, "icon": "🌟", "description": "Score 10 points"},
    "Quiz Master": {"requirement": 5, "icon": "🎯", "description": "Complete 5 quizzes"},
    "Knowledge Seeker": {"requirement": 50, "icon": "📚", "description": "Score 50 points"},
    "Level Up!": {"requirement": 2, "icon": "🚀", "description": "Reach Level 2"},
}

def get_ai_response(prompt, system_message="You are a helpful AI tutor."):
    try:
        response = client.chat.completions.create(
            # model="x-ai/grok-beta",
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"

def generate_quiz(topic, difficulty="medium", num_questions=3):
    """Generate quiz questions using AI"""
    prompt = f"""Generate {num_questions} multiple choice questions about {topic} at {difficulty} difficulty level.
    
    Return the response in this exact JSON format:
    {{
        "questions": [
            {{
                "question": "Question text here",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct": "A",
                "explanation": "Brief explanation of the correct answer"
            }}
        ]
    }}
    """
    
    response = get_ai_response(prompt, "You are an expert quiz generator. Always return valid JSON.")
    
    try:
        quiz_data = json.loads(response)
        return quiz_data
    except:
        # Fallback quiz if JSON parsing fails
        return {
            "questions": [
                {
                    "question": f"What is a key concept in {topic}?",
                    "options": ["A) Concept 1", "B) Concept 2", "C) Concept 3", "D) Concept 4"],
                    "correct": "A",
                    "explanation": "This is the correct answer because it's fundamental to the topic."
                }
            ]
        }

def explain_concept(topic):
    """Get AI explanation for a concept"""
    prompt = f"""Explain {topic} in a clear, student-friendly way. 
    Include:
    1. A simple definition
    2. A real-world example
    3. Why it's important to learn
    Keep it under 200 words."""
    
    return get_ai_response(prompt, "You are an enthusiastic teacher explaining concepts to students.")

def update_gamification(points_earned):
    """Update points, level, and badges"""
    st.session_state.user_points += points_earned
    
    # Level calculation (every 30 points = new level)
    new_level = (st.session_state.user_points // 30) + 1
    if new_level > st.session_state.user_level:
        st.session_state.user_level = new_level
        st.balloons()
        st.success(f"🎉 Level Up! You're now Level {new_level}!")
    
    # Check for new badges
    for badge_name, badge_info in BADGES.items():
        if badge_name not in st.session_state.badges:
            if badge_name == "First Steps" and st.session_state.user_points >= badge_info["requirement"]:
                st.session_state.badges.append(badge_name)
                st.success(f"🏆 New Badge Earned: {badge_info['icon']} {badge_name}!")
            elif badge_name == "Quiz Master" and len(st.session_state.quiz_history) >= badge_info["requirement"]:
                st.session_state.badges.append(badge_name)
                st.success(f"🏆 New Badge Earned: {badge_info['icon']} {badge_name}!")
            elif badge_name == "Knowledge Seeker" and st.session_state.user_points >= badge_info["requirement"]:
                st.session_state.badges.append(badge_name)
                st.success(f"🏆 New Badge Earned: {badge_info['icon']} {badge_name}!")
            elif badge_name == "Level Up!" and st.session_state.user_level >= badge_info["requirement"]:
                st.session_state.badges.append(badge_name)
                st.success(f"🏆 New Badge Earned: {badge_info['icon']} {badge_name}!")

# Streamlit UI
st.set_page_config(page_title="AI Study Companion", page_icon="🎓", layout="wide")

# Header with gamification stats
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("🎓 AI Study Companion")
with col2:
    st.metric("Points", st.session_state.user_points, delta=None)
with col3:
    st.metric("Level", st.session_state.user_level, delta=None)

# Display badges
if st.session_state.badges:
    badge_display = " ".join([BADGES[b]["icon"] for b in st.session_state.badges])
    st.markdown(f"**Your Badges:** {badge_display}")

# Sidebar for navigation
st.sidebar.title("📚 Study Options")
mode = st.sidebar.radio("Choose Mode:", ["Learn Concepts", "Take Quiz", "Progress Dashboard"])

if mode == "Learn Concepts":
    st.header("🧠 Learn New Concepts")
    
    topic = st.text_input("What would you like to learn about?", placeholder="e.g., Photosynthesis, Python loops, World War 2")
    
    if st.button("Explain Concept", type="primary"):
        if topic:
            with st.spinner("🤔 Let me explain that for you..."):
                explanation = explain_concept(topic)
                st.markdown("### Explanation:")
                st.write(explanation)
                
                # Award points for learning
                update_gamification(5)
                st.info("📈 +5 points for learning!")
        else:
            st.warning("Please enter a topic to learn about!")
    
    # Quick topic suggestions
    st.markdown("### 💡 Suggested Topics:")
    col1, col2, col3 = st.columns(3)
    suggestions = ["Machine Learning", "Photosynthesis", "French Revolution", 
                   "Quadratic Equations", "Solar System", "DNA Structure"]
    
    for i, suggestion in enumerate(suggestions):
        with [col1, col2, col3][i % 3]:
            if st.button(suggestion, key=f"sug_{i}"):
                with st.spinner(f"Learning about {suggestion}..."):
                    explanation = explain_concept(suggestion)
                    st.markdown(f"### {suggestion}")
                    st.write(explanation)
                    update_gamification(5)
                    st.info("📈 +5 points for learning!")

elif mode == "Take Quiz":
    st.header("🎯 Quiz Time!")
    
    col1, col2 = st.columns(2)
    with col1:
        quiz_topic = st.text_input("Quiz Topic:", placeholder="e.g., Mathematics, Science, History")
    with col2:
        difficulty = st.select_slider("Difficulty:", options=["easy", "medium", "hard"])
    
    if st.button("Generate Quiz", type="primary"):
        if quiz_topic:
            with st.spinner("Creating your quiz..."):
                quiz_data = generate_quiz(quiz_topic, difficulty)
                st.session_state.current_quiz = quiz_data
                st.session_state.quiz_answers = {}
    
    # Display quiz if available
    if st.session_state.current_quiz:
        st.markdown("---")
        questions = st.session_state.current_quiz.get("questions", [])
        
        for i, q in enumerate(questions):
            st.markdown(f"**Question {i+1}:** {q['question']}")
            answer = st.radio(
                "Select your answer:",
                q['options'],
                key=f"q_{i}"
            )
            if f"q_{i}" not in st.session_state.quiz_answers:
                st.session_state.quiz_answers[f"q_{i}"] = None
        
        if st.button("Submit Quiz", type="primary"):
            score = 0
            total = len(questions)
            
            st.markdown("### Results:")
            for i, q in enumerate(questions):
                user_answer = st.session_state[f"q_{i}"][0] if f"q_{i}" in st.session_state else None
                correct_answer = q['correct']
                
                if user_answer == correct_answer:
                    score += 1
                    st.success(f"✅ Question {i+1}: Correct!")
                else:
                    st.error(f"❌ Question {i+1}: Incorrect. The correct answer was {correct_answer}")
                    st.info(f"💡 {q['explanation']}")
            
            # Calculate points based on score and difficulty
            difficulty_multiplier = {"easy": 5, "medium": 10, "hard": 15}
            points_earned = score * difficulty_multiplier.get(difficulty, 10)
            
            st.markdown(f"### Final Score: {score}/{total}")
            update_gamification(points_earned)
            st.success(f"🎉 You earned {points_earned} points!")
            
            # Save to history
            st.session_state.quiz_history.append({
                "topic": quiz_topic,
                "score": score,
                "total": total,
                "difficulty": difficulty,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
            # Clear current quiz
            st.session_state.current_quiz = None

elif mode == "Progress Dashboard":
    st.header("📊 Your Progress")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Points", st.session_state.user_points)
    with col2:
        st.metric("Current Level", st.session_state.user_level)
    with col3:
        st.metric("Quizzes Completed", len(st.session_state.quiz_history))
    
    # Progress bar to next level
    points_to_next_level = 30 - (st.session_state.user_points % 30)
    progress = (st.session_state.user_points % 30) / 30
    st.progress(progress)
    st.caption(f"📈 {points_to_next_level} points to Level {st.session_state.user_level + 1}")
    
    # Badges section
    st.markdown("### 🏆 Badges")
    badge_cols = st.columns(4)
    for i, (badge_name, badge_info) in enumerate(BADGES.items()):
        with badge_cols[i % 4]:
            if badge_name in st.session_state.badges:
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background: #d4edda; border-radius: 10px;'>
                    <h1>{badge_info['icon']}</h1>
                    <p><b>{badge_name}</b></p>
                    <small>✅ Earned</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background: #f8f9fa; border-radius: 10px;'>
                    <h1>🔒</h1>
                    <p><b>{badge_name}</b></p>
                    <small>{badge_info['description']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Quiz History
    if st.session_state.quiz_history:
        st.markdown("### 📝 Recent Quizzes")
        for quiz in st.session_state.quiz_history[-5:]:
            st.write(f"**{quiz['topic']}** ({quiz['difficulty']}) - Score: {quiz['score']}/{quiz['total']} - {quiz['date']}")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit and OpenAI | AI Study Companion v1.0")

