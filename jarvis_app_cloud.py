import streamlit as st
import re
import os
from groq import Groq

# Try to get API key from secrets (cloud) or .env (local)
try:
    # For cloud deployment (Streamlit Cloud, Hugging Face)
    api_key = st.secrets["GROQ_API_KEY"]
except:
    # For local development
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

# ----- Tools -----
def calculate(expression):
    try:
        return eval(expression)
    except:
        return "Invalid expression"

def get_weather(city):
    import re
    city = city.lower()
    city = re.sub(r"weather|in|of|for", "", city).strip()
    weather_data = {
        "tokyo": "22°C, sunny",
        "london": "15°C, cloudy",
        "new york": "18°C, rainy",
        "paris": "20°C, clear sky",
        "mumbai": "30°C, humid",
        "delhi": "35°C, hazy",
        "singapore": "28°C, humid"
    }
    return weather_data.get(city, f"Weather data not available for {city}")

def decide_tool(user_input):
    if re.search(r"\d+[\+\-\*/]\d+", user_input):
        return "calculate"
    elif "weather" in user_input.lower():
        return "weather"
    else:
        return "chat"

def run_agent(user_input):
    tool = decide_tool(user_input)
    if tool == "calculate":
        expr = re.search(r"[\d\+\-\*/ ]+", user_input).group()
        result = calculate(expr)
        return f"🧮 {result}"
    elif tool == "weather":
        city = user_input.lower().replace("weather", "").replace("in", "").strip()
        result = get_weather(city)
        return f"🌤️ {result}"
    else:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_input}],
            temperature=0.7
        )
        return completion.choices[0].message.content

# ----- Enhanced Streamlit UI -----
st.set_page_config(
    page_title="JARVIS Agent", 
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://emojis.slackmojis.com/emojis/images/1531849430/4246/blaster.png?1531849430", width=50)
    st.title("🤖 JARVIS v2.0")
    st.markdown("---")
    st.markdown("### Features:")
    st.markdown("""
    - 🧮 **Calculator** - Math operations
    - 🌤️ **Weather** - City weather lookup
    - 💬 **AI Chat** - Powered by Llama 3
    """)
    st.markdown("---")
    st.info("💡 **Try:**\n- 'What is 15 * 8?'\n- 'Weather in Paris'\n- 'Tell me a joke'")

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🤖 JARVIS Personal Assistant")
    st.markdown("*Your intelligent AI companion*")

with col2:
    st.metric("Status", "🟢 Online", "Ready to assist")

st.markdown("---")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What can I do for you today?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("JARVIS is thinking..."):
            try:
                response = run_agent(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {str(e)}")
