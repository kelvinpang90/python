import streamlit as st
import os
from openai import OpenAI

# Set page title for AI chat
st.title("AI Chat Assistant")

# Initialize OpenAI client using DeepSeek API (same configuration as in main.py)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Initialize chat history if not exists
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Set initial system message to provide context and personality to the AI
    st.session_state.messages.append({
        "role": "system",
        "content": "你是一个马来西亚tiktok电商的专业人员，按照客户的需求，精准且简洁的回答用户问题，且按照用户上一个问题使用的语言回复"
    })

# Display chat messages from history (excluding system messages)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What would you like to discuss?"):
    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate and display assistant response using OpenAI API
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=st.session_state.messages,  # Send entire conversation history for context
        temperature = 0.7,
        max_tokens = 1024
        )

        assistant_response = response.choices[0].message.content

        # Display assistant response in chat
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    except Exception as e:
        error_message = f"Error communicating with AI service: {str(e)}"
        with st.chat_message("assistant"):
            st.markdown(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})

# Add a button to clear chat history
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "system",
        "content": "You are a helpful AI assistant. Keep responses clear and concise."
    })
    st.rerun()
