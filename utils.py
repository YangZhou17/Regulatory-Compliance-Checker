from config import *
import glob
import os
import pickle
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import docx

def load_processed_data():
    '''
    Loads all processed regulatory documents (pickle files) from the persistent directory.
    
    Returns:
    - A list of data dictionaries for each processed document.
    '''
    processed_files = glob.glob(os.path.join(PROCESSED_DIR, "*.pkl"))
    data_list = []
    # Iterate over each pickle file and load its content.
    for file in processed_files:
        with open(file, "rb") as f:
            data = pickle.load(f)
            data_list.append(data)
    return data_list

def extract_keywords_from_text(text, top_n=20):
    '''
    Extracts keywords from the given text.
    
    Process:
    - Tokenizes the text into words.
    - Removes stopwords and non-alphabetic tokens.
    - Uses frequency analysis to select the top_n most frequent words.
    
    Returns:
    - A set of keywords.
    '''
    # Tokenize and convert text to lowercase.
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    # Filter tokens: only alphabetic and non-stopwords.
    tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
    from collections import Counter
    freq = Counter(tokens)
    most_common = freq.most_common(top_n)
    keywords = [word for word, count in most_common]
    return set(keywords)

def extract_text_from_docx(docx_path):
    '''
    Extracts and returns text from a DOCX file.
    '''
    doc = docx.Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def compute_jaccard(set1, set2):
    '''
    Computes the Jaccard similarity between two sets.
    
    Returns:
    - The ratio of the intersection size to the union size of the two sets.
    '''
    if not set1 and not set2:
        return 0
    
    # Calculate intersection and union.
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union) if union else 0

def compute_tfidf_similarity_batch(reference_text, texts):
    '''
    Computes TF-IDF cosine similarity between a reference text and a list of texts.
    
    Returns:
    - A list of similarity scores.
    '''
    # Create a TfidfVectorizer instance and compute TF-IDF vectors.
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([reference_text] + texts)
    # Compute cosine similarity between the reference text and each text.
    sim_matrix = cosine_similarity(tfidf[0:1], tfidf[1:])
    return sim_matrix[0]

def combine_short_sentences(sentences, min_words=MIN_SOP_WORDS, max_words=MAX_SOP_WORDS):
    '''
    Combines sentences that are shorter than min_words with the previous sentence
    if the combined sentence is not longer than max_words.
    
    Returns:
    - A new list of combined sentences.
    '''
    combined = []
    # Loop through each sentence.
    for sentence in sentences:
        word_count = len(sentence.split())
        # If sentence is too short and the previous sentence exists and is within max_words, combine them.
        if word_count < min_words and combined and len(combined[-1]) < max_words:
            combined[-1] += " " + sentence.strip()
        else:
            combined.append(sentence.strip())
    return combined