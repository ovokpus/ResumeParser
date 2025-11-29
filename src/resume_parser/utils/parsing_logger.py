"""Utility for logging resume parsing results to CSV and JSON.

CSV: Single append-only file with date and timestamp columns.
JSON: Timestamped files for single or group processing.
"""

import csv
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from resume_parser.models import ResumeData
from resume_parser.exceptions import (
    FileParsingError,
    ExtractionError,
    ValidationError,
    APIError
)


class ParsingStatus(Enum):
    """
    Enumeration of possible parsing status values.
    
    Attributes:
        SUCCESSFUL: All fields (name, email, skills) were successfully extracted
        PARTIAL_SUCCESS: At least one field was extracted, but not all fields
        FAILED: Parsing failed completely or no data was extracted
    
    Usage:
        >>> status = ParsingStatus.SUCCESSFUL
        >>> print(status.value)  # "successful"
    """
    SUCCESSFUL = "successful"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"


class ParsingLogger:
    """
    Logger for resume parsing results with CSV and JSON output formats.
    
    This class provides comprehensive logging of resume parsing operations,
    maintaining both human-readable CSV logs and structured JSON logs. The CSV
    file is append-only and accumulates all parsing results over time, while JSON
    files are timestamped and can represent single or batch processing sessions.
    
    Features:
        - CSV logging: Single append-only file with date and timestamp columns
        - JSON logging: Timestamped files for individual or batch processing
        - Status determination: Automatically categorizes results (successful/partial/failed)
        - Error tracking: Captures error types and messages for failed parsing
        - Summary statistics: Provides counts of successful, partial, and failed parses
    
    CSV File Structure:
        - File: outputs/csv/parsing_log.csv
        - Columns: date, timestamp, filename, status, json_output, reasons_explanations,
                   name_extracted, email_extracted, skills_count, error_type, error_message
        - Format: Append-only, new entries added to end of file
    
    JSON File Structure:
        - File: outputs/json/parsing_log_<timestamp>.json
        - Format: Array of log entry objects
        - Each entry contains: date, timestamp, filename, status, parsed_data,
                               reasons_explanations, and error information
    
    Example:
        >>> logger = ParsingLogger()
        >>> result = framework.parse_resume("resume.pdf")
        >>> logger.log_result("resume.pdf", result=result)
        >>> summary = logger.get_summary()
        >>> print(f"Total processed: {summary['total']}")
    
    Attributes:
        output_dir (Path): Base directory for log files
        csv_dir (Path): Directory for CSV log files
        json_dir (Path): Directory for JSON log files
        csv_file (Path): Path to the CSV log file (single file)
        json_file (Path): Path to the current JSON log file (timestamped)
    """
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize the parsing logger with output directories and log files.
        
        Creates the necessary directory structure and initializes log files:
        - Creates outputs/csv/ and outputs/json/ subdirectories if they don't exist
        - Initializes CSV file with headers (if file doesn't exist)
        - Creates timestamped JSON file with empty array
        
        Args:
            output_dir: Base directory to store log files (default: "outputs")
                        Creates subdirectories: {output_dir}/csv/ and {output_dir}/json/
        
        Note:
            - CSV file is shared across all ParsingLogger instances (append-only)
            - JSON file is unique per instance (timestamped)
            - JSON file is created lazily (only when first result is logged)
            - Directories are created if they don't exist (with parents=True)
        """
        self.output_dir = Path(output_dir)
        self.csv_dir = self.output_dir / "csv"
        self.json_dir = self.output_dir / "json"
        
        # Create subdirectories
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        self.json_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV: Single append-only file
        self.csv_file = self.csv_dir / "parsing_log.csv"
        
        # JSON: Timestamped files (can be for single or group processing)
        # Lazy initialization: only create JSON file when first result is logged
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.json_file = self.json_dir / f"parsing_log_{timestamp}.json"
        self._json_initialized = False
        
        # Initialize CSV file (always needed)
        self._initialize_csv()
    
    def _initialize_csv(self) -> None:
        """
        Initialize CSV log file with column headers.
        
        Creates the CSV file with headers if it doesn't exist. If the file
        already exists, this method does nothing (preserving existing data).
        
        CSV Columns:
            - date: Date in YYYY-MM-DD format
            - timestamp: Full ISO timestamp
            - filename: Name of the resume file
            - status: Parsing status (successful/partial_success/failed)
            - json_output: Full parsed data as JSON string
            - reasons_explanations: Human-readable explanation of result
            - name_extracted: Extracted name (or empty string)
            - email_extracted: Extracted email (or empty string)
            - skills_count: Number of skills extracted
            - error_type: Type of error if parsing failed
            - error_message: Error message if parsing failed
        
        Note:
            File is created with UTF-8 encoding and newline='' for proper CSV handling.
        """
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'date',
                    'timestamp',
                    'filename',
                    'status',
                    'json_output',
                    'reasons_explanations',
                    'name_extracted',
                    'email_extracted',
                    'skills_count',
                    'error_type',
                    'error_message'
                ])
    
    def _initialize_json(self) -> None:
        """
        Initialize JSON log file with empty array structure.
        
        Creates a new JSON file with an empty array. This method is called
        lazily when the first result is logged, preventing empty JSON files
        from being created if a ParsingLogger instance is created but never used.
        
        JSON Structure:
            [
                {
                    "date": "YYYY-MM-DD",
                    "timestamp": "ISO timestamp",
                    "filename": "resume.pdf",
                    "status": "successful|partial_success|failed",
                    "parsed_data": {...},
                    ...
                },
                ...
            ]
        
        Note:
            - File is created with UTF-8 encoding and pretty-printed (indent=2)
            - Only called when first log_result() is invoked
            - Prevents empty JSON files from being created unnecessarily
        """
        if not self.json_file.exists():
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
    
    def _determine_status(self, result: Optional[ResumeData], error: Optional[Exception] = None) -> ParsingStatus:
        """
        Determine the parsing status based on result and any errors.
        
        Status determination logic:
            - FAILED: If an error occurred or result is None
            - FAILED: If result exists but no fields were extracted
            - PARTIAL_SUCCESS: If at least one field (name, email, or skills) was extracted
            - SUCCESSFUL: If all three fields (name, email, and skills) were extracted
        
        Args:
            result: Parsed ResumeData object (None if parsing failed)
            error: Exception if parsing failed (None if successful)
        
        Returns:
            ParsingStatus: Enum value indicating the parsing status
            
        Example:
            >>> logger = ParsingLogger()
            >>> result = ResumeData(name="John", email="john@example.com", skills=[])
            >>> status = logger._determine_status(result)
            >>> print(status)  # ParsingStatus.PARTIAL_SUCCESS
        """
        if error:
            return ParsingStatus.FAILED
        
        if not result:
            return ParsingStatus.FAILED
        
        # Check if we got any meaningful data
        has_name = result.name and result.name.strip()
        has_email = result.email and result.email.strip()
        has_skills = len(result.skills) > 0
        
        # If we have at least one field, it's partial success
        if has_name or has_email or has_skills:
            # If we have all fields, it's successful
            if has_name and has_email and has_skills:
                return ParsingStatus.SUCCESSFUL
            else:
                return ParsingStatus.PARTIAL_SUCCESS
        
        return ParsingStatus.FAILED
    
    def _get_reasons_explanations(
        self,
        result: Optional[ResumeData],
        error: Optional[Exception] = None,
        filename: str = ""
    ) -> str:
        """
        Generate human-readable explanations for parsing results or failures.
        
        Analyzes the parsing result and error (if any) to provide clear explanations
        about what happened during parsing. Handles various scenarios including:
        - Successful parsing with all fields extracted
        - Partial success with missing fields
        - Edge cases (encrypted files, corrupted files, minimal content)
        - Different error types (parsing errors, extraction errors, API errors)
        
        Args:
            result: Parsed ResumeData object (None if parsing failed)
            error: Exception if parsing failed (None if successful)
            filename: Name/path of the resume file being parsed (used for edge case detection)
        
        Returns:
            str: Human-readable explanation string. Multiple reasons are joined with "; "
                 Returns "All fields extracted successfully" if everything worked.
        
        Examples:
            >>> logger._get_reasons_explanations(result, None, "resume.pdf")
            "All fields extracted successfully"
            
            >>> logger._get_reasons_explanations(result, None, "resume.pdf")
            "Skills extraction: Failed or empty"
            
            >>> logger._get_reasons_explanations(None, FileParsingError(...), "encrypted.pdf")
            "Edge case: Encrypted PDF (requires password)"
        """
        reasons = []
        
        if error:
            # Determine error type and reason
            if isinstance(error, FileParsingError):
                error_msg = str(error).lower()
                file_ext = Path(filename).suffix.lower() if filename else ""
                
                if "encrypted" in error_msg or "password" in error_msg:
                    reasons.append(f"Edge case: Encrypted {file_ext.upper() or 'file'} (requires password)")
                elif "corrupted" in error_msg or "no text content" in error_msg:
                    file_type = "PDF" if file_ext == ".pdf" else "DOCX" if file_ext == ".docx" else "file"
                    reasons.append(f"Edge case: Corrupted or image-based {file_type}")
                elif "not found" in error_msg:
                    reasons.append("File not found")
                else:
                    reasons.append(f"File parsing error: {str(error)}")
            elif isinstance(error, ExtractionError):
                reasons.append(f"Extraction error: {str(error)}")
            elif isinstance(error, APIError):
                reasons.append(f"API error: OpenAI API call failed")
            elif isinstance(error, ValidationError):
                reasons.append(f"Validation error: {str(error)}")
            else:
                reasons.append(f"Unexpected error: {type(error).__name__}: {str(error)}")
        else:
            # Check what was extracted
            if result:
                if not result.name or not result.name.strip():
                    reasons.append("Name extraction: Failed or empty")
                if not result.email or not result.email.strip():
                    reasons.append("Email extraction: Failed or empty")
                if len(result.skills) == 0:
                    reasons.append("Skills extraction: Failed or empty")
                
                # Check for edge cases
                if filename and "edge_cases" in filename:
                    if "minimal" in filename.lower():
                        reasons.append("Edge case: Minimal content resume")
                    elif "encrypted" in filename.lower():
                        reasons.append("Edge case: Encrypted PDF")
                    elif "corrupted" in filename.lower():
                        reasons.append("Edge case: Corrupted PDF")
        
        if not reasons:
            return "All fields extracted successfully"
        
        return "; ".join(reasons)
    
    def log_result(
        self,
        filename: str,
        result: Optional[ResumeData] = None,
        error: Optional[Exception] = None
    ) -> None:
        """
        Log a resume parsing result to both CSV and JSON files.
        
        This is the main logging method that records parsing results. It:
        1. Determines the parsing status (successful/partial_success/failed)
        2. Extracts relevant data from the result or error
        3. Generates human-readable explanations
        4. Writes to CSV file (append mode)
        5. Writes to JSON file (appends to array)
        
        Both files receive the same information, formatted appropriately for each format.
        The CSV file is append-only and accumulates all results, while the JSON file
        is specific to this logger instance (timestamped).
        
        Args:
            filename: Name or path of the resume file that was parsed
            result: Parsed ResumeData object (None if parsing failed)
            error: Exception if parsing failed (None if successful)
        
        Note:
            - At least one of result or error should be provided
            - If both are None, status will be FAILED
            - CSV entries are appended to the shared parsing_log.csv file
            - JSON entries are appended to the instance-specific JSON file
        
        Example:
            >>> logger = ParsingLogger()
            >>> result = framework.parse_resume("resume.pdf")
            >>> logger.log_result("resume.pdf", result=result)
            
            >>> # Or for failures:
            >>> try:
            ...     result = framework.parse_resume("bad.pdf")
            ... except Exception as e:
            ...     logger.log_result("bad.pdf", error=e)
        """
        # Get current datetime
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        timestamp_str = now.isoformat()
        
        status = self._determine_status(result, error)
        
        # Prepare data
        if result:
            parsed_data = result.to_dict()
            json_output = json.dumps(parsed_data, ensure_ascii=False)
            name_extracted = result.name or ""
            email_extracted = result.email or ""
            skills_count = len(result.skills)
        else:
            parsed_data = {}
            json_output = "{}"
            name_extracted = ""
            email_extracted = ""
            skills_count = 0
        
        # Get reasons/explanations
        reasons = self._get_reasons_explanations(result, error, filename)
        
        # Extract error information
        error_type = type(error).__name__ if error else ""
        error_message = str(error) if error else ""
        
        # Write to CSV (append-only)
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                date_str,
                timestamp_str,
                filename,
                status.value,
                json_output,
                reasons,
                name_extracted,
                email_extracted,
                skills_count,
                error_type,
                error_message
            ])
        
        # Write to JSON (append to array) - lazy initialization
        if not self._json_initialized:
            self._initialize_json()
            self._json_initialized = True
        
        log_entry = {
            "date": date_str,
            "timestamp": timestamp_str,
            "filename": filename,
            "status": status.value,
            "parsed_data": parsed_data,
            "reasons_explanations": reasons,
            "name_extracted": name_extracted,
            "email_extracted": email_extracted,
            "skills_count": skills_count,
            "error_type": error_type,
            "error_message": error_message
        }
        
        # Read existing JSON, append new entry, write back
        with open(self.json_file, 'r', encoding='utf-8') as f:
            log_entries = json.load(f)
        
        log_entries.append(log_entry)
        
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(log_entries, f, indent=2, ensure_ascii=False)
    
    def get_csv_log_file(self) -> Path:
        """
        Get the path to the CSV log file.
        
        Returns:
            Path: Path to the single append-only CSV log file (parsing_log.csv)
        
        Note:
            This is a shared file across all ParsingLogger instances, so all
            parsing results accumulate in the same CSV file.
        """
        return self.csv_file
    
    def get_latest_json_file(self) -> Optional[Path]:
        """
        Get the path to the most recently created JSON log file.
        
        Searches the JSON output directory for all parsing log JSON files
        and returns the one with the most recent modification time.
        
        Returns:
            Optional[Path]: Path to the most recent JSON log file, or None if
                           no JSON files exist in the output directory
        
        Note:
            This searches all JSON files in the directory, not just the one
            created by this instance. Useful for finding the latest log file
            across multiple processing sessions.
        """
        log_files = list(self.json_dir.glob("parsing_log_*.json"))
        if log_files:
            return max(log_files, key=lambda p: p.stat().st_mtime)
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics from the CSV log file.
        
        Reads the CSV log file and counts entries by status (successful,
        partial_success, failed) to provide an overview of parsing results.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - total (int): Total number of entries processed
                - successful (int): Number of successful parses
                - partial_success (int): Number of partial success parses
                - failed (int): Number of failed parses
                - csv_file (str): Path to the CSV log file
                - json_file (Optional[str]): Path to the latest JSON file (if exists)
        
        Note:
            - Returns zeros if CSV file doesn't exist
            - Reads the entire CSV file to count entries
            - JSON file path is the most recent one found (may be from different session)
        
        Example:
            >>> logger = ParsingLogger()
            >>> summary = logger.get_summary()
            >>> print(f"Success rate: {summary['successful'] / summary['total'] * 100:.1f}%")
        """
        csv_log = self.get_csv_log_file()
        if not csv_log.exists():
            return {
                "total": 0,
                "successful": 0,
                "partial_success": 0,
                "failed": 0,
                "csv_file": str(csv_log),
                "json_file": None
            }
        
        successful = 0
        partial_success = 0
        failed = 0
        
        with open(csv_log, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = row.get('status', '')
                if status == ParsingStatus.SUCCESSFUL.value:
                    successful += 1
                elif status == ParsingStatus.PARTIAL_SUCCESS.value:
                    partial_success += 1
                elif status == ParsingStatus.FAILED.value:
                    failed += 1
        
        total = successful + partial_success + failed
        
        latest_json = self.get_latest_json_file()
        
        return {
            "total": total,
            "successful": successful,
            "partial_success": partial_success,
            "failed": failed,
            "csv_file": str(csv_log),
            "json_file": str(latest_json) if latest_json else None
        }

