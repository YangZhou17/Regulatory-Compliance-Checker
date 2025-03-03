from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
import numpy as np
from sentence_transformers import SentenceTransformer
from config import *
from utils import *


def generate_tasks():
    '''
    Generates analysis tasks by matching each SOP statement with relevant regulatory document chunks.
    
    Process:
    - Loads the embedding model and processed regulatory documents.
    - Constructs a regulatory documents dictionary with keywords, chunks, and embeddings.
    - Processes the SOP document (extracts text, tokenizes sentences, combines short sentences).
    - Precomputes embeddings for all SOP statements.
    - For each SOP statement:
      * Extracts keywords and computes similarity scores (Jaccard, semantic, TF-IDF) with regulatory chunks.
      * Selects top candidate chunks and combines them into a regulatory context.
      * Creates a task tuple (index, SOP statement, regulatory context).
    
    Returns:
    - A list of tasks for further processing.
    '''
    # Load the embedding model
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    # Load all processed regulatory documents.
    processed_docs = load_processed_data()
    
    # Build a dictionary of regulatory documents keyed by source filename.
    reg_docs = {}
    for doc in processed_docs:
        reg_docs[doc["source"]] = {
            "keywords": set(doc["keywords"]),
            "chunks": doc["chunks"],
            "embeddings": np.array(doc["embeddings"])
        }
    
    # Process the SOP document: extract text, tokenize into sentences, and combine short sentences.
    sop_text = extract_text_from_docx(SOP_DOC_PATH)
    raw_sentences = sent_tokenize(sop_text)
    sop_sentences = combine_short_sentences(raw_sentences, min_words=MIN_SOP_WORDS)
    
    # Compute embeddings for all SOP statements in one batch.
    sop_embeddings = model.encode(sop_sentences)
    
    tasks = []
    # Iterate over each SOP statement to create an analysis task.
    for idx, sop_statement in enumerate(tqdm(sop_sentences, desc="Processing SOP")):
        # Extract keywords from the SOP statement.
        sop_keywords = extract_keywords_from_text(sop_statement, top_n=20)
        sop_emb = sop_embeddings[idx]
        
        # Compute Jaccard similarity between SOP keywords and each regulatory document's keywords.
        doc_scores = {}
        for source, doc_data in reg_docs.items():
            doc_scores[source] = compute_jaccard(sop_keywords, doc_data["keywords"])
        # Select the top 2 regulatory documents based on similarity score.
        selected_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:2]
        selected_sources = [source for source, score in selected_docs if score > 0]
        # If no document scores above zero, consider all regulatory documents.
        if not selected_sources:
            selected_sources = list(reg_docs.keys())
        
        # Evaluate candidate regulatory chunks using multiple similarity metrics.
        candidate_chunks = []
        for source in selected_sources:
            doc_data = reg_docs[source]
            chunks = doc_data["chunks"]
            embeddings = doc_data["embeddings"]
            # Compute semantic similarity using cosine similarity.
            semantic_sim_vector = cosine_similarity([sop_emb], embeddings)[0]
            # Compute TF-IDF similarity between the SOP statement and each regulatory chunk.
            tfidf_sim_vector = compute_tfidf_similarity_batch(sop_statement, chunks)
            
            for j, chunk_text in enumerate(chunks):
                # Extract keywords from the regulatory chunk.
                chunk_keywords = extract_keywords_from_text(chunk_text, top_n=10)
                # Compute keyword similarity using Jaccard similarity.
                keyword_sim = compute_jaccard(sop_keywords, chunk_keywords)
                # Combine the similarity metrics using weighted factors
                final_score = ALPHA * semantic_sim_vector[j] + BETA * tfidf_sim_vector[j] + GAMMA * keyword_sim
                candidate_chunks.append((final_score, source, chunk_text))
        
        # Sort candidate chunks by the final weighted score in descending order.
        candidate_chunks = sorted(candidate_chunks, key=lambda x: x[0], reverse=True)
        # Select the top K chunks.
        selected_chunks = [chunk for score, source, chunk in candidate_chunks[:CHUNK_TOP_K]]
        # Combine the selected chunks into a single regulatory context.
        regulatory_context = "\n\n".join(selected_chunks)
        
        # Append the task as a tuple: (task index, SOP statement, regulatory context).
        tasks.append((idx, sop_statement, regulatory_context))
    
    return tasks
