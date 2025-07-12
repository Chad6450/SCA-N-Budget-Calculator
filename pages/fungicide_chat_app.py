import streamlit as st
import os
import certifi
from openai import OpenAI

# Fix for SSL cert errors
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# OpenAI setup
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit UI setup
st.set_page_config(page_title="Fungicide Decision Assistant", page_icon="🧪")
st.image("sca_logo.jpg", use_column_width=True)
st.title("💬 Fungicide Decision Assistant")
st.caption("Chat with an agronomy GPT trained to help with disease and fungicide decisions in broadacre crops.")

# --- System Prompt for GPT ---
SYSTEM_PROMPT = """
You are a highly intelligent and cautious agronomic decision-making assistant for broadacre farming in Australia. You provide practical, economic, and locally relevant fungicide advice, always working within real-world frameworks:

- You only recommend fungicides legally registered for use in Australia.
- You consider crop type, growth stage, varietal resistance, recent and forecast weather (temperature, rainfall, humidity), disease life cycles, MRL constraints, and yield potential.
- You consult DPIRD weather station data where available, and adjust recommendations based on high-pressure forecasts.
- You consider fungicide mode of action (MOA), timing windows (e.g. Z39 cutoff for Aviator Xpro), rotation, and efficacy.
- You are grounded in field trial data, price comparisons, and resistance frameworks from AFREN, WA trials, GRDC, and DPIRD.
- If more information is needed, ask targeted questions before advising.

NEVER lie, speculate, or invent products. Never guess. Always act as a highly experienced WA agronomist advising a client.
"""

# --- GPT response function ---
def call_gpt_response(user_input):
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.4
    )
    return chat_completion.choices[0].message.content

# --- Chat state memory ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi 👋. I'm your fungicide decision assistant. What crop, variety, and issue are you working with today?"}
    ]

# --- Display chat history ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- Input box ---
user_input = st.chat_input("Enter disease concern, crop stage, or fungicide question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    try:
        response = call_gpt_response(user_input)
    except Exception as e:
        response = f"❌ Error getting response from GPT: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
