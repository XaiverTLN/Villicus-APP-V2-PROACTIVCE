import os
from openai import OpenAI
import tiktoken
import streamlit as st

api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

MODEL = "gpt-4o-search-preview-2025-03-11"
MAX_TOKENS = 100
SYSTEM_PROMPT = "Your a helpful AI Aissitant named Villicus who's knowledgeable in cybersecurity. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information and deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
TOKEN_BUDGET = 100


def get_encoding(model):
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        print(f"Warning: Tokens for model '{model}' not found. Returning to 'c1100k_base',")
        return tiktoken.get_encoding("cl100k_base")


ENCODING = get_encoding(MODEL)


def count_tokens(text):
    return len(ENCODING.encode(text))


def total_tokens_used(messages):
    try:
        return sum(count_tokens(msg["content"]) for msg in messages)
    except Exception as e:
        print(f"[token count error]: {e}")
        return 0


def enforce_token_budget(messages, budget=TOKEN_BUDGET):
    try:
        while total_tokens_used(messages) > budget:
            if len(messages) <= 2:
                break
            messages.pop(1)
    except Exception as e:
        print(f"[token budget error]:{e}")


if not api_key:
    st.error("Missing OPENAI_API_KEY")
    st.stop()
client = OpenAI(api_key=api_key)


def chat(user_input, max_tokens, messages_key="messages"):
    messages = st.session_state[messages_key]
    messages.append({"role": "user", "content": user_input})

    enforce_token_budget(messages)

    with st.spinner("Generating Response..."):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
        )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    return reply


def get_system_prompt(system_message_type):
    if system_message_type == "Villicus: Cybersecurity Informat Assistant":
        return "Your a helpful AI Aissitant named Villicus who's knowledgeable in the foundations of cybersecurity. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information using only expert verified/professional sources for your responses. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
    elif system_message_type == "Villicus: Cybersecurity Threat Assistant":
        return "Your a helpful AI Aissitant named Villicus who's knowledgeable in all forms, types, methods of attack, and preventions of cyber threats and attacks. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information using only expert verified/professional sources for your responses. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
    elif system_message_type == "Villicus: Cyber Saftey Assistant":
        return "Your a helpful AI Aissitant named Villicus who's knowledgeable in all ways, methods, and strategies of cyber threats and attacks. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information using only expert verified/professional sources for your respones. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
    elif system_message_type == "Villicus: Custom Cybersecurity Related Assistant":
        return "Your a helpful AI Aissitant named Villicus who's knowledgeable in all things related to cybersecurity. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information using only expert verified/professional sources for your respones. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
    elif system_message_type == "Villicus: Cybersecurity Phishing Threat Assistant":
        return "Your a helpful AI Aissitant named Villicus who's knowledgeable in all things related to phishing cyber threats. Be sure to introduce yourself in your first response and provide reasoning on why a link is most likely a phising attempt. Also reveal a summary about the contnets of the linbk if possible and if you cannot, tell the user that. Make sure to reveal the sources of your information using only expert verified/professional sources for your respones. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
    else:
        return "Your a helpful AI Aissitant named Villicus who's knowledgeable in cybersecurity. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information and deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."


def init_session_state(system_message_type):
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": get_system_prompt(system_message_type)}]

    if "phishing_messages" not in st.session_state:
        st.session_state.phishing_messages = [{
            "role": "system",
            "content": get_system_prompt("Villicus: Cybersecurity Phishing Threat Assistant"),
        }]

    if "phishing_results" not in st.session_state:
        st.session_state.phishing_results = []


def render_chat_tab(max_tokens):
    st.subheader("Villicus Chatbot Cybersecurity Assistant Mode")
    system_message_type = st.sidebar.selectbox(
        "System Message",
        (
            "Villicus: Cybersecurity Informat Assistant",
            "Villicus: Cybersecurity Threat Assistant",
            "Villicus: Cyber Saftey Assistant",
            "Villicus: Custom Cybersecurity Related Assistant",
        ),
    )

    selected_system_prompt = get_system_prompt(system_message_type)
    st.write(f"{system_message_type}")
    st.write(f"{selected_system_prompt}")

    if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
        st.session_state.messages[0]["content"] = selected_system_prompt

    if st.sidebar.button("Reset Conversation"):
        st.session_state.messages = [{"role": "system", "content": selected_system_prompt}]
        st.success("Conversation Reset.")

    if prompt := st.chat_input("What would you like to know?"):
        chat(prompt, max_tokens=max_tokens, messages_key="messages")

    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_phishing_tab(max_tokens):
    st.subheader("Villicus Chatbot Phishing Threat Assistant Mode")
    url_input = st.text_input("Enter a URL to analyze for phishing threats:")
    email_input = st.text_input("Enter an email to analyze for phishing threats:")

    analyze_clicked = st.button("Analyze URL for Phishing Threats")

    if analyze_clicked and url_input:
        prompt = (
            "Analyze the following URL for phishing threats. "
            "Provide risk level, key red flags, and a short explanation: "
            f"{url_input}"
        )
        reply = chat(prompt, max_tokens=max_tokens, messages_key="phishing_messages")
        st.session_state.phishing_results.append(f"User: {prompt}")
        st.session_state.phishing_results.append(f"Villicus: {reply}")

    if analyze_clicked and email_input:
        prompt = (
            "Analyze the following email for phishing threats. "
            "Provide risk level, key red flags, and a short explanation: "
            f"{email_input}"
        )
        reply = chat(prompt, max_tokens=max_tokens, messages_key="phishing_messages")
        st.session_state.phishing_results.append(f"User: {prompt}")
        st.session_state.phishing_results.append(f"Villicus: {reply}")

    if st.sidebar.button("Reset Phishing Conversation"):
        st.session_state.phishing_results = []
        st.session_state.phishing_messages = [{
            "role": "system",
            "content": get_system_prompt("Villicus: Cybersecurity Phishing Threat Assistant"),
        }]
        st.success("Phishing Conversation Reset.")

    if prompt := st.chat_input("What would you like to know about phishing threats?"):
        reply = chat(prompt, max_tokens=max_tokens, messages_key="phishing_messages")
        st.session_state.phishing_results.append(f"User: {prompt}")
        st.session_state.phishing_results.append(f"Villicus: {reply}")

    for message in st.session_state.phishing_results:
        st.markdown(message)


def main():
    init_session_state("Villicus: Cybersecurity Informat Assistant")

    st.title("Villicus Cybersecurity Chatbot")
    st.subheader("Ver.2")
    st.sidebar.header("Options")
    st.sidebar.write("Customize the token amount and change your chatbot's specialty area!")
    max_tokens = st.sidebar.slider("Max Tokens", 1, 250, MAX_TOKENS)

    tab1, tab2 = st.tabs(["Villicus Chatbot Assistant Mode", "Villicus Phishing Threat Assistant Mode"])

    with tab1:
        render_chat_tab(max_tokens)
    with tab2:
        render_phishing_tab(max_tokens)


if __name__ == "__main__":
    main()
