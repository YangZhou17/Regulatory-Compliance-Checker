import os
import glob
import pickle
from collections import Counter
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from config import *

# Ensure required NLTK data is downloaded for tokenization and stopword filtering.
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

def extract_text_from_pdf(pdf_path):
    '''
    Extracts and returns text content from a PDF file.
    '''
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def group_sentences_into_chunks(sentences, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    '''
    Groups a list of sentences into overlapping chunks.
    
    Parameters:
    - sentences: List of sentences.
    - chunk_size: Number of sentences per chunk.
    - overlap: Number of sentences to overlap between chunks.
    
    Returns:
    - List of text chunks.
    '''
    chunks = []
    i = 0
    # Slide through the sentence list using the specified chunk size and overlap.
    while i < len(sentences):
        chunk = " ".join(sentences[i: i+chunk_size])
        chunks.append(chunk)
        i += (chunk_size - overlap)
    return chunks

def extract_keywords_from_text(text, top_n=20):
    '''
    Extracts the top_n most frequent keywords from the provided text.
    
    Process:
    - Tokenizes text.
    - Filters out stopwords and non-alphabetic tokens.
    - Uses frequency analysis to determine the most common words.
    
    Returns:
    - A list of keywords.
    '''
    # Tokenize the lowercased text.
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))

    # Filter tokens: keep only alphabetic words not in the stopwords list.
    tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
    freq = Counter(tokens)
    most_common = freq.most_common(top_n)
    keywords = [word for word, count in most_common]
    return keywords

def process_pdf(pdf_path, model):
    '''
    Processes a PDF file by:
    - Extracting text.
    - Splitting text into sentences and grouping them into chunks.
    - Computing embeddings for each chunk using the provided model.
    - Extracting keywords from the text.
    
    Returns:
    - A dictionary containing the source filename, text chunks, embeddings, and keywords.
    '''
    print(f"Processing: {pdf_path}")
    # Extract text from the PDF.
    text = extract_text_from_pdf(pdf_path)

    # Split text into individual sentences.
    sentences = sent_tokenize(text)

    # Group sentences into chunks using a sliding window approach.
    chunks = group_sentences_into_chunks(sentences)

    # Compute embeddings for each text chunk.
    embeddings = model.encode(chunks)

    # Extract keywords from the complete text.
    keywords = extract_keywords_from_text(text, top_n=20)

    # Package all processed data into a dictionary.
    data = {
        "source": os.path.basename(pdf_path),
        "chunks": chunks,
        "embeddings": [emb.tolist() for emb in embeddings],
        "keywords": keywords
    }
    return data

def process_regulatory_files():
    '''
    Processes all regulatory PDF files in the specified directory.
    For each file:
    - Processes the file using process_pdf.
    - Saves the processed data as a pickle file.
    Skips files that have already been processed.
    '''
    # Create the processed files directory if it doesn't exist.
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
    
    # Initialize the SentenceTransformer model.
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    # Retrieve all PDF files from the regulatory documents directory.
    pdf_files = glob.glob(os.path.join(REGULATORY_DOCS_DIR, "*.pdf"))
    for pdf_file in pdf_files:
        output_file = os.path.join(PROCESSED_DIR, os.path.basename(pdf_file) + ".pkl")
        if os.path.exists(output_file):
            print(f"Already processed {pdf_file}, skipping.")
            continue
        data = process_pdf(pdf_file, model)
        # Save the processed data to a pickle file.
        with open(output_file, "wb") as f:
            pickle.dump(data, f)
        print(f"Saved processed data for {pdf_file} to {output_file}")

# if __name__ == "__main__":
#     process_regulatory_files()
