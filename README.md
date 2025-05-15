# 📊 Data analysis AI Application

**Data Chat** is a simple yet powerful web application built with **Flask**, **Pandas**, and **PandasAI**. It allows users to upload various types of data files (CSV, Excel, JSON, Text, PDF) and interact with them using natural language. The chatbot can answer questions, analyze data, and even generate plots directly in the web interface.

---

## 🚀 Features

* 📁 Upload multiple data formats: `.csv`, `.xls`, `.xlsx`, `.json`, `.txt`, `.pdf`
* 💬 Chat with your data using natural language queries
* 📊 Generate and display plots based on data analysis
* 📄 Basic text extraction from PDFs
* ⏳ Loading indicators for file uploads and chat responses
* 👨‍💼 Built-in data analyst persona for contextual and insightful answers

---

## 🧰 Prerequisites

Before you begin, make sure you have:

* **Python 3.7+**: [Download](https://www.python.org/downloads/)
* **Git**: [Download](https://git-scm.com/)
* **OpenAI API Key**: [Get API Key](https://platform.openai.com/)

---

## 🔧 Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/poojithinavolu/
   cd AI_Dataanalyzer
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

3. **Activate the environment**:

   * On **Windows**:

     ```bash
     .\venv\Scripts\activate
     ```

   * On **macOS/Linux**:

     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:

   ```bash
   pip install Flask pandas pandasai numpy matplotlib openpyxl python-dotenv flask-cors pdfminer.six
   ```

---

## 🔐 Configuration

Create a `.env` file in the root directory and add your OpenAI API key:

```bash
OPENAI_API_KEY='YOUR_API_KEY'
```

> 💡 You may hardcode the key in `chatbot.py`, but using `.env` is more secure and recommended.

---

## ▶️ Running the Application

1. Ensure your virtual environment is activated.
2. Run the Flask server:

   ```bash
   python chatbot.py
   ```
3. Open your browser and go to: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 💡 How to Use

1. Upload a supported file (`.csv`, `.xls`, `.xlsx`, `.json`, `.txt`, or `.pdf`)
2. Once uploaded, you’ll see a confirmation message in the chat box.
3. Ask questions or request plots about the data in plain English.
4. Get responses, insights, and visualizations from the AI-powered data analyst.

---

## 📁 File Structure

```
your-project-folder/
├── chatbot.py               # Main Flask app
├── .env                     # Environment file with OpenAI API key
├── uploads/                 # Uploaded files (auto-created)
├── static/
│   └── plots/               # Optional: plot images if saved as files
└── templates/
    └── index.html           # Frontend template
```

---

## ⚠️ Notes

* **PDF Support**: Only plain text is extracted. Tabular data may require advanced PDF parsing.
* **Security**: Avoid hardcoding API keys in production. Use `.env` or environment variables.
* **Scalability**: Designed for small/medium datasets and single users. Consider scaling for larger or concurrent use.

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit pull requests with improvements, features, or fixes.

---
