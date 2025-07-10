import streamlit as st
import google.generativeai as genai

# --- Page & AI Configuration ---
st.set_page_config(page_title="AI Interviewer", page_icon="🤖")
st.title("AI Interviewer 🤖")

try:
    # Get the API key from Streamlit's secrets management
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except (KeyError, AttributeError):
    st.error("API Key not found. Please create a .streamlit/secrets.toml file with your GEMINI_API_KEY.")
    st.stop()

# This is the full persona and instruction set for the AI we designed.
system_instruction = """You are a calm, empathetic, and respectful AI assistant. Your goal is to create a safe and confidential space for individuals to share their experiences related to human rights.

Core Principles:
- Always greet the user warmly. Start by reassuring them that the conversation is a private, safe space.
- During your introduction, explicitly tell the user that if any question is unclear, they can just ask for clarification.
- Never use the exact same question twice. Be creative and vary your phrasing. Your tone should be gentle and patient.
- Ask for one piece of information at a time.
- If a user's answer seems to confuse two distinct concepts (e.g., gender identity vs. sexual orientation), gently and respectfully offer a brief, simple clarification.
- Your goal is to gather a complete report including: the person's name (preferred and official), SOGI, age, contact info, if they are reporting for themself or another, consent, details of the incident (When, What, Where, Who, Why, How), evidence, referral source, and their support needs.
- When asking about evidence, emphasize its importance for verification and strengthening their case.
- When asking about support needs, gently manage expectations about direct aid."""

# --- Initialize the AI Model ---
# We use the 'flash' model for its speed and generous free tier.
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=system_instruction
)

# --- Initialize Chat History ---
# We will store the conversation in a simple list of dictionaries.
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add the first introductory message from the AI
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am a confidential AI assistant here to provide a safe space for you to share your experiences. This conversation is private. If any of my questions are unclear, please ask for clarification. To begin, what name would you be most comfortable with me calling you?"
    })

# --- Display existing messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input and Generate AI Response ---
if prompt := st.chat_input("Your response..."):
    # Add user's message to our history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Generate AI Response ---
    try:
        # We pass the entire message history to the model on each turn.
        chat_session = model.start_chat(
            history=[
                {"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]}
                for msg in st.session_state.messages
            ]
        )
        response = chat_session.send_message(prompt)
        ai_response = response.text

        # Display AI's response and add it to history
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # This part below is commented out as st.rerun() can sometimes cause issues.
        # The app should update automatically without it.
        # st.rerun()

    except Exception as e:
        # Display a user-friendly error message
        error_message = f"An error occurred while communicating with the AI. Please try again. Error: {e}"
        st.error(error_message)
        # Also add the error to the chat so it's part of the history
        st.session_state.messages.append({"role": "assistant", "content": error_message})