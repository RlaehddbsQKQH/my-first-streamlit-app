import streamlit as st
from openai import OpenAI
import time

# --- OpenAI Client Setup ---
# Initialize the OpenAI client with your API key and base URL.
# The API key is provided directly in the prompt, but in a real application,
# it's best practice to load it from environment variables or Streamlit secrets.
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    base_url="https://api.upstage.ai/v1"
)

# --- Streamlit App Configuration ---
st.set_page_config(page_title="학생 심리 상담 챗봇 💬", page_icon="💡")
st.title("학생 심리 상담 챗봇 💬")
st.markdown("""
이 챗봇은 학생들의 심리적 어려움을 경청하고, 지지하며, 필요한 경우 추가적인 도움을 받을 수 있는 방향을 제시하는 데 목적이 있습니다.
전문적인 의료 또는 심리 치료를 대체할 수 없으며, 긴급한 상황에서는 전문가의 도움을 받으세요.
""")

# --- Initialize Chat History ---
# Check if 'messages' is already in session_state. If not, initialize it.
# This ensures chat history persists across reruns of the app.
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add an initial system message to guide the AI's behavior
    st.session_state.messages.append(
        {"role": "system", "content": "당신은 학생들의 심리 상담을 돕는 친절하고 공감 능력 있는 AI 상담사입니다. 학생들의 이야기를 경청하고, 지지하며, 긍정적인 방향으로 이끌어 주세요. 전문적인 진단이나 치료는 제공하지 않으며, 필요시 전문가의 도움을 권유할 수 있습니다."}
    )
    # Add an initial welcome message from the AI
    st.session_state.messages.append(
        {"role": "assistant", "content": "안녕하세요! 저는 학생들의 마음 건강을 돕는 AI 상담사입니다. 어떤 이야기든 편하게 나눠주세요. 제가 경청하고 함께 고민해 드릴게요."}
    )

# --- Display Chat Messages ---
# Iterate through the messages in session_state and display them.
# Skip the system message when displaying to the user.
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Chat Input and Response Generation ---
# Get user input from the chat input box.
if prompt := st.chat_input("여기에 메시지를 입력하세요..."):
    # Add user message to chat history and display it.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for the API call.
    # The API expects a list of dictionaries with 'role' and 'content'.
    messages_for_api = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    # Display a placeholder for the assistant's response.
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Call the OpenAI API with the 'solar-pro2' model in streaming mode.
            stream = client.chat.completions.create(
                model="solar-pro2",
                messages=messages_for_api,
                stream=True,
            )

            # Iterate through the streamed chunks and build the response.
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌") # Add a blinking cursor effect
            message_placeholder.markdown(full_response) # Display final response without cursor

            # Add the assistant's full response to chat history.
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"API 호출 중 오류가 발생했습니다: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "죄송합니다. 현재 상담을 진행할 수 없습니다. 잠시 후 다시 시도해 주세요."})
