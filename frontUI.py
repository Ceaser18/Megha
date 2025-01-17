import streamlit as st
import requests

# AWS Lambda API Endpoint
lambda_api_url = "https://dcfzqd4foezjwjzgtndg5pw2fi0gwhnb.lambda-url.ap-south-1.on.aws/query"
# Replace with your Lambda function URL

# Path to agent image
agent_image_path = "nurse.png"  # Ensure this path is correct
agent_description = """
Welcome to Megha Didi's Assistant! Megha Didi is here to assist you with health advice and embedding search queries.
She is caring, supportive, and knowledgeable, always ready to help with your concerns. Ask her about health or search-related tasks!
"""

# Initialize Streamlit Pages
def home_page():
    """Displays the home page with the agent's image and description."""
    st.title("Welcome to Megha Didi's Assistant!")
    st.image(agent_image_path, width=150, caption="Megha Didi")
    st.markdown(agent_description)
    if st.button("Go to Chat"):
        st.session_state.page = "chat"

def chat_page():
    """Displays the chat page for interacting with Megha Didi."""
    st.title("Chat with Megha Didi")

    # Session state for storing chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Input form
    user_input = st.text_input("You:", key="input", placeholder="Type your query here...")
    if st.button("Send"):
        if user_input.strip():
            # Send input to the Lambda function
            payload = {"query": user_input}
            try:
                response = requests.post(lambda_api_url, json=payload)
                if response.status_code == 200:
                    lambda_response = response.json().get("response", "No response from server")
                    # Save the query and response to chat history
                    st.session_state.chat_history.append((user_input, lambda_response))
                else:
                    st.session_state.chat_history.append((user_input, f"Error: {response.status_code} - {response.text}"))
            except Exception as e:
                st.session_state.chat_history.append((user_input, f"Error: {str(e)}"))

    # Display chat history
    for query, reply in st.session_state.chat_history:
        st.markdown(f"**You:** {query}")
        st.markdown(f"**Megha Didi:** {reply}")
        st.markdown("---")

    if st.button("Back to Home"):
        st.session_state.page = "home"

# Main Function to Control Page Flow
def main():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "chat":
        chat_page()

if __name__ == "__main__":
    main()
