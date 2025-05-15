# Import matplotlib and set the backend BEFORE importing pyplot
import matplotlib
matplotlib.use('Agg') # Use the 'Agg' backend for non-interactive plotting

import os
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS # Import CORS
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI # You can replace with other LLMs if needed
import matplotlib.pyplot as plt # Import pyplot AFTER setting the backend
import base64
from io import BytesIO
import json # Import json for handling JSON files

# Import PDF processing libraries
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

# --- Configuration ---
# Set your OpenAI API key here.
# It's recommended to use environment variables for security.
# Example: export OPENAI_API_KEY='YOUR_API_KEY' in your terminal
# Or use a .env file and python-dotenv
# from dotenv import load_dotenv
# load_dotenv()
# API_KEY = os.getenv("OPENAI_API_KEY")
API_KEY = "OPENAI_API_KEY" # Replace with your actual API key or use environment variable

if not API_KEY or API_KEY == "YOUR_API_KEY":
    print("WARNING: OPENAI_API_KEY not set. Please set it in app.py or as an environment variable.")
    # You might want to exit or handle this more gracefully in a production app.
    # For this example, we'll continue but PandasAI calls will fail without a key.


UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
PLOT_FOLDER = os.path.join(STATIC_FOLDER, 'plots')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLOT_FOLDER, exist_ok=True)

# --- Flask App Setup ---
app = Flask(__name__, static_folder=STATIC_FOLDER)
CORS(app) # Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# Global variable to hold the SmartDataframe instance
# In a real application, you might want to manage sessions for multiple users
smart_df = None
uploaded_filename = None

# --- Data Analyst Persona Prompt ---
# This prompt guides the LLM to act as a data analyst
DATA_ANALYST_PROMPT = """
You are a helpful and insightful data analyst.
Your goal is to analyze the provided dataset and answer questions based on the data.
When asked a question, you should:
1. Understand the user's intent.
2. Analyze the relevant columns or data points in the dataset.
3. Provide a clear and concise answer based *only* on the data available.
4. If a plot is requested or would help illustrate the answer, generate an appropriate plot using matplotlib.
5. Explain your findings in a way that is easy to understand.
6. If you cannot answer the question based on the data, state that clearly.
7. Avoid making assumptions or bringing in outside knowledge unless specifically asked to do so.
8. Present numerical results accurately.
9. If asked to show data, provide a sample of the relevant rows or columns if appropriate.
"""


# --- Helper Functions ---

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    output_string = StringIO()
    with open(pdf_path, 'rb') as in_file:
        # Use LAParams for better layout analysis, which can help with tables
        # though full table extraction requires more logic
        laparams = LAParams()
        extract_text_to_fp(in_file, output_string, laparams=laparams)
    return output_string.getvalue()


def load_data(filepath):
    """Loads data from various file types into a pandas DataFrame."""
    try:
        file_extension = os.path.splitext(filepath)[1].lower()
        if file_extension == '.csv':
            df = pd.read_csv(filepath)
        elif file_extension in ['.xls', '.xlsx']:
            df = pd.read_excel(filepath)
        elif file_extension == '.json':
            # Assuming a simple JSON structure that pandas can read directly
            df = pd.read_json(filepath)
        elif file_extension == '.txt':
            # Basic text file reading - assumes a simple delimited format like CSV
            # You might need more sophisticated parsing for complex text files
            df = pd.read_csv(filepath, delimiter='\t') # Assuming tab-delimited, adjust as needed
        elif file_extension == '.pdf':
            # Extract text from PDF and create a DataFrame
            pdf_text = extract_text_from_pdf(filepath)
            # Create a DataFrame with one column, where each row is a line of text
            # Note: This is basic. Extracting tables from PDF is much more complex.
            lines = pdf_text.splitlines()
            df = pd.DataFrame(lines, columns=['text_content'])
            # Remove empty lines
            df = df[df['text_content'].str.strip() != ''].reset_index(drop=True)

            if df.empty:
                 return None, "Could not extract any meaningful text from the PDF."

        else:
            return None, f"Unsupported file type: {file_extension}"

        # Initialize SmartDataframe with the loaded data and LLM
        llm = OpenAI(api_token=API_KEY)
        global smart_df
        # Add the system_prompt to the config
        smart_df = SmartDataframe(df, config={"llm": llm, "system_prompt": DATA_ANALYST_PROMPT})
        return df, None # Return the raw df and no error
    except Exception as e:
        return None, str(e)

def save_plot_to_base64(plot_object):
    """Saves a matplotlib plot to a base64 string."""
    if plot_object is None:
        return None

    try:
        # Ensure we are working with the current figure if plot_object is not explicitly a figure
        # PandasAI often returns the Axes object, so get the figure from it
        if isinstance(plot_object, plt.Axes):
            fig = plot_object.get_figure()
        elif isinstance(plot_object, plt.Figure):
            fig = plot_object
        else:
             # Assume it's the current active figure if type is unknown
             fig = plt.gcf()


        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('ascii')
        plt.close(fig) # Close the figure to free memory
        return img_base64
    except Exception as e:
        print(f"Error saving plot: {e}")
        return None


# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main index page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file uploads."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        global uploaded_filename
        uploaded_filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_filename)
        file.save(filepath)

        df, error = load_data(filepath)

        if error:
            # Clean up the uploaded file if loading failed
            os.remove(filepath)
            uploaded_filename = None
            return jsonify({'error': f'Failed to load data: {error}'}), 500
        else:
            # Optionally, remove the file after loading into memory if you don't need to keep it
            # os.remove(filepath)
            # For this example, we'll keep it in the uploads folder

            # Return some info about the loaded data (e.g., columns, shape)
            data_info = {
                'filename': uploaded_filename,
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'message': 'File uploaded and data loaded successfully.'
            }
            # Add a specific note for PDF uploads
            if os.path.splitext(uploaded_filename)[1].lower() == '.pdf':
                 data_info['message'] += " Note: For PDFs, only text content was extracted. Complex analytical queries on tabular data within the PDF might not work as expected."

            return jsonify(data_info), 200

@app.route('/chat', methods=['POST'])
def chat_with_data():
    """Handles chat queries."""
    if smart_df is None:
        return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400

    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Use PandasAI to process the query
        # The system_prompt is already set during SmartDataframe initialization
        response = smart_df.chat(query)

        # PandasAI might return different types of responses (text, dataframe, plot object)
        result_type = 'text'
        result_content = str(response)
        plot_base64 = None

        # Check if the response is a matplotlib figure or axes
        if isinstance(response, (plt.Figure, plt.Axes)):
             plot_base64 = save_plot_to_base64(response)
             if plot_base64:
                 result_type = 'plot'
                 result_content = 'Generated plot:' # Message to display above the plot
             else:
                 result_type = 'text'
                 result_content = "Could not generate or save the plot."
        elif isinstance(response, pd.DataFrame):
             result_type = 'dataframe'
             result_content = response.to_html() # Convert dataframe to HTML table
        # You might add checks for other types PandasAI might return

        return jsonify({
            'type': result_type,
            'content': result_content,
            'plot_base64': plot_base64
        }), 200

    except Exception as e:
        print(f"Error during chat processing: {e}")
        return jsonify({'error': f'An error occurred while processing your query: {e}'}), 500

# Route to serve static files (like plots if saved as files) - currently using base64
# @app.route('/static/<path:filename>')
# def static_files(filename):
#     return send_from_directory(app.config['STATIC_FOLDER'], filename)


if __name__ == '__main__':
    # In a production environment, use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True) # debug=True is good for development
