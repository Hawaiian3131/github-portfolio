"""
Undo System for File Organizer
Restore files to their original locations
"""
import json
import shutil
from pathlib import Path
from datetime import datetime


class UndoManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.undo_log = self.script_dir / "undo_log.json"
        self.operations = self.load_operations()
    
    def load_operations(self):
        """Load undo operations from file"""
        if self.undo_log.exists():
            with open(self.undo_log, 'r') as f:
                return json.load(f)
        return {"operations": []}
    
    def save_operations(self):
        """Save undo operations to file"""
        with open(self.undo_log, 'w') as f:
            json.dump(self.operations, f, indent=4)
    
    def record_operation(self, source, destination, operation_id=None):
        """
        Record a file operation for potential undo
        
        Args:
            source: Original file location
            destination: New file location
            operation_id: ID to group operations (e.g., session timestamp)
        """
        if operation_id is None:
            operation_id = datetime.now().isoformat()
        
        operation = {
            "id": operation_id,
            "timestamp": datetime.now().isoformat(),
            "source": str(source),
            "destination": str(destination),
            "undone": False
        }
        
        self.operations["operations"].append(operation)
        self.save_operations()
    
    def get_recent_operations(self, count=10):
        """Get most recent operations"""
        recent = [op for op in self.operations["operations"] if not op["undone"]]
        return recent[-count:]
    
    def get_operations_by_session(self, operation_id):
        """Get all operations from a specific session"""
        return [
            op for op in self.operations["operations"]
            if op["id"] == operation_id and not op["undone"]
        ]
    
    def undo_operation(self, operation):
        """
        Undo a single file operation
        
        Args:
            operation: Operation dictionary with source and destination
            
        Returns:
            (success, message)
        """
        try:
            source = Path(operation["source"])
            destination = Path(operation["destination"])
            
            # Check if destination file still exists
            if not destination.exists():
                return False, f"File not found: {destination.name}"
            
            # Create source directory if it doesn't exist
            source.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file back to original location
            shutil.move(str(destination), str(source))
            
            # Mark as undone
            for op in self.operations["operations"]:
                if op["source"] == str(source) and op["destination"] == str(destination):
                    op["undone"] = True
            
            self.save_operations()
            
            return True, f"Restored: {source.name}"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def undo_session(self, operation_id):
        """
        Undo all operations from a session
        
        Args:
            operation_id: Session ID to undo
            
        Returns:
            (success_count, error_count, messages)
        """
        operations = self.get_operations_by_session(operation_id)
        
        if not operations:
            return 0, 0, ["No operations found for this session"]
        
        success_count = 0
        error_count = 0
        messages = []
        
        for operation in operations:
            success, message = self.undo_operation(operation)
            messages.append(message)
            
            if success:
                success_count += 1
            else:
                error_count += 1
        
        return success_count, error_count, messages
    
    def undo_last_session(self):
        """Undo the most recent organization session"""
        recent_ops = self.get_recent_operations(count=1000)  # Get many operations
        
        if not recent_ops:
            return 0, 0, ["No operations to undo"]
        
        # Get the most recent session ID
        latest_id = recent_ops[-1]["id"]
        
        return self.undo_session(latest_id)
    
    def get_undo_history(self):
        """Get list of sessions that can be undone"""
        sessions = {}
        
        for op in self.operations["operations"]:
            if not op["undone"]:
                session_id = op["id"]
                if session_id not in sessions:
                    sessions[session_id] = {
                        "id": session_id,
                        "timestamp": op["timestamp"],
                        "file_count": 0
                    }
                sessions[session_id]["file_count"] += 1
        
        return list(sessions.values())
    
    def clear_history(self):
        """Clear all undo history"""
        self.operations = {"operations": []}
        self.save_operations()
