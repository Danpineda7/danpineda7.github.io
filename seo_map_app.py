import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Load API key securely from Streamlit Secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# Streamlit UI setup
st.set_page_config(page_title="AI SEO Chat", layout="wide")
st.title("💬 AI-Powered SEO Topical Map Chat")

st.write("📝 Chat with AI to refine your SEO strategy. Share a **topic & URL**, then request improvements!")

# Function to extract text from a webpage
def extract_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text_content = " ".join([p.get_text() for p in paragraphs])
            return text_content[:4000]  # Limit to 4000 characters (GPT limit)
        else:
            return None
    except Exception as e:
        return None

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an SEO expert. Guide the user in building a structured topical map based on their topic and website."}
    ]

# Display chat history
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.write(f"📝 **You:** {msg['content']}")
    else:
        st.write(f"🤖 **AI:** {msg['content']}")

# User input for chat
chat_input = st.text_input("💬 Type your SEO request...")

if st.button("Send"):
    if chat_input:
        st.session_state.messages.append({"role": "user", "content": chat_input})

        # Extract URL from user message (if provided)
        extracted_url = None
        for word in chat_input.split():
            if word.startswith("http"):
                extracted_url = word
                break

        page_content = ""
        if extracted_url:
            st.write(f"🔗 Fetching content from: {extracted_url}")
            page_content = extract_text_from_url(extracted_url)
            if not page_content:
                st.warning("⚠️ Unable to extract content from this URL.")

        # Build prompt
        prompt = chat_input
        if page_content:
            prompt += f"\n\nHere is additional context from the provided webpage:\n{page_content}"

        # Call OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=st.session_state.messages + [{"role": "user", "content": prompt}]
            )

            ai_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            # Display AI response
            st.write(f"🤖 **AI:** {ai_reply}")

            # Save chat history
            with open("seo_map_chat.txt", "w", encoding="utf-8") as file:
                for msg in st.session_state.messages:
                    file.write(f"{msg['role'].capitalize()}: {msg['content']}\n")

            st.download_button("📥 Download SEO Map", ai_reply, file_name="seo_map.txt")

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
