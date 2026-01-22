"""
Configuration settings for File Organizer
"""
import os
from pathlib import Path

# === USER SETTINGS ===

# Scan mode: "single_folder" or "full_pc"
SCAN_MODE = "single_folder"  # Full PC scan enabled - scans entire computer

# Path to your Documents folder (used in single_folder mode)
DOCUMENTS_PATH = Path(r"C:\Users\Noble\OneDrive - ITEDU\Documents")

# For full PC mode - these drives will be scanned
DRIVES_TO_SCAN = ["C:\\"]  # Add more drives like ["C:\\", "D:\\", "E:\\"]

# Where organized files will go
if SCAN_MODE == "full_pc":
    ORGANIZED_PATH = Path(r"C:")  # Files go to C:\School, C:\Personal, etc.
else:
    ORGANIZED_PATH = DOCUMENTS_PATH / "_Organized"

# Where organized files will go (creates subfolder in Documents)
BACKUP_PATH = ORGANIZED_PATH.parent / "_Backup_Before_Organize"

# === ORGANIZATION RULES ===

# Define how files should be categorized by extension
FILE_CATEGORIES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt"],
    "Spreadsheets": [".xlsx", ".xls", ".csv", ".ods"],
    "Presentations": [".pptx", ".ppt", ".key"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".java", ".cpp", ".c", ".js", ".html", ".css", ".sql"],
    "Executables": [".exe", ".msi", ".bat", ".sh"],
    "Other": []  # Catch-all for unrecognized extensions
}

# Smart categorization based on folder path (checked BEFORE file extension)
# Format: "folder_name_in_path": "destination_category"
FOLDER_BASED_CATEGORIES = {
    "Basic English": "School",
    "Personal": "Personal",
    "Budgets": "Finance",
}

# === SAFETY SETTINGS ===

# Dry run mode - if True, only shows what would happen without moving files
DRY_RUN = True  # IMPORTANT: Test in dry run first before actual organization!

# Create backups before moving
CREATE_BACKUP = True

# Backup folder location
BACKUP_PATH = DOCUMENTS_PATH / "_Backup_Before_Organize"

# Skip organizing these folders (to avoid messing with important stuff)
SKIP_FOLDERS = ["_Organized", "_Backup_Before_Organize", "venv", ".git", "node_modules", "My Games"]

# === PROTECTED DIRECTORIES (Full PC Mode) ===
# CRITICAL: These directories are NEVER scanned or modified
PROTECTED_SYSTEM_DIRS = [
    # Windows System
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "ProgramData",
    "System Volume Information",
    "$Recycle.Bin",
    "Recovery",
    "Boot",
    "Windows.old",
    
    # User System
    "AppData",
    "Application Data",
    "Local Settings",
    "NetHood",
    "PrintHood",
    "Recent",
    "SendTo",
    "Start Menu",
    "Templates",
    
    # Development
    "node_modules",
    ".git",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    
    # This Project (protect the file organizer itself!)
    "FileOrganizer",
    
    # Common Game Directories
    "SteamLibrary",
    "Steam",
    "Epic Games",
    "Origin Games",
    "Battle.net",
    "GOG Games",
    "Riot Games",
    "Xbox Games",
    "WindowsApps",
    
    # Game Save Locations
    "Saved Games",
    "My Games",
    
    # Cloud Storage (don't duplicate organize)
    "OneDrive",
    "Google Drive",
    "Dropbox",
    "iCloud Drive",
    
    # Virtual Machines
    "VirtualBox VMs",
    "VMware",
    "Hyper-V",
    
    # Already organized
    "_Organized",
    "_Backup_Before_Organize",
    "_Duplicates_Review",
    "OrganizedFiles",
    
    # Top-level organized folders (if organizing to C:\)
    # These will be created by the organizer, don't scan them
    # "School",  # Commented out - we want to scan these
    # "Personal",
    # "Finance",
]

# File extensions to NEVER organize (system files)
PROTECTED_EXTENSIONS = [
    ".sys", ".dll", ".exe", ".msi", ".bat", ".cmd", ".ps1",
    ".ini", ".cfg", ".conf", ".reg", ".dat"
]

# === FULL PC MODE SAFETY ===

# Require confirmation for full PC scan
REQUIRE_ADMIN_FOR_FULL_PC = True

# Safety limit for full PC scan
MAX_FILES_FULL_PC = 10000

# Minimum file size to organize (ignore tiny system files)
MIN_FILE_SIZE_BYTES = 1024  # 1 KB minimum

# Maximum file size to organize (skip huge files)
MAX_FILE_SIZE_MB = 5000  # 5 GB maximum

# === DELETION PROTECTION ===

# NEVER allow automatic deletion - always require user approval
ALLOW_AUTO_DELETE = False

# Operations that require explicit user confirmation
REQUIRE_CONFIRMATION = [
    "delete",
    "move", 
    "overwrite",
    "batch_operations"  # Any operation affecting multiple files
]

# Maximum files to process in one batch (safety limit)
MAX_BATCH_SIZE = 100

# === LOGGING SETTINGS ===

# Where to save the log file
LOG_FILE = Path(__file__).parent / "organizer.log"

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"
