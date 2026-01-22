"""
Main File Organizer Script
Automatically organizes files in your Documents folder
"""
import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

from config import (
    DOCUMENTS_PATH,
    ORGANIZED_PATH,
    FILE_CATEGORIES,
    FOLDER_BASED_CATEGORIES,
    DRY_RUN,
    CREATE_BACKUP,
    SKIP_FOLDERS,
    ALLOW_AUTO_DELETE,
    REQUIRE_CONFIRMATION,
    MAX_BATCH_SIZE
)

# Import BACKUP_PATH if CREATE_BACKUP is enabled
if CREATE_BACKUP:
    from config import BACKUP_PATH
from logger import log


class FileOrganizer:
    def __init__(self):
        """Initialize the file organizer"""
        self.documents_path = Path(DOCUMENTS_PATH)
        self.organized_path = Path(ORGANIZED_PATH)
        self.backup_path = Path(BACKUP_PATH) if CREATE_BACKUP else None
        self.stats = {
            "Files Scanned": 0,
            "Files to Organize": 0,
            "Files Moved": 0,
            "Files Backed Up": 0,
            "Files Skipped": 0,
            "Duplicates Found": 0,
            "Errors": 0
        }
        
        log.info(f"Initializing File Organizer")
        log.info(f"Source: {self.documents_path}")
        log.info(f"Destination: {self.organized_path}")
        if CREATE_BACKUP:
            log.info(f"Backup: {self.backup_path}")
        log.info(f"Dry Run Mode: {DRY_RUN}")
    
    def get_file_category(self, file_path: Path) -> str:
        """
        Determine which category a file belongs to based on folder or extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            Category name as string
        """
        # First check if file is in a special folder
        for folder_name, category in FOLDER_BASED_CATEGORIES.items():
            if folder_name in file_path.parts:
                return category
        
        # If not in special folder, categorize by extension
        extension = file_path.suffix.lower()
        
        for category, extensions in FILE_CATEGORIES.items():
            if extension in extensions:
                return category
        
        return "Other"
    
    def get_file_hash(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of file for duplicate detection
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            log.error(f"Could not hash file {file_path}: {e}")
            return None
    
    def should_skip(self, path: Path) -> bool:
        """
        Check if a file or folder should be skipped
        
        Args:
            path: Path to check
            
        Returns:
            True if should skip, False otherwise
        """
        # Skip folders in the skip list
        for skip_folder in SKIP_FOLDERS:
            if skip_folder in path.parts:
                return True
        
        # Skip hidden files and folders
        if path.name.startswith('.'):
            return True
        
        # Skip the organized folder itself
        if self.organized_path in path.parents or path == self.organized_path:
            return True
        
        return False
    
    def scan_files(self) -> List[Tuple[Path, str]]:
        """
        Scan documents folder and categorize files
        
        Returns:
            List of tuples (file_path, category)
        """
        log.info("Starting file scan...")
        files_to_organize = []
        
        try:
            for item in self.documents_path.rglob('*'):
                # Only process files, not directories
                if not item.is_file():
                    continue
                
                self.stats["Files Scanned"] += 1
                
                # Check if should skip
                if self.should_skip(item):
                    self.stats["Files Skipped"] += 1
                    log.debug(f"Skipping: {item}")
                    continue
                
                # Get category
                category = self.get_file_category(item)
                files_to_organize.append((item, category))
                self.stats["Files to Organize"] += 1
                
                log.debug(f"Found: {item.name} -> {category}")
        
        except Exception as e:
            log.error(f"Error during scan: {e}")
            self.stats["Errors"] += 1
        
        log.info(f"Scan complete. Found {len(files_to_organize)} files to organize")
        return files_to_organize
    
    def find_duplicates(self, files_to_organize: List[Tuple[Path, str]]) -> Dict[str, List[Path]]:
        """
        Find duplicate files based on content hash
        
        Args:
            files_to_organize: List of (file_path, category) tuples
            
        Returns:
            Dictionary mapping hash to list of duplicate file paths
        """
        log.info("Checking for duplicate files...")
        hash_map = {}
        duplicates = {}
        
        for file_path, category in files_to_organize:
            file_hash = self.get_file_hash(file_path)
            if file_hash:
                if file_hash in hash_map:
                    # Found a duplicate
                    if file_hash not in duplicates:
                        duplicates[file_hash] = [hash_map[file_hash]]
                    duplicates[file_hash].append(file_path)
                    self.stats["Duplicates Found"] += 1
                else:
                    hash_map[file_hash] = file_path
        
        if duplicates:
            log.warning(f"Found {len(duplicates)} sets of duplicate files")
            for file_hash, paths in duplicates.items():
                log.warning(f"Duplicates ({len(paths)} files):")
                for path in paths:
                    log.warning(f"  - {path}")
        else:
            log.info("No duplicate files found")
        
        return duplicates
    
    def create_destination_path(self, file_path: Path, category: str) -> Path:
        """
        Create the destination path for a file
        
        Args:
            file_path: Original file path
            category: File category
            
        Returns:
            Destination path
        """
        # Create category folder
        category_folder = self.organized_path / category
        
        # Use original filename
        destination = category_folder / file_path.name
        
        # Handle duplicate filenames
        if destination.exists():
            # Add timestamp to make unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = file_path.stem
            suffix = file_path.suffix
            destination = category_folder / f"{stem}_{timestamp}{suffix}"
        
        return destination
    
    def preview_operations(self, files_to_organize: List[Tuple[Path, str]]):
        """
        Show user what will happen without doing it
        
        Args:
            files_to_organize: List of (file_path, category) tuples
        """
        log.info("\n" + "="*60)
        log.info("PREVIEW: The following operations will be performed")
        log.info("="*60)
        
        # Group by category for cleaner display
        by_category = {}
        for file_path, category in files_to_organize:
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(file_path)
        
        for category, files in by_category.items():
            log.info(f"\n{category} ({len(files)} files):")
            for file_path in files[:5]:  # Show first 5 of each category
                log.info(f"  - {file_path.name}")
            if len(files) > 5:
                log.info(f"  ... and {len(files) - 5} more")
        
        log.info("\n" + "="*60)
    
    def get_user_confirmation(self, file_count: int) -> bool:
        """
        Ask user to confirm operation
        
        Args:
            file_count: Number of files to be processed
            
        Returns:
            True if user confirms, False otherwise
        """
        if file_count > MAX_BATCH_SIZE:
            log.warning(f"Batch size ({file_count}) exceeds maximum ({MAX_BATCH_SIZE})")
            log.warning("Consider organizing in smaller batches for safety")
            return False
        
        print(f"\nReady to organize {file_count} files.")
        response = input("Proceed? Type 'yes' to continue: ").strip().lower()
        
        if response == 'yes':
            log.info("User confirmed operation")
            return True
        else:
            log.info("User cancelled operation")
            return False
    
    def organize_files(self, files_to_organize: List[Tuple[Path, str]]):
        """
        Move files to their organized locations
        
        Args:
            files_to_organize: List of (file_path, category) tuples
        """
        log.info("Starting file organization...")
        
        for file_path, category in files_to_organize:
            try:
                # Create destination path
                destination = self.create_destination_path(file_path, category)
                
                # Create category folder if it doesn't exist
                destination.parent.mkdir(parents=True, exist_ok=True)
                
                # Create backup if enabled
                if CREATE_BACKUP and not DRY_RUN:
                    # Create backup path maintaining folder structure
                    relative_path = file_path.relative_to(self.documents_path)
                    backup_destination = self.backup_path / relative_path
                    backup_destination.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy to backup
                    shutil.copy2(str(file_path), str(backup_destination))
                    log.log_operation("BACKUP", file_path, backup_destination, "COMPLETED")
                    self.stats["Files Backed Up"] += 1
                
                # Log the planned operation
                log.log_operation("MOVE", file_path, destination, "PLANNED")
                
                if not DRY_RUN:
                    # Actually move the file
                    shutil.move(str(file_path), str(destination))
                    log.log_operation("MOVE", file_path, destination, "COMPLETED")
                    self.stats["Files Moved"] += 1
                else:
                    log.log_operation("MOVE", file_path, destination, "DRY_RUN")
                
            except Exception as e:
                log.error(f"Failed to move {file_path}: {e}")
                log.log_operation("MOVE", file_path, destination, "FAILED")
                self.stats["Errors"] += 1
        
        if DRY_RUN:
            log.warning("DRY RUN MODE - No files were actually moved")
            log.info("Set DRY_RUN = False in config.py to perform actual organization")
        elif CREATE_BACKUP:
            log.info(f"Backup created at: {self.backup_path}")
            log.info("You can safely delete the backup folder once you verify everything worked correctly")
    
    def run(self):
        """Main execution method"""
        try:
            # Step 1: Scan files
            files_to_organize = self.scan_files()
            
            if not files_to_organize:
                log.info("No files found to organize!")
                return
            
            # Step 2: Check for duplicates
            duplicates = self.find_duplicates(files_to_organize)
            
            # Step 3: Preview what will happen
            self.preview_operations(files_to_organize)
            
            # Step 4: Get user confirmation (if not in dry run)
            if not DRY_RUN:
                if not self.get_user_confirmation(len(files_to_organize)):
                    log.info("Operation cancelled by user")
                    return
            
            # Step 5: Organize files
            self.organize_files(files_to_organize)
            
            # Step 6: Show summary
            log.session_summary(self.stats)
            
            log.info("File organization complete!")
            
        except Exception as e:
            log.error(f"Critical error: {e}")
            self.stats["Errors"] += 1


def main():
    """Entry point for the script"""
    organizer = FileOrganizer()
    organizer.run()


if __name__ == "__main__":
    main()