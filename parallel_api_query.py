from call_claude_api import compare_with_claude
from config import *
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

def call_claude_on_tasks(tasks, max_workers=5):
    '''
    Sends API calls to the Claude API concurrently for each task using ThreadPoolExecutor.
    Returns a list of tuples with the result dictionary and a discrepancy flag for each task.
    '''
    # Initialize a list to hold results for each task.
    results = [None] * len(tasks)

    # Create a thread pool with a maximum number of workers.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map each task submission (API call) to its task index.
        future_to_idx = {executor.submit(compare_with_claude, task[1], task[2]): task[0] for task in tasks}
        
        # Process each completed future.
        for future in tqdm(as_completed(future_to_idx), total=len(future_to_idx), desc="API Calls"):
            idx = future_to_idx[future]
            try:
                # Retrieve the result from the future.
                result, found_dis = future.result()
                results[idx] = (result, found_dis)
            except Exception as e:
                results[idx] = ({
                    "sop_statement": tasks[idx][1],
                    "regulatory_context": tasks[idx][2],
                    "discrepancies_and_improvement": f"Error: {str(e)}"
                }, True)
    return results

def save_reports(results):
    '''
    Saves the results of the API calls to JSON files.
    Generates both a full compliance report and a separate error report.
    '''
    # Ensure that the result directory exists.
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    # Extract all logs and those flagged with discrepancies or errors.
    all_logs = [result for result, flag in results]
    error_logs = [result for result, flag in results if flag]
    
    # Save the full compliance report to the designated output path.
    with open(REPORT_OUTPUT_PATH, "w") as f:
        json.dump(all_logs, f, indent=2)
    print(f"Compliance report saved to {REPORT_OUTPUT_PATH}")
    
    # Save the error report for tasks with discrepancies or errors.
    with open(ERROR_OUTPUT_PATH, "w") as f:
        json.dump(error_logs, f, indent=2)
    print(f"Error report saved to {ERROR_OUTPUT_PATH}")