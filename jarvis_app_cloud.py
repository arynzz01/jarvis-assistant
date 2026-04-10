import streamlit as st
import re
from groq import Groq

# Get API key from Streamlit secrets (cloud)
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

st.set_page_config(page_title="JARVIS", page_icon="🤖")
st.title("🤖 JARVIS Assistant")
st.markdown("Ask me anything - math, weather, or just chat!")

# Weather data
weather_data = {
    "tokyo": "22°C, sunny",
    "london": "15°C, cloudy",
    "new york": "18°C, rainy",
    "paris": "20°C, clear",
    "mumbai": "30°C, humid",
    "delhi": "35°C, hazy"
}

def calculate(expression):
    try:
        return eval(expression)
    except:
        return "Invalid expression"

def get_weather(city):
    city = city.lower().replace("weather", "").replace("in", "").strip()
    return weather_data.get(city, f"Weather data not available for {city}")

def run_agent(user_input):
    if re.search(r"\d+[\+\-\*/]\d+", user_input):
        expr = re.search(r"[\d\+\-\*/ ]+", user_input).group()
        return f"🧮 {calculate(expr)}"
    elif "weather" in user_input.lower():
        return f"🌤️ {get_weather(user_input)}"
    else:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_input}],
            temperature=0.7
        )
        return completion.choices[0].message.content

# UI
user_input = st.text_input("You:", placeholder="e.g., What is 12+7? or Weather in Tokyo?")
if st.button("Ask JARVIS") and user_input:
    with st.spinner("JARVIS is thinking..."):
        response = run_agent(user_input)
        st.success(f"**JARVIS:** {response}")
