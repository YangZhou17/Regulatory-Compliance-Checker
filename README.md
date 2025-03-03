# Regulatory Compliance Checker

A tool to automatically analyze Standard Operating Procedure (SOP) statements against regulatory requirements. This project processes regulatory documents (PDFs) and an SOP document (DOCX), extracts relevant textual features and context, and uses the Claude API to identify any discrepancies between SOP operations and regulatory guidelines.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
---

## Overview

The Regulatory Compliance Checker is designed to streamline the process of verifying whether SOP statements comply with the applicable regulatory requirements. By leveraging natural language processing (NLP) techniques and the Claude API, the project:
- Processes regulatory PDFs to extract text, generate embeddings, and extract keywords.
- Processes an SOP document, segments it into coherent statements, and computes similarity metrics.
- Generates comparison tasks by selecting the most relevant regulatory context for each SOP statement.
- Executes parallel API calls to check for discrepancies and generate improvement suggestions.
- Saves the results in JSON reports, highlighting both overall compliance and specific discrepancies.

---

## Features

- **Regulatory Document Processing:** 
  - Extract text from PDF files.
  - Split text into chunks with configurable window sizes and overlaps.
  - Compute embeddings using SentenceTransformer.
  - Extract keywords based on token frequency.
  
- **SOP Document Analysis:**
  - Extract text from DOCX files.
  - Tokenize and combine short sentences to form complete SOP statements.
  
- **Task Generation:**
  - Select relevant regulatory document chunks based on keyword overlap, semantic similarity (cosine similarity), and TF-IDF similarity.
  - Create tasks pairing each SOP statement with its corresponding regulatory context.
  
- **Parallel API Calls:**
  - Utilize multithreading (via ThreadPoolExecutor) to perform concurrent calls to the Claude API.
  - Analyze each task to identify discrepancies and generate improvement suggestions.
  
- **Reporting:**
  - Save comprehensive compliance reports (all tasks) and error reports (tasks with discrepancies) in JSON format.

---

## Installation and Setup

1. **System Dependencies:**

    Before installing the Python packages, install the following system packages using apt:
    ```bash
    sudo apt update
    sudo apt install build-essential python3-dev libopenblas-dev libopenmpi-dev
    ```

2. **Python Dependencies:**

    Create a virtual environment (optional but recommended) and install the required Python packages:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install requests sentence-transformers nltk PyPDF2 python-docx scikit-learn tqdm numpy
    ```

2. **Set Up Configuration:**

   `config.py` file in the project root with your configuration settings.
   - **API Configuration:**  
     - `CLAUDE_API_KEY`: Your Claude API key.
     - `CLAUDE_API_URL`: The API endpoint URL.
   - **Document Directories and Paths:**
     - `REGULATORY_DOCS_DIR`: Directory containing the regulatory PDF files.
     - `PROCESSED_DIR`: Directory where processed regulatory data will be stored.
     - `SOP_DOC_PATH`: Path to the SOP DOCX file.
   - **Processing Parameters:**
     - Chunking parameters (e.g., `CHUNK_SIZE`, `OVERLAP`).
     - Similarity scoring weights (`ALPHA`, `BETA`, `GAMMA`).
     - Minimum and maximum word limits for combining SOP sentences (`MIN_SOP_WORDS`, `MAX_SOP_WORDS`).
   - **Output Paths:**
     - `REPORT_OUTPUT_PATH`: Path for the final compliance report.
     - `ERROR_OUTPUT_PATH`: Path for the error/discrepancy report.
   - **Reprocessing Flag:**
     - `REPROCESS_DOCS`: Set to `True` if you want to reprocess regulatory documents on each run.

3. **Download NLTK Data (if not already installed):**

   The project downloads the required NLTK data automatically on first run, but you can also run:

   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('punkt_tab')
   ```

---

## Usage

Run the main script to execute the entire pipeline:

```bash
python main.py
```

- If `REPROCESS_DOCS` is set to `True` in your configuration, the script will process the regulatory PDF files before generating tasks.
- The script then generates tasks from the SOP document, sends parallel requests to the Claude API, and saves the generated reports to the specified output paths.

---

## Project Structure

```
├── call_claude_api.py         # API call functions including comparison with regulatory context.
├── main.py                   # Main entry point to run the pipeline.
├── parallel_api_query.py     # Handles parallel API calls and report saving.
├── process_regulatory_file.py# Processes regulatory PDF files into structured data.
├── report_generator.py       # Generates tasks by comparing SOP statements with regulatory context.
├── utils.py                  # Utility functions for text extraction, keyword extraction, and similarity computations.
├── config.py                 # Configuration file (to be created by the user).
├── requirements.txt          # List of Python package dependencies.
└── data/                     # Additional data resources.
```

---