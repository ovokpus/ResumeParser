#!/usr/bin/env python3
"""
Resume parsing and logging script with detailed output.

This script processes resumes from an input folder, parsing each resume file
sequentially and logging results to both CSV and JSON formats. It provides
detailed, step-by-step output showing the parsing process, extracted data,
and any warnings or errors encountered.

Features:
    - Processes PDF and DOCX resume files from a specified folder
    - Recursively searches subdirectories for resume files
    - Shows detailed parsing progress with timing information
    - Logs results to CSV (append-only single file) and JSON (timestamped files)
    - Provides interactive pause between resumes (when run in terminal)
    - Generates summary statistics after processing

Output Files:
    - CSV: outputs/csv/parsing_log.csv (single append-only file with date/timestamp columns)
    - JSON: outputs/json/parsing_log_<timestamp>.json (timestamped files per processing session)

Usage:
    python parse_and_log.py [input_folder]
    
    If no folder is specified and 'resumes/' exists, it will be used as default.

Examples:
    python parse_and_log.py                    # Uses default 'resumes/' folder
    python parse_and_log.py tests/test_data    # Process resumes from test data folder
    python parse_and_log.py ./my_resumes       # Process resumes from custom folder

Exit Codes:
    0: Success
    1: Error (invalid arguments, folder not found, no files found)
"""

import sys
import json
import time
from pathlib import Path
from resume_parser import ResumeParserFramework
from resume_parser.utils.parsing_logger import ParsingLogger
from resume_parser.exceptions import ResumeParserError


def parse_single_resume(resume_path: Path, output_dir: str = "outputs") -> None:
    """
    Parse a single resume file and log results with detailed output.
    
    This function handles the complete parsing workflow for a single resume:
    1. Parses the file to extract text content
    2. Extracts structured data (name, email, skills)
    3. Determines parsing status (successful, partial success, failed)
    4. Displays detailed output including extracted data and JSON representation
    5. Logs results to both CSV and JSON files
    6. Handles errors gracefully with detailed error reporting
    
    The function provides step-by-step console output showing:
    - File information (name, size, type)
    - Parsing progress and timing
    - Extracted data (name, email, skills count and list)
    - JSON output of parsed data
    - Warnings or explanations for partial/failed extractions
    - Log file locations
    
    Args:
        resume_path: Path to the resume file to parse (.pdf or .docx)
        output_dir: Base directory for log files (default: "outputs")
                    Creates subdirectories: outputs/csv/ and outputs/json/
    
    Raises:
        FileNotFoundError: If resume file doesn't exist
        PermissionError: If file cannot be read
        Exception: Any parsing or extraction errors are caught and logged
    
    Note:
        - Creates new ParsingLogger instance for each resume (shares CSV file)
        - Processing time is measured and displayed
        - Errors are logged but don't stop execution
    """
    framework = ResumeParserFramework()
    logger = ParsingLogger(output_dir=output_dir)
    
    filename = resume_path.name
    
    print("\n" + "=" * 70)
    print(f"PARSING RESUME: {filename}")
    print("=" * 70)
    print(f"File: {resume_path}")
    print(f"Size: {resume_path.stat().st_size:,} bytes")
    print(f"Type: {resume_path.suffix.upper()}")
    
    start_time = time.time()
    
    try:
        print("\n[Step 1] Parsing file to text...")
        result = framework.parse_resume(str(resume_path))
        parsing_time = time.time() - start_time
        
        # Log successful/partial result
        logger.log_result(filename, result=result)
        
        # Determine status
        has_name = result.name and result.name.strip()
        has_email = result.email and result.email.strip()
        has_skills = len(result.skills) > 0
        
        if has_name and has_email and has_skills:
            status = "SUCCESSFUL"
        elif has_name or has_email or has_skills:
            status = "PARTIAL SUCCESS"
        else:
            status = "FAILED (no data extracted)"
        
        print(f"  [OK] Parsed in {parsing_time:.2f} seconds")
        
        print("\n[Step 2] Extracted Data:")
        print("-" * 70)
        print(f"Status: {status}")
        print(f"\nName:  {result.name or '[Not extracted]'}")
        print(f"Email: {result.email or '[Not extracted]'}")
        print(f"Skills: {len(result.skills)} extracted")
        
        if result.skills:
            print("\nSkills List:")
            for i, skill in enumerate(result.skills[:10], 1):
                print(f"  {i}. {skill}")
            if len(result.skills) > 10:
                print(f"  ... and {len(result.skills) - 10} more")
        else:
            print("  (No skills extracted)")
        
        print("\n[Step 3] JSON Output:")
        print("-" * 70)
        json_output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        print(json_output)
        
        # Get reasons from logger
        reasons = logger._get_reasons_explanations(result, None, filename)
        if reasons != "All fields extracted successfully":
            print("\n[Step 4] Notes:")
            print("-" * 70)
            print(f"[WARNING] {reasons}")
        
        print("\n[Step 5] Logged to Files:")
        print("-" * 70)
        print(f"[OK] CSV: {logger.csv_file}")
        print(f"[OK] JSON: {logger.json_file}")
        
        total_time = time.time() - start_time
        print(f"\nTotal processing time: {total_time:.2f} seconds")
        
    except Exception as e:
        parsing_time = time.time() - start_time
        
        # Log failure
        logger.log_result(filename, error=e)
        
        print(f"\n[FAILED] Parsing failed after {parsing_time:.2f} seconds")
        print("\n[Error Details]")
        print("-" * 70)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        
        # Get reasons from logger
        reasons = logger._get_reasons_explanations(None, e, filename)
        print(f"\nExplanation: {reasons}")
        
        print("\n[Logged to Files]")
        print("-" * 70)
        print(f"[OK] CSV: {logger.csv_file}")
        print(f"[OK] JSON: {logger.json_file}")
    
    print("\n" + "=" * 70)


