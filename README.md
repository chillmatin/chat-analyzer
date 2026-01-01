# 💬 WhatsApp Chat Analyzer

A web application to analyze and visualize your WhatsApp chat exports with interactive charts and insights.


## Features

- 📊 **Interactive Visualizations** - Time series, heatmaps, GitHub-style activity calendar
- 👥 **Participant Analysis** - Compare message counts, response times, and activity patterns
- 📝 **Content Insights** - Most used words, emojis, and media sharing statistics
- 🔄 **Conversation Patterns** - Response time analysis and conversation starters
- 🔒 **Self-hosted** - So that processing happens locally on your machine

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chat-analyzer.git
   cd chat-analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**
   - The app will automatically open at `http://localhost:8501`

## How to Export WhatsApp Chat

**On Android:**
1. Open the chat → Tap ⋮ menu → More → Export chat
2. Choose "Without Media" and save the .txt file

**On iPhone:**
1. Open the chat → Tap contact name → Export Chat
2. Choose "Without Media" and save the .txt file

## Usage

1. Upload your exported WhatsApp chat file (`.txt`) in the sidebar
2. Explore different analysis views from the navigation menu
3. Filter by participants in the Content Analysis section

## Requirements

- Python 3.8+
- streamlit
- plotly
- pandas
- numpy

## License

MIT License - See [LICENSE](LICENSE) file for details

Analizing chat statistics
