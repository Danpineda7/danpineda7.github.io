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
    - A brief content strategy for each subtopic

    Return a JSON response like this:
    {{
        "Main Topic": "{main_keyword}",
        "Subtopics": {{
            "Subtopic 1": {{
                "keywords": ["Keyword 1", "Keyword 2"],
                "content": "Brief content strategy for this subtopic."
            }},
            "Subtopic 2": {{
                "keywords": ["Keyword 3", "Keyword 4"],
                "content": "Another content strategy suggestion."
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

# Function to Create and Display SEO Topical Map
def display_graph(topical_map):
    """Displays an SEO topical map using Matplotlib inside the Streamlit app."""
    if not topical_map or "Subtopics" not in topical_map or not topical_map["Subtopics"]:
        st.error("❌ No valid subtopics available. Try again.")
        return
    
    G = nx.DiGraph()
    main_topic = topical_map["Main Topic"]
    G.add_node(main_topic)
    
    for subtopic, data in topical_map["Subtopics"].items():
        G.add_node(subtopic)
        G.add_edge(main_topic, subtopic)
        for keyword in data["keywords"]:
            G.add_node(keyword)
            G.add_edge(subtopic, keyword)
    
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10)
    st.pyplot(plt)

# Function to Generate and Display the Content Strategy
def display_content_strategy(topical_map):
    """Displays the AI-generated content strategy for each subtopic."""
    st.subheader("📄 SEO Content Strategy:")
    for subtopic, data in topical_map["Subtopics"].items():
        st.markdown(f"### 🔹 {subtopic}")
        st.write(f"**Keywords:** {', '.join(data['keywords'])}")
        st.write(f"**Content Strategy:** {data['content']}")
        st.markdown("---")

# Function to Generate PDF of Content Strategy
def generate_pdf(topical_map):
    """Creates a downloadable PDF with the SEO content strategy."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "SEO Content Strategy Document", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Main Keyword: {topical_map['Main Topic']}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, "Content Strategy", ln=True)
    
    pdf.set_font("Arial", size=12)
    for subtopic, data in topical_map["Subtopics"].items():
        pdf.ln(5)
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, f"{subtopic}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, f"Keywords: {', '.join(data['keywords'])}")
        pdf.multi_cell(0, 8, f"Content Strategy: {data['content']}")
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# Run if User Clicks 'Generate SEO Strategy'
if st.button("🚀 Generate SEO Strategy"):
    if website_url and main_keyword and competitor_url and selected_objectives:
        website_topics = extract_topics(website_url)
        topical_map = generate_topical_map(website_topics, competitor_url, main_keyword, selected_objectives)
        if topical_map and topical_map["Subtopics"]:
            st.success("✅ SEO Strategy Generated!")
            st.subheader("📊 Interactive SEO Topical Map:")
            display_graph(topical_map)
            display_content_strategy(topical_map)

            pdf_file = generate_pdf(topical_map)
            st.download_button("📥 Download SEO Strategy PDF", open(pdf_file, "rb"), "SEO_Strategy.pdf", "application/pdf")

        else:
            st.error("❌ Failed to generate SEO strategy. Please try again.")
    else:
        st.error("❌ Please fill in all required fields!")
