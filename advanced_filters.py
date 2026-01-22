"""
Advanced Filters and Rules Engine
Filter files by age, size, patterns, and custom rules
"""
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable


class FileFilter:
    def __init__(self):
        self.filters = []
    
    def add_age_filter(self, min_days: Optional[int] = None, max_days: Optional[int] = None):
        """
        Filter files by age
        
        Args:
            min_days: Minimum age in days (files older than this)
            max_days: Maximum age in days (files newer than this)
        """
        def age_filter(file_path: Path) -> bool:
            try:
                file_age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
                
                if min_days is not None and file_age_days < min_days:
                    return False
                if max_days is not None and file_age_days > max_days:
                    return False
                return True
            except:
                return True  # Include if can't determine age
        
        self.filters.append(age_filter)
        return self
    
    def add_size_filter(self, min_mb: Optional[float] = None, max_mb: Optional[float] = None):
        """
        Filter files by size
        
        Args:
            min_mb: Minimum size in MB
            max_mb: Maximum size in MB
        """
        def size_filter(file_path: Path) -> bool:
            try:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                
                if min_mb is not None and size_mb < min_mb:
                    return False
                if max_mb is not None and size_mb > max_mb:
                    return False
                return True
            except:
                return True
        
        self.filters.append(size_filter)
        return self
    
    def add_regex_filter(self, pattern: str, match: bool = True):
        """
        Filter files by regex pattern
        
        Args:
            pattern: Regex pattern to match
            match: If True, include matching files. If False, exclude matching files.
        """
        def regex_filter(file_path: Path) -> bool:
            try:
                matches = bool(re.search(pattern, file_path.name, re.IGNORECASE))
                return matches if match else not matches
            except:
                return True
        
        self.filters.append(regex_filter)
        return self
    
    def add_extension_filter(self, extensions: List[str], include: bool = True):
        """
        Filter files by extension
        
        Args:
            extensions: List of extensions (e.g., ['.jpg', '.png'])
            include: If True, include only these. If False, exclude these.
        """
        # Normalize extensions
        extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
        
        def extension_filter(file_path: Path) -> bool:
            file_ext = file_path.suffix.lower()
            has_extension = file_ext in extensions
            return has_extension if include else not has_extension
        
        self.filters.append(extension_filter)
        return self
    
    def add_custom_filter(self, filter_func: Callable[[Path], bool]):
        """
        Add a custom filter function
        
        Args:
            filter_func: Function that takes Path and returns bool
        """
        self.filters.append(filter_func)
        return self
    
    def apply(self, file_path: Path) -> bool:
        """
        Apply all filters to a file
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file passes all filters, False otherwise
        """
        for filter_func in self.filters:
            if not filter_func(file_path):
                return False
        return True
    
    def filter_files(self, file_paths: List[Path]) -> List[Path]:
        """
        Filter a list of files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Filtered list of file paths
        """
        return [fp for fp in file_paths if self.apply(fp)]
    
    def clear_filters(self):
        """Clear all filters"""
        self.filters = []
        return self


