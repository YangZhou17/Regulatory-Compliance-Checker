from process_regulatory_file import process_regulatory_files
from report_generator import generate_tasks
from parallel_api_query import call_claude_on_tasks, save_reports
from config import REPROCESS_DOCS

def main():
    '''
    Main entry point for the application.
    It optionally reprocesses regulatory files, generates analysis tasks,
    calls the Claude API in parallel for each task, and saves the reports.
    '''
    # Reprocess regulatory documents if the configuration flag is set.
    if REPROCESS_DOCS:
        process_regulatory_files()
    
    # Generate tasks by processing the SOP and regulatory documents.
    tasks = generate_tasks()

    # Execute API calls concurrently for each task.
    results = call_claude_on_tasks(tasks)
    
    # Save the results to JSON reports.
    save_reports(results)
    
if __name__ == "__main__":
    main()
