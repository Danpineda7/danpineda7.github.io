import streamlit as st
import openai
import requests
import json
from bs4 import BeautifulSoup
import networkx as nx
from pyvis.network import Network
from fpdf import FPDF
import tempfile

# Set OpenAI API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        topics = [heading.get_text(strip=True) for heading in soup.find_all(["h1", "h2", "h3"])]
        return list(set(topics))
    except Exception as e:
        return None

# Function to Generate SEO Topical Map
def generate_topical_map(website_topics, competitor_url, main_keyword, objectives):
    """Generates an SEO topical map based on competitor analysis and SEO objectives."""
    prompt = f"""
    Analyze the following website topics: {website_topics}
    Competitor URL: {competitor_url}
    Main Keyword: {main_keyword}
    SEO Objectives: {objectives}
    Generate a structured SEO topical map with a main topic, subtopics, and internal linking recommendations.
    Return JSON format.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return json.loads(response["choices"][0]["message"]["content"])

# Function to Create Interactive SEO Topical Map
def create_interactive_graph(topical_map):
    """Creates an interactive SEO topical map visualization using Pyvis."""
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
    return net

# Function to Generate PDF SEO Strategy
def generate_pdf(topical_map, website_url, main_keyword, objectives):
    """Creates a downloadable PDF with the SEO content strategy."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "SEO Content Strategy Document", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Website: {website_url}", ln=True)
    pdf.cell(200, 10, f"Main Keyword: {main_keyword}", ln=True)
    pdf.cell(200, 10, f"SEO Objectives: {', '.join(objectives)}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, f"Main Topic: {topical_map['Main Topic']}", ln=True)
    pdf.set_font("Arial", size=12)
    
    for subtopic, keywords in topical_map["Subtopics"].items():
        pdf.ln(5)
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, f"{subtopic}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, f"Keywords: {', '.join(keywords)}")
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# Run if User Clicks 'Generate SEO Strategy'
if st.button("🚀 Generate SEO Strategy"):
    if website_url and main_keyword and competitor_url and selected_objectives:
        website_topics = extract_topics(website_url)
        topical_map = generate_topical_map(website_topics, competitor_url, main_keyword, selected_objectives)
        net = create_interactive_graph(topical_map)
        pdf_file = generate_pdf(topical_map, website_url, main_keyword, selected_objectives)
        
        st.success("✅ SEO Strategy Generated!")
        st.subheader("📊 Interactive SEO Topical Map:")
        net.show("topical_map.html")
        st.markdown("[Click here to view the SEO Topical Map](topical_map.html)")
        
        st.download_button("📥 Download SEO Strategy PDF", open(pdf_file, "rb"), "SEO_Strategy.pdf", "application/pdf")
    else:
        st.error("❌ Please fill in all required fields!")
