import streamlit as st
import subprocess

# Define the function to interact with the Ollama model using subprocess
def get_ollama_response(prompt):
    try:
        # Run the 'llama3:latest' model and pass the prompt through stdin
        result = subprocess.run(
            ['ollama', 'run', 'llama3:latest'],
            input=prompt,
            text=True,
            capture_output=True,
            encoding='utf-8',  # Force utf-8 encoding
            errors='ignore'    # Ignore characters that can't be decoded
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit web interface

# Add logo to the app (Replace 'logo.png' with your actual logo file)
st.image("logo.svg", width=100)  # Adjust width as per your needs

# Heading and tagline
st.markdown("<h1 style='text-align: center;'>Vthink - vBot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:20px;'>Being vThinker - We are ThinK tanker</p>", unsafe_allow_html=True)

# Initialize session state for name and chat history
if "name" not in st.session_state:
    st.session_state["name"] = ""

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Ask for user's name if not provided
if not st.session_state["name"]:
    st.session_state["name"] = st.text_input("Hi ..! How can i call you?", key="name_input")

# If we have the user's name, greet them
if st.session_state["name"]:
    if len(st.session_state["chat_history"]) == 0:
        # Greet the user with positive words before the first conversation
        st.markdown(f"Hello, {st.session_state['name']}! 🌟 You're awesome, and I hope we have a great conversation today!")

    # Input for user's question
    user_input = st.text_input(f"What would you like to ask today, {st.session_state['name']}?", "", key="user_input")

    # If there's user input, get the response from Ollama and update the chat history
    if user_input and st.button("Send"):
        ollama_response = get_ollama_response(user_input)
        st.session_state.chat_history.append({"user": user_input, "bot": ollama_response})

    # Display the chat history interactively
    for i, chat in enumerate(st.session_state.chat_history):
        st.markdown(f"**{st.session_state['name']}**: {chat['user']}")

        # Display the bot's response in a text area for easy copying
        st.text_area(f"Vthink_Bot Response {i + 1}", chat['bot'], height=100, key=f"bot_response_{i}")

    # Option to clear chat history
    if st.button("Clear Chat"):
        st.session_state["chat_history"] = []

else:
    st.write("Please enter your name to start the conversation.")
