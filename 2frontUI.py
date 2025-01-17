import streamlit as st
from streamlit_chat import message
import sys
import os

# Add the directory containing Kasturi1.py to the Python path
sys.path.append(os.path.abspath("D:\Ava\AvaTools\Aditya2Urav\Kasturi1.py"))
from Kasturi1 import nurse_agent  # Import the agent from Kasturi1.py

# Page Configuration
st.set_page_config(page_title="Kasturi Didi Assistant", layout="wide")

# Navigation Mechanism
if "page" not in st.session_state:
    st.session_state["page"] = "front_page"  # Default page

# Chat History Initialization
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Function to query the agent
def query_agent(user_input):
    try:
        # Use the `run` method of the nurse_agent to process the input
        response = nurse_agent.run(msg=user_input)
        return response
    except Exception as e:
        return f"Error communicating with the agent: {e}"

# Front Page
def front_page():
    st.title("Welcome to Megha Didi's Assistant!")
    st.image("D:\Ava\AvaTools\Aditya2Urav\nurse.png", width=150)
    st.markdown(
        """
        **Megha Didi** is your personal health assistant. She can assist you with:
        - Health-related advice.
        - Answers to your maternity-related questions.
        - Reliable, empathetic, and knowledgeable support.
        
        Click the button below to start chatting with Kasturi Didi!
        """
    )
    if st.button("Start Chat"):
        st.session_state["page"] = "chat_page"

# Chat Page
def chat_page():
    st.title("Kasturi Didi's Assistant")
    st.write("Kasturi Didi is here to help with your health and search-related queries.")

    # Chat Input
    user_input = st.text_input("You:", "", placeholder="Type your message here and press Enter...")
    if st.button("Send") and user_input:
        # Add user message to chat history
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        # Get response from agent
        response = query_agent(user_input)
        
        # Add agent response to chat history
        st.session_state["messages"].append({"role": "agent", "content": response})

    # Display Chat Messages
    st.write("### Chat History")
    chat_container = st.container()
    with chat_container:
        for message in st.session_state["messages"]:
            if message["role"] == "user":
                st.markdown(
                    f"<div style='text-align: right; background-color: #d1e7dd; border-radius: 8px; padding: 10px; margin-bottom: 10px; display: inline-block; max-width: 70%;'>{message['content']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='text-align: left; background-color: #e7e7ff; border-radius: 8px; padding: 10px; margin-bottom: 10px; display: inline-block; max-width: 70%;'>{message['content']}</div>",
                    unsafe_allow_html=True,
                )

    if st.button("Back to Home"):
        st.session_state["page"] = "front_page"

# Page Navigation
if st.session_state["page"] == "front_page":
    front_page()
elif st.session_state["page"] == "chat_page":
    chat_page()
