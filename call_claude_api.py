import requests
from config import *


def call_claude_api(prompt):
    '''
    Sends a POST request to the Claude API with a given prompt and returns the API response text.
    '''
    # Define HTTP headers including the API key, version, and content type.
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    # Construct the data payload with model details, max token limit, and the message content.
    data = {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    }

    # Send a POST request to the Claude API endpoint.
    response = requests.post(CLAUDE_API_URL, json=data, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        if "content" in response_json and isinstance(response_json["content"], list):
            assistant_reply = response_json["content"][0].get("text", "")
            return assistant_reply.strip()
    else:
        print(f"Claude API error: {response.status_code} {response.text}")
        return ""

# DO NOT CHANGE THE FOLLOWING PROMPT
def compare_with_claude(sop_statement, regulatory_context):
    '''
    Compares an SOP statement with its regulatory context by sending both to the Claude API.
    Returns a tuple containing the result dictionary and a flag indicating if a discrepancy was found.
    '''
    # Construct a detailed prompt instructing the API to analyze discrepancies and suggest improvements.
    prompt = (
        "Analyze the following SOP statement and its related regulatory context. "
        "Identify any discrepancies between the SOP and regulatory requirements, and suggest improvements."
        "Please note that what you will see is only a small part of SOP document and regulation document."
        "Retrieved using cosine similarity and keyword matching"
        "So you do NOT need to say that if sop statement or regulatory statement is missing or incomplete."
        "ONLY check if any operation in SOP statement contradicts with the guidelines specified in regulatory statement."
        f"SOP Statement:\n{sop_statement}\n\n"
        f"Regulatory Context:\n{regulatory_context}\n\n"
        "If you found any contradiction, list them and suggest imporvement for them in detail"
        "If you have not found any contradiction, or statement and context is irrelevant, only respond 'NO DISCREPANCY', and nothing else other than these two words."
    )

    # Call the API with the constructed prompt.
    result_text = call_claude_api(prompt)

    # Build the result dictionary containing the input texts and the API response.
    result = {
        "sop_statement": sop_statement,
        "regulatory_context": regulatory_context,
        "discrepancies_and_improvement": result_text
    }
    
    # Set flag to True if the API response does not contain "no discrepancy" (ignoring case).
    found_dis = not ("no discrepancy" in result_text.lower())
    return result, found_dis
