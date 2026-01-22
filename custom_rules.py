"""
Custom Categories and Rules Builder
GUI editor for creating custom organization rules
"""
import json
from pathlib import Path
from typing import Dict, List, Optional


class CustomCategoryManager:
    def __init__(self, config_file: Path = None):
        """
        Manage custom categories
        
        Args:
            config_file: Path to custom categories JSON file
        """
        self.config_file = config_file or Path("custom_categories.json")
        self.categories = self.load_categories()
    
    def load_categories(self) -> Dict:
        """Load custom categories from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "categories": {},
            "rules": []
        }
    
    def save_categories(self):
        """Save categories to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.categories, f, indent=4)
    
    def add_category(self, name: str, description: str = "", parent: Optional[str] = None):
        """
        Add a new category
        
        Args:
            name: Category name
            description: Category description
            parent: Parent category for subcategories
        """
        if parent:
            category_path = f"{parent}/{name}"
        else:
            category_path = name
        
        self.categories["categories"][category_path] = {
            "name": name,
            "description": description,
            "parent": parent,
            "subcategories": []
        }
        
        # Update parent's subcategories list
        if parent and parent in self.categories["categories"]:
            if category_path not in self.categories["categories"][parent]["subcategories"]:
                self.categories["categories"][parent]["subcategories"].append(category_path)
        
        self.save_categories()
    
    def remove_category(self, category_path: str):
        """Remove a category"""
        if category_path in self.categories["categories"]:
            del self.categories["categories"][category_path]
            self.save_categories()
    
    def get_all_categories(self) -> List[str]:
        """Get list of all category paths"""
        return list(self.categories["categories"].keys())
    
    def get_category_tree(self) -> Dict:
        """Get hierarchical category tree"""
        tree = {}
        
        for path, info in self.categories["categories"].items():
            if not info["parent"]:
                # Top-level category
                tree[path] = {
                    "info": info,
                    "children": self._get_children(path)
                }
        
        return tree
    
    def _get_children(self, parent: str) -> Dict:
        """Get children of a category"""
        children = {}
        
        for path, info in self.categories["categories"].items():
            if info["parent"] == parent:
                children[path] = {
                    "info": info,
                    "children": self._get_children(path)
                }
        
        return children


class RuleBuilder:
    def __init__(self, config_file: Path = None):
        """
        Build and manage custom rules
        
        Args:
            config_file: Path to rules JSON file
        """
        self.config_file = config_file or Path("custom_rules.json")
        self.rules = self.load_rules()
    
    def load_rules(self) -> List[Dict]:
        """Load rules from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_rules(self):
        """Save rules to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.rules, f, indent=4)
    
    def add_rule(self, rule_type: str, condition: Dict, action: Dict, priority: int = 0, enabled: bool = True):
        """
        Add a new rule
        
        Args:
            rule_type: "if_then", "filename_contains", "extension", "size", "age", "regex"
            condition: Condition parameters
            action: Action to take (category, etc.)
            priority: Rule priority (higher = checked first)
            enabled: Whether rule is active
        """
        rule = {
            "id": self._generate_rule_id(),
            "type": rule_type,
            "condition": condition,
            "action": action,
            "priority": priority,
            "enabled": enabled,
            "created": str(Path(__file__).stat().st_ctime)
        }
        
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x["priority"], reverse=True)
        self.save_rules()
        
        return rule["id"]
    
    def _generate_rule_id(self) -> str:
        """Generate unique rule ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def remove_rule(self, rule_id: str):
        """Remove a rule by ID"""
        self.rules = [r for r in self.rules if r["id"] != rule_id]
        self.save_rules()
    
    def enable_rule(self, rule_id: str, enabled: bool = True):
        """Enable or disable a rule"""
        for rule in self.rules:
            if rule["id"] == rule_id:
                rule["enabled"] = enabled
                break
        self.save_rules()
    
    def update_rule(self, rule_id: str, updates: Dict):
        """Update a rule"""
        for rule in self.rules:
            if rule["id"] == rule_id:
                rule.update(updates)
                break
        self.save_rules()
    
    def get_rule(self, rule_id: str) -> Optional[Dict]:
        """Get a rule by ID"""
        for rule in self.rules:
            if rule["id"] == rule_id:
                return rule
        return None
    
    def get_all_rules(self, enabled_only: bool = False) -> List[Dict]:
        """Get all rules"""
        if enabled_only:
            return [r for r in self.rules if r["enabled"]]
        return self.rules
    
    def create_if_then_rule(self, if_type: str, if_params: Dict, then_category: str, priority: int = 0):
        """
        Create an if-then rule
        
        Args:
            if_type: "contains", "matches", "extension", "size", "age"
            if_params: Parameters for the condition
            then_category: Destination category
            priority: Rule priority
        """
        condition = {
            "type": if_type,
            "params": if_params
        }
        
        action = {
            "type": "categorize",
            "category": then_category
        }
        
        return self.add_rule("if_then", condition, action, priority)


# Preset rule templates
RULE_TEMPLATES = {
    "work_project": {
        "name": "Work Projects",
        "description": "Organize work files by project",
        "rules": [
            {
                "type": "if_then",
                "condition": {"type": "contains", "params": {"keyword": "project"}},
                "action": {"type": "categorize", "category": "Work/Projects"},
                "priority": 10
            },
            {
                "type": "if_then",
                "condition": {"type": "contains", "params": {"keyword": "client"}},
                "action": {"type": "categorize", "category": "Work/Clients"},
                "priority": 10
            }
        ]
    },
    "media_library": {
        "name": "Media Library",
        "description": "Organize media by type and date",
        "rules": [
            {
                "type": "if_then",
                "condition": {"type": "extension", "params": {"extensions": [".jpg", ".png"]}},
                "action": {"type": "categorize", "category": "Media/Photos"},
                "priority": 5
            },
            {
                "type": "if_then",
                "condition": {"type": "extension", "params": {"extensions": [".mp4", ".avi"]}},
                "action": {"type": "categorize", "category": "Media/Videos"},
                "priority": 5
            }
        ]
    },
    "archive_old": {
        "name": "Archive Old Files",
        "description": "Auto-archive files older than 90 days",
        "rules": [
            {
                "type": "if_then",
                "condition": {"type": "age", "params": {"min_days": 90}},
                "action": {"type": "categorize", "category": "Archive"},
                "priority": 1
            }
        ]
    },
    "size_based": {
        "name": "Size-Based Organization",
        "description": "Organize by file size",
        "rules": [
            {
                "type": "if_then",
                "condition": {"type": "size", "params": {"max_mb": 1}},
                "action": {"type": "categorize", "category": "Small Files"},
                "priority": 3
            },
            {
                "type": "if_then",
                "condition": {"type": "size", "params": {"min_mb": 100}},
                "action": {"type": "categorize", "category": "Large Files"},
                "priority": 3
            }
        ]
    }
}


# Example category structures
EXAMPLE_CATEGORY_STRUCTURES = {
    "work_structure": {
        "Work": {
            "Projects": ["Project A", "Project B", "Project C"],
            "Clients": ["Client 1", "Client 2"],
            "Finance": ["Invoices", "Receipts", "Taxes"]
        }
    },
    "personal_structure": {
        "Personal": {
            "Documents": ["Taxes", "Legal", "Medical"],
            "Finance": ["Bank Statements", "Investments"],
            "Career": ["Resumes", "Certifications"]
        }
    },
    "media_structure": {
        "Media": {
            "Photos": ["Family", "Vacation", "Work"],
            "Videos": ["Personal", "Projects"],
            "Music": ["Playlists", "Albums"]
        }
    }
}