def main() -> None:
    """
    Main entry point for the resume parsing and logging script.
    
    Handles command-line arguments, validates input folder, discovers resume files,
    and orchestrates the parsing of all resumes in the folder. Provides interactive
    pause between resumes when running in a terminal and generates a final summary.
    
    Workflow:
        1. Parse command-line arguments or use default folder
        2. Validate input folder exists and is a directory
        3. Discover all PDF and DOCX files (including subdirectories)
        4. Sort files for consistent processing order
        5. Process each resume sequentially with parse_single_resume()
        6. Provide interactive pause between resumes (if running in terminal)
        7. Generate and display final summary statistics
    
    Command-Line Arguments:
        input_folder (optional): Path to folder containing resume files
                                 Default: "resumes/" if it exists
    
    Exit Codes:
        0: Success (all resumes processed or user interrupted)
        1: Error (invalid arguments, folder not found, no files found)
    
    Examples:
        >>> main()  # Uses default 'resumes/' folder if it exists
        >>> # Command line: python parse_and_log.py tests/test_data
    """
    # Default input folder if not specified
    DEFAULT_INPUT_FOLDER = "resumes"
    
    if len(sys.argv) < 2:
        # Use default input folder if it exists
        default_path = Path(DEFAULT_INPUT_FOLDER)
        if default_path.exists() and default_path.is_dir():
            print(f"No input folder specified. Using default: {DEFAULT_INPUT_FOLDER}")
            input_folder = default_path
        else:
            print("Usage: python parse_and_log.py [input_folder]")
            print("\nExample:")
            print(f"  python parse_and_log.py {DEFAULT_INPUT_FOLDER}")
            print("  python parse_and_log.py tests/test_data")
            print("  python parse_and_log.py ./resumes")
            print(f"\nDefault input folder: {DEFAULT_INPUT_FOLDER} (if it exists)")
            print("\nThe script will:")
            print("  1. Process resumes one at a time from the input folder")
            print("  2. Show detailed demo-style output for each resume")
            print("  3. Log results to outputs/csv/ and outputs/json/")
            sys.exit(1)
    else:
        input_folder = Path(sys.argv[1])
    
    if not input_folder.exists():
        print(f"Error: Input folder does not exist: {input_folder}")
        sys.exit(1)
    
    if not input_folder.is_dir():
        print(f"Error: Not a directory: {input_folder}")
        sys.exit(1)
    
    # Find all resume files
    resume_files = []
    resume_files.extend(input_folder.glob("*.pdf"))
    resume_files.extend(input_folder.glob("*.docx"))
    
    # Also check subdirectories (like edge_cases)
    for subdir in input_folder.rglob("*.pdf"):
        if subdir not in resume_files:
            resume_files.append(subdir)
    for subdir in input_folder.rglob("*.docx"):
        if subdir not in resume_files:
            resume_files.append(subdir)
    
    if not resume_files:
        print(f"Error: No PDF or DOCX files found in {input_folder}")
        sys.exit(1)
    
    # Sort files for consistent processing
    resume_files.sort()
    
    print(f"\nFound {len(resume_files)} resume file(s) in {input_folder}")
    print(f"Results will be logged to:")
    print(f"  - CSV: outputs/csv/parsing_log.csv (append-only, single file)")
    print(f"  - JSON: outputs/json/parsing_log_<timestamp>.json (timestamped)")
    print(f"\nStarting processing...")
    
    # Process each resume one at a time
    for i, resume_file in enumerate(resume_files, 1):
        print(f"\n\n{'='*70}")
        print(f"RESUME {i} of {len(resume_files)}")
        print(f"{'='*70}")
        
        parse_single_resume(resume_file)
        
        # Pause between resumes (only if running interactively)
        if i < len(resume_files) and sys.stdin.isatty():
            print("\nPress Enter to continue to next resume (or Ctrl+C to stop)...")
            try:
                input()
            except (KeyboardInterrupt, EOFError):
                print("\n\n[WARNING] Processing stopped")
                break
    
    # Final summary
    logger = ParsingLogger()
    summary = logger.get_summary()
    
    print("\n\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total processed: {summary['total']}")
    print(f"[OK] Successful: {summary['successful']}")
    print(f"[PARTIAL] Partial success: {summary['partial_success']}")
    print(f"[FAILED] Failed: {summary['failed']}")
    print(f"\nLog files:")
    if summary.get('csv_file'):
        print(f"  CSV: {summary['csv_file']}")
    if summary.get('json_file'):
        print(f"  JSON: {summary['json_file']}")
    print("=" * 70)


if __name__ == "__main__":
    main()

