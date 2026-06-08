# Research Paper Summarization Agent

An AI-powered application that automatically summarizes research papers and enables users to interact with uploaded documents through natural language queries. The system leverages Large Language Models (LLMs) to generate concise summaries and provide contextual answers based on the content of research papers.

## Features

* Upload research papers in PDF format
* Extract and process text from academic documents
* Generate concise and meaningful summaries
* Ask questions about uploaded research papers
* Interactive user interface built with Streamlit
* LLM-powered summarization and question answering
* Support for large documents through text chunking

## Technologies Used

* **Python**
* **Flask** – User Interface
* **LangChain** – LLM Workflow Management
* **Groq API** – Large Language Model Inference
* **PyMuPDF / PDF Processing Libraries** – PDF Text Extraction

## Project Structure

```text
research-paper-summarization-agent/
│
├── summarizer/              # Core summarization modules
├── .streamlit/              # Streamlit configuration
├── app.py                   # Streamlit application
├── flask_app.py             # Flask backend
├── flask_app_old.py         # Previous backend implementation
├── test.py                  # Testing scripts
├── requirements.txt         # Project dependencies
└── README.md
```

## How It Works

1. Upload a research paper in PDF format.
2. The system extracts text from the document.
3. Extracted text is cleaned and preprocessed.
4. The document is divided into smaller chunks for efficient processing.
5. The LLM generates summaries for individual chunks.
6. Chunk summaries are combined into a final comprehensive summary.
7. Users can ask questions related to the uploaded paper and receive context-aware responses.

## Prerequisites

Before running the project, ensure that you have:

* Python 3.9 or later
* pip package manager
* Groq API Key

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/momina-22/research-paper-summarization-agent.git
cd research-paper-summarization-agent
```

### 2. Create a Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the project root directory and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

Replace `your_groq_api_key` with your actual API key.

## Running the Application

### Streamlit Frontend

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

### Flask Backend (Optional)

If the project requires the Flask backend, run:

```bash
python flask_app.py
```

The backend will typically run on:

```text
http://localhost:5000
```

## Usage

### Generate a Summary

1. Launch the application.
2. Upload a research paper in PDF format.
3. Wait for the document to be processed.
4. Generate the summary.
5. Review the summarized content.

### Ask Questions

You can ask questions such as:

* What is the main contribution of this paper?
* What methodology was used?
* What dataset was utilized?
* What are the limitations of the study?
* What future work is suggested?

The system retrieves relevant information from the uploaded document and generates context-aware responses.


### Empty or Incomplete Summaries

* Ensure the PDF contains selectable text.
* Verify that the uploaded file is not image-only.
* Confirm that your API key is valid.
* Check your internet connection.

## Future Improvements

* Multi-document summarization
* Literature review generation
* Citation extraction
* Semantic search capabilities
* Export summaries to PDF or DOCX
* Support for additional LLM providers


## License

This project is intended for educational and research purposes.


_Developed with Python, Flask, LangChain, and Groq LLM Acceleration._
