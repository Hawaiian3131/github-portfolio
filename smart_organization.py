"""
Smart Organization Options
Advanced organization strategies including date-based, size-based, and custom patterns
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class SmartOrganizer:
    def __init__(self):
        self.organization_strategies = {}
    
    def organize_by_date(self, file_path: Path, format: str = "year/month") -> str:
        """
        Organize files by date into year/month folders
        
        Args:
            file_path: Path to file
            format: Organization format
                - "year/month" → 2026/01/
                - "year" → 2026/
                - "year-month" → 2026-01/
                - "month/year" → 01/2026/
                
        Returns:
            Folder path structure
        """
        try:
            # Use modification time
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            if format == "year/month":
                return f"{mod_time.year}/{mod_time.month:02d}"
            elif format == "year":
                return f"{mod_time.year}"
            elif format == "year-month":
                return f"{mod_time.year}-{mod_time.month:02d}"
            elif format == "month/year":
                return f"{mod_time.month:02d}/{mod_time.year}"
            else:
                return f"{mod_time.year}/{mod_time.month:02d}"
        except:
            return "Unknown_Date"
    
    def organize_by_size(self, file_path: Path, thresholds: Dict[str, float] = None) -> str:
        """
        Organize files by size
        
        Args:
            file_path: Path to file
            thresholds: Size thresholds in MB
                Default: {"Small": 1, "Medium": 50, "Large": float('inf')}
                
        Returns:
            Size category
        """
        if thresholds is None:
            thresholds = {
                "Small": 1,      # < 1 MB
                "Medium": 50,    # 1-50 MB
                "Large": 500,    # 50-500 MB
                "Huge": float('inf')  # > 500 MB
            }
        
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            
            for category, max_size in sorted(thresholds.items(), key=lambda x: x[1]):
                if size_mb < max_size:
                    return category
            
            return list(thresholds.keys())[-1]
        except:
            return "Unknown_Size"
    
    def organize_by_type_and_date(self, file_path: Path, base_category: str) -> str:
        """
        Combine type and date organization
        Example: Photos/2026/01/, Documents/2025/12/
        
        Args:
            file_path: Path to file
            base_category: Base category (e.g., "Photos", "Documents")
            
        Returns:
            Combined path
        """
        date_path = self.organize_by_date(file_path, "year/month")
        return f"{base_category}/{date_path}"
    
    def organize_by_type_and_size(self, file_path: Path, base_category: str) -> str:
        """
        Combine type and size organization
        Example: Photos/Large/, Documents/Small/
        
        Args:
            file_path: Path to file
            base_category: Base category
            
        Returns:
            Combined path
        """
        size_category = self.organize_by_size(file_path)
        return f"{base_category}/{size_category}"
    
    def auto_archive_old_files(self, file_path: Path, age_days: int = 90) -> str:
        """
        Archive files older than specified days
        
        Args:
            file_path: Path to file
            age_days: Age threshold in days
            
        Returns:
            "Archive" if old, None if not
        """
        try:
            file_age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
            
            if file_age_days > age_days:
                # Further organize archives by year
                year = datetime.fromtimestamp(file_path.stat().st_mtime).year
                return f"Archive/{year}"
            return None
        except:
            return None
    
    def organize_by_project(self, file_path: Path, project_patterns: Dict[str, List[str]]) -> Optional[str]:
        """
        Organize by project based on filename patterns
        
        Args:
            file_path: Path to file
            project_patterns: Dict mapping project names to keyword lists
                Example: {"ProjectA": ["proj-a", "clientA"], "ProjectB": ["proj-b"]}
                
        Returns:
            Project name if matched, None otherwise
        """
        filename_lower = file_path.name.lower()
        
        for project, keywords in project_patterns.items():
            for keyword in keywords:
                if keyword.lower() in filename_lower:
                    return f"Projects/{project}"
        
        return None
    
    def organize_by_client(self, file_path: Path, client_list: List[str]) -> Optional[str]:
        """
        Organize by client name
        
        Args:
            file_path: Path to file
            client_list: List of client names
            
        Returns:
            Client folder if matched, None otherwise
        """
        filename_lower = file_path.name.lower()
        
        for client in client_list:
            if client.lower() in filename_lower:
                return f"Clients/{client}"
        
        return None
    
    def custom_folder_pattern(self, file_path: Path, pattern: str) -> str:
        """
        Create custom folder names using patterns
        
        Supported variables:
            {year} - File year
            {month} - File month
            {day} - File day
            {size} - File size category
            {ext} - File extension
            {name} - First word of filename
            
        Args:
            file_path: Path to file
            pattern: Pattern string (e.g., "{year}/{month}/{size}")
            
        Returns:
            Formatted folder path
        """
        try:
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            size_category = self.organize_by_size(file_path)
            
            # Get first word of filename (before first space or underscore)
            import re
            name_parts = re.split(r'[\s_-]', file_path.stem)
            first_word = name_parts[0] if name_parts else "Unknown"
            
            replacements = {
                '{year}': str(mod_time.year),
                '{month}': f"{mod_time.month:02d}",
                '{day}': f"{mod_time.day:02d}",
                '{size}': size_category,
                '{ext}': file_path.suffix.lstrip('.').upper(),
                '{name}': first_word
            }
            
            result = pattern
            for key, value in replacements.items():
                result = result.replace(key, value)
            
            return result
        except:
            return "Custom"
    
    def multi_level_organization(self, file_path: Path, rules: List[Tuple[str, callable]]) -> str:
        """
        Apply multi-level categorization
        
        Args:
            file_path: Path to file
            rules: List of (description, function) tuples
                Each function should return a folder name or None
                
        Returns:
            Multi-level path (e.g., "Work/Projects/2026")
        """
        path_parts = []
        
        for description, rule_func in rules:
            result = rule_func(file_path)
            if result:
                path_parts.append(result)
        
        return "/".join(path_parts) if path_parts else "Other"


# Preset organization strategies
ORGANIZATION_PRESETS = {
    "by_date_year_month": {
        "description": "Organize by Year/Month folders",
        "strategy": "date",
        "format": "year/month"
    },
    "by_date_and_type": {
        "description": "Organize by Type/Year/Month",
        "strategy": "type_date"
    },
    "by_size": {
        "description": "Organize by file size (Small/Medium/Large)",
        "strategy": "size"
    },
    "archive_old": {
        "description": "Archive files older than 90 days",
        "strategy": "archive",
        "age_days": 90
    },
    "by_project": {
        "description": "Organize by project based on filename",
        "strategy": "project"
    }
}


# Example usage configurations
EXAMPLE_CONFIGS = {
    "photo_library": {
        "strategy": "multi_level",
        "rules": [
            ("base", lambda fp: "Photos"),
            ("year", lambda fp: SmartOrganizer().organize_by_date(fp, "year")),
            ("month", lambda fp: SmartOrganizer().organize_by_date(fp, "month"))
        ],
        "description": "Photos organized as Photos/2026/01/"
    },
    "work_files": {
        "strategy": "multi_level",
        "rules": [
            ("base", lambda fp: "Work"),
            ("project", lambda fp: SmartOrganizer().organize_by_project(fp, {"ProjectA": ["proj-a"], "ProjectB": ["proj-b"]})),
            ("date", lambda fp: SmartOrganizer().organize_by_date(fp, "year-month"))
        ],
        "description": "Work files as Work/ProjectA/2026-01/"
    },
    "media_by_size_and_date": {
        "strategy": "multi_level",
        "rules": [
            ("type", lambda fp: "Media"),
            ("size", lambda fp: SmartOrganizer().organize_by_size(fp)),
            ("date", lambda fp: SmartOrganizer().organize_by_date(fp, "year"))
        ],
        "description": "Media files as Media/Large/2026/"
    }
}
