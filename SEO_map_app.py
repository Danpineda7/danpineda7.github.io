import streamlit as st
import openai
import requests
import json
from bs4 import BeautifulSoup
import networkx as nx
from pyvis.network import Network
from fpdf import FPDF
import tempfile
from jinja2 import Template  # Import Jinja2 to fix Pyvis missing template issue

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
    """Generates an SEO topical map based on competitor analysis and SEO objectives."""
    prompt = f"""
    Analyze the following website topics: {website_topics}
    Competitor URL: {competitor_url}
    Main Keyword: {main_keyword}
    SEO Objectives: {objectives}
    Generate a structured SEO topical map with:
    - A main topic
    - 4-6 subtopics
    - 3-5 keywords per subtopic
    - Internal linking recommendations

    Ensure the JSON response follows this format:
    {{
        "Main Topic": "{main_keyword}",
        "Subtopics": {{
            "Subtopic 1": ["Keyword 1", "Keyword 2"],
            "Subtopic 2": ["Keyword 3", "Keyword 4"]
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

# Function to Create Interactive SEO Topical Map
def create_interactive_graph(topical_map):
    """Creates an interactive SEO topical map visualization using Pyvis."""
    if not topical_map or "Subtopics" not in topical_map or not topical_map["Subtopics"]:
        st.error("❌ No valid subtopics available. Try again.")
        return None
    
    G = nx.DiGraph()
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
    
    main_topic = topical_map["Main Topic"]
    G.add_node(main_topic, size=30, color="#FF5733")
    
    for subtopic, keywords in topical_map["Subtopics"].items():
        G.add_node(subtopic, size=20, color="#33FF57")
        G.add_edge(main_topic, subtopic)
        for keyword in keywords:
            G.add_node(keyword, size=10, color="#338FFF")
            G.add_edge(subtopic, keyword)
    
    net.from_nx(G)
    
    # ✅ Fix for missing template issue in Pyvis
    if net.template is None:
        net.template = Template("<html><head></head><body><div id='mynetwork'></div></body></html>")
    
    return net

# Run if User Clicks 'Generate SEO Strategy'
if st.button("🚀 Generate SEO Strategy"):
    if website_url and main_keyword and competitor_url and selected_objectives:
        website_topics = extract_topics(website_url)
        topical_map = generate_topical_map(website_topics, competitor_url, main_keyword, selected_objectives)
        if topical_map and topical_map["Subtopics"]:
            net = create_interactive_graph(topical_map)
            if net:
                st.success("✅ SEO Strategy Generated!")
                st.subheader("📊 Interactive SEO Topical Map:")
                net.write_html("topical_map.html")  # ✅ Use write_html() instead of show()
                st.markdown("[📊 Click here to view the SEO Topical Map](topical_map.html)")
            else:
                st.error("❌ Failed to generate SEO topical map.")
        else:
            st.error("❌ Failed to generate SEO strategy. Please try again.")
    else:
        st.error("❌ Please fill in all required fields!")
