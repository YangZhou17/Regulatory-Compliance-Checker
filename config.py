# -----------------------------
# Configuration and Constants
# -----------------------------
import os

REGULATORY_DOCS_DIR = "./data/regulations"  # folder containing regulatory PDFs
SOP_DOC_PATH = "./data/sop/original.docx"                # path to SOP document (DOCX)
PROCESSED_DIR = "processed_docs"              # folder to store processed PDFs
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 7      # number of sentences per chunk
OVERLAP = 1         # overlapping sentences per chunk
REPROCESS_DOCS = True

RESULT_DIR = "result"  # Define the directory where reports should be saved
REPORT_OUTPUT_PATH = os.path.join(RESULT_DIR, "report.json")
ERROR_OUTPUT_PATH = os.path.join(RESULT_DIR, "error.json")
CHUNK_TOP_K = 3  # Number of top regulatory chunks to retrieve per SOP statement
CLAUDE_API_KEY = "Your Claude API Key"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

# Weights for multiple similarity metrics (should sum to 1)
ALPHA = 0.4  # weight for semantic similarity
BETA = 0.4   # weight for TF-IDF similarity
GAMMA = 0.2 # weight for keyword overlap

# Global parameter for minimum words in an SOP statement.
MIN_SOP_WORDS = 15
MAX_SOP_WORDS = 30