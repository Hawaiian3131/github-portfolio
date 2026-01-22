"""
Logging system for File Organizer
Tracks all operations for security and audit purposes
"""
import logging
from datetime import datetime
from pathlib import Path
from config import LOG_FILE, LOG_LEVEL

class FileOrganizerLogger:
    def __init__(self):
        """Initialize the logger with file and console output"""
        self.logger = logging.getLogger("FileOrganizer")
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # File handler - saves to log file
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        # Console handler - shows in terminal
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        
        # Add both handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log session start
        self.logger.info("="*60)
        self.logger.info(f"File Organizer Session Started: {datetime.now()}")
        self.logger.info("="*60)
    
    def info(self, message):
        """Log informational message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def log_operation(self, operation, source, destination=None, status="PLANNED"):
        """
        Log file operations with details
        
        Args:
            operation: Type of operation (SCAN, MOVE, DELETE, etc.)
            source: Source file path
            destination: Destination path (if applicable)
            status: Operation status (PLANNED, COMPLETED, FAILED, SKIPPED)
        """
        if destination:
            self.logger.info(f"[{status}] {operation}: {source} -> {destination}")
        else:
            self.logger.info(f"[{status}] {operation}: {source}")
    
    def session_summary(self, stats):
        """
        Log summary of session
        
        Args:
            stats: Dictionary with operation statistics
        """
        self.logger.info("="*60)
        self.logger.info("SESSION SUMMARY")
        self.logger.info("-"*60)
        for key, value in stats.items():
            self.logger.info(f"{key}: {value}")
        self.logger.info("="*60)

# Create a global logger instance
log = FileOrganizerLogger()