class RuleEngine:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, condition: Callable[[Path], bool], action: str, priority: int = 0):
        """
        Add a rule
        
        Args:
            condition: Function that returns True if rule applies
            action: Category/destination for matching files
            priority: Higher priority rules are checked first
        """
        self.rules.append({
            'condition': condition,
            'action': action,
            'priority': priority
        })
        # Sort by priority
        self.rules.sort(key=lambda x: x['priority'], reverse=True)
    
    def add_filename_contains_rule(self, keyword: str, category: str, priority: int = 0):
        """
        Rule: If filename contains keyword, categorize as category
        
        Args:
            keyword: Keyword to search for
            category: Destination category
            priority: Rule priority
        """
        def condition(file_path: Path) -> bool:
            return keyword.lower() in file_path.name.lower()
        
        self.add_rule(condition, category, priority)
    
    def add_extension_rule(self, extensions: List[str], category: str, priority: int = 0):
        """
        Rule: If file has extension, categorize as category
        
        Args:
            extensions: List of extensions
            category: Destination category
            priority: Rule priority
        """
        extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
        
        def condition(file_path: Path) -> bool:
            return file_path.suffix.lower() in extensions
        
        self.add_rule(condition, category, priority)
    
    def add_size_rule(self, min_mb: float, max_mb: float, category: str, priority: int = 0):
        """
        Rule: If file size is between min and max, categorize as category
        
        Args:
            min_mb: Minimum size in MB
            max_mb: Maximum size in MB
            category: Destination category
            priority: Rule priority
        """
        def condition(file_path: Path) -> bool:
            try:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                return min_mb <= size_mb <= max_mb
            except:
                return False
        
        self.add_rule(condition, category, priority)
    
    def add_age_rule(self, min_days: int, max_days: int, category: str, priority: int = 0):
        """
        Rule: If file age is between min and max days, categorize as category
        
        Args:
            min_days: Minimum age in days
            max_days: Maximum age in days
            category: Destination category
            priority: Rule priority
        """
        def condition(file_path: Path) -> bool:
            try:
                file_age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
                return min_days <= file_age_days <= max_days
            except:
                return False
        
        self.add_rule(condition, category, priority)
    
    def add_regex_rule(self, pattern: str, category: str, priority: int = 0):
        """
        Rule: If filename matches regex pattern, categorize as category
        
        Args:
            pattern: Regex pattern
            category: Destination category
            priority: Rule priority
        """
        def condition(file_path: Path) -> bool:
            try:
                return bool(re.search(pattern, file_path.name, re.IGNORECASE))
            except:
                return False
        
        self.add_rule(condition, category, priority)
    
    def apply_rules(self, file_path: Path) -> Optional[str]:
        """
        Apply rules to file and return category
        
        Args:
            file_path: Path to file
            
        Returns:
            Category name if rule matched, None otherwise
        """
        for rule in self.rules:
            if rule['condition'](file_path):
                return rule['action']
        return None
    
    def clear_rules(self):
        """Clear all rules"""
        self.rules = []


# Preset filter configurations
PRESET_FILTERS = {
    "recent_files": {
        "description": "Files modified in last 30 days",
        "filters": {"max_days": 30}
    },
    "old_files": {
        "description": "Files older than 90 days",
        "filters": {"min_days": 90}
    },
    "large_files": {
        "description": "Files larger than 100 MB",
        "filters": {"min_mb": 100}
    },
    "small_files": {
        "description": "Files smaller than 1 MB",
        "filters": {"max_mb": 1}
    },
    "images_only": {
        "description": "Image files only",
        "filters": {"extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp"]}
    },
    "documents_only": {
        "description": "Document files only",
        "filters": {"extensions": [".pdf", ".docx", ".doc", ".txt", ".xlsx"]}
    }
}


# Preset rule configurations
PRESET_RULES = {
    "work_projects": [
        {"keyword": "project", "category": "Work/Projects", "priority": 10},
        {"keyword": "client", "category": "Work/Clients", "priority": 10},
        {"keyword": "invoice", "category": "Work/Finance", "priority": 10}
    ],
    "personal_docs": [
        {"keyword": "resume", "category": "Personal/Career", "priority": 10},
        {"keyword": "cv", "category": "Personal/Career", "priority": 10},
        {"keyword": "bank", "category": "Personal/Finance", "priority": 10},
        {"keyword": "tax", "category": "Personal/Finance", "priority": 10}
    ],
    "media_organization": [
        {"extensions": [".jpg", ".png"], "category": "Media/Photos", "priority": 5},
        {"extensions": [".mp4", ".avi"], "category": "Media/Videos", "priority": 5},
        {"extensions": [".mp3", ".wav"], "category": "Media/Music", "priority": 5}
    ]
}
