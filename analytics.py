"""
File Analytics Module
Track statistics and generate insights about file organization
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class FileAnalytics:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.history_file = self.script_dir / "organization_history.json"
        self.history = self.load_history()
    
    def load_history(self):
        """Load organization history from file"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {"sessions": []}
    
    def save_history(self):
        """Save organization history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)
    
    def record_session(self, stats, files_organized):
        """
        Record an organization session
        
        Args:
            stats: Dictionary with session statistics
            files_organized: List of (file_path, category, size) tuples
        """
        session = {
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "categories": self.analyze_categories(files_organized),
            "total_size_mb": sum(size for _, _, size in files_organized) / (1024 * 1024),
            "file_count": len(files_organized)
        }
        
        self.history["sessions"].append(session)
        self.save_history()
    
    def analyze_categories(self, files_organized):
        """Analyze file distribution by category"""
        categories = defaultdict(lambda: {"count": 0, "size_mb": 0})
        
        for file_path, category, size in files_organized:
            categories[category]["count"] += 1
            categories[category]["size_mb"] += size / (1024 * 1024)
        
        return dict(categories)
    
    def get_total_stats(self):
        """Get all-time statistics"""
        total_files = 0
        total_size_mb = 0
        total_duplicates = 0
        category_breakdown = defaultdict(int)
        
        for session in self.history["sessions"]:
            total_files += session["stats"].get("Files Moved", 0)
            total_size_mb += session.get("total_size_mb", 0)
            total_duplicates += session["stats"].get("Duplicates Found", 0)
            
            for category, data in session.get("categories", {}).items():
                category_breakdown[category] += data["count"]
        
        return {
            "total_files_organized": total_files,
            "total_size_mb": round(total_size_mb, 2),
            "total_duplicates_found": total_duplicates,
            "total_sessions": len(self.history["sessions"]),
            "category_breakdown": dict(category_breakdown)
        }
    
    def get_recent_sessions(self, count=5):
        """Get most recent organization sessions"""
        return self.history["sessions"][-count:]
    
    def get_category_distribution(self):
        """Get percentage distribution by category"""
        total_stats = self.get_total_stats()
        category_breakdown = total_stats["category_breakdown"]
        total = sum(category_breakdown.values())
        
        if total == 0:
            return {}
        
        return {
            category: round((count / total) * 100, 1)
            for category, count in category_breakdown.items()
        }
    
    def get_size_by_category(self):
        """Get total size organized by category"""
        size_by_category = defaultdict(float)
        
        for session in self.history["sessions"]:
            for category, data in session.get("categories", {}).items():
                size_by_category[category] += data["size_mb"]
        
        return {
            category: round(size, 2)
            for category, size in size_by_category.items()
        }
    
    def clear_history(self):
        """Clear all history"""
        self.history = {"sessions": []}
        self.save_history()
