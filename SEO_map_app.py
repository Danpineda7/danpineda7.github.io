import streamlit as st
import openai
import requests
import json
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile

# Set OpenAI API Key
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Streamlit UI Title
st.title("🚀 AI-Powered SEO Topical Map & Content Strategy Generator")

# User Input Fields
website_url = st.text_input("🌍 Enter your website URL:")
main_keyword = st.text_input("🔑 Enter your main keyword (Main Topic):")
competitor_url = st.text_input("🏆 Enter a top-ranking competitor URL:")

target_audience = st.text_input("🎯 Describe your target audience (optional):")

# SEO Objectives Checkboxes
st.subheader("📌 Select your SEO Objectives:")
objectives = {
    "Build Authority Against Competitors": st.checkbox("Build Authority Against Competitors"),
    "Rank for Broader Keywords (Higher Traffic)": st.checkbox("Rank for Broader Keywords (Higher Traffic)"),
    "Target Long-Tail Keywords (Easier Wins)": st.checkbox("Target Long-Tail Keywords (Easier Wins)"),
    "Improve Internal Linking & Content Gaps": st.checkbox("Improve Internal Linking & Content Gaps"),
    "Rank for Transactional Keywords (Leads & Sales)": st.checkbox("Rank for Transactional Keywords (Leads & Sales)")
}

selected_objectives = [key for key, value in objectives.items() if value]

# Function to Extract Topics from a Website
def extract_topics(url):
    """Scrapes the website and extracts headings as potential topics."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        topics = [heading.get_text(strip=True) for heading in soup.find_all(["h1", "h2", "h3"])]
        return list(set(topics))
    except Exception as e:
        return []

# Function to Generate SEO Topical Map
def generate_topical_map(website_topics, competitor_url, main_keyword, objectives):
    """Generates an in-depth SEO topical map based on competitor analysis and SEO objectives."""
    prompt = f"""
    Analyze the following website topics: {website_topics}
    Competitor URL: {competitor_url}
    Main Keyword: {main_keyword}
    SEO Objectives: {objectives}
    
    Generate an SEO strategy for ranking in search engines. Provide:
    - A main topic
    - 4-6 detailed subtopics
    - 3-5 keywords per subtopic
    - **For each subtopic, generate a structured SEO content plan including:**
      - Page Title (H1)
      - Meta Description
      - Recommended Word Count
      - H2 and H3 Headings
      - Internal Linking Recommendations
      - Detailed Content Outline (with bullet points)

    Return a structured JSON like this:
    {{
        "Main Topic": "{main_keyword}",
        "Subtopics": {{
            "Subtopic 1": {{
                "keywords": ["Keyword 1", "Keyword 2"],
                "page_title": "Optimized H1 Title for SEO",
                "meta_description": "Engaging description for SEO rankings.",
                "word_count": 1200,
                "headings": ["H2 Title 1", "H2 Title 2", "H3 Subsection 1"],
                "internal_links": ["Relevant Page 1", "Relevant Page 2"],
                "content_outline": [
                    "Introduction covering the topic.",
                    "Main points to discuss under each heading.",
                    "Final Call-to-Action to engage users."
                ]
            }}
        }}
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    try:
        topics_data = json.loads(response.choices[0].message.content)
        if "Main Topic" not in topics_data or "Subtopics" not in topics_data:
            raise ValueError("Invalid API response format")
        return topics_data
    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"❌ Error parsing AI response: {e}")
        return {"Main Topic": main_keyword, "Subtopics": {}}

# Function to Display SEO Content Strategy
def display_content_strategy(topical_map):
    """Displays the detailed SEO content strategy for each subtopic."""
    st.subheader("📄 SEO Content Strategy:")
    for subtopic, data in topical_map["Subtopics"].items():
        st.markdown(f"### 🔹 {subtopic}")
        st.write(f"**📌 Keywords:** {', '.join(data['keywords'])}")
        st.write(f"**🏷️ Page Title (H1):** {data['page_title']}")
        st.write(f"**📝 Meta Description:** {data['meta_description']}")
        st.write(f"**🔢 Recommended Word Count:** {data['word_count']} words")
        st.write(f"**📖 Suggested Headings:** {', '.join(data['headings'])}")
        st.write(f"**🔗 Internal Links:** {', '.join(data['internal_links'])}")
        
        st.write("**📝 Content Outline:**")
        for bullet in data["content_outline"]:
            st.markdown(f"- {bullet}")

        st.markdown("---")

# Run if User Clicks 'Generate SEO Strategy'
if st.button("🚀 Generate SEO Strategy"):
    if website_url and main_keyword and competitor_url and selected_objectives:
        website_topics = extract_topics(website_url)
        topical_map = generate_topical_map(website_topics, competitor_url, main_keyword, selected_objectives)
        if topical_map and topical_map["Subtopics"]:
            st.success("✅ SEO Strategy Generated!")
            display_content_strategy(topical_map)
        else:
            st.error("❌ Failed to generate SEO strategy. Please try again.")
    else:
        st.error("❌ Please fill in all required fields!")
