"""
Performance & Safety Module
Multi-threading, progress tracking, and transaction management
"""
import threading
import queue
from pathlib import Path
from typing import List, Callable, Dict, Optional
import shutil
import hashlib
from datetime import datetime
import json


class ThreadedScanner:
    def __init__(self, num_threads: int = 4):
        """
        Multi-threaded file scanner
        
        Args:
            num_threads: Number of worker threads
        """
        self.num_threads = num_threads
        self.file_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.progress = {"scanned": 0, "total": 0, "errors": 0}
        self.stop_flag = threading.Event()
    
    def worker(self, process_func: Callable):
        """Worker thread that processes files"""
        while not self.stop_flag.is_set():
            try:
                file_path = self.file_queue.get(timeout=1)
                if file_path is None:  # Poison pill
                    break
                
                try:
                    result = process_func(file_path)
                    self.result_queue.put(("success", file_path, result))
                except Exception as e:
                    self.result_queue.put(("error", file_path, str(e)))
                    self.progress["errors"] += 1
                
                self.progress["scanned"] += 1
                self.file_queue.task_done()
            
            except queue.Empty:
                continue
    
    def scan_threaded(self, file_paths: List[Path], process_func: Callable) -> List:
        """
        Scan files using multiple threads
        
        Args:
            file_paths: List of file paths to process
            process_func: Function to apply to each file
            
        Returns:
            List of results
        """
        self.progress["total"] = len(file_paths)
        self.progress["scanned"] = 0
        self.progress["errors"] = 0
        
        # Start worker threads
        threads = []
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.worker, args=(process_func,))
            t.start()
            threads.append(t)
        
        # Add files to queue
        for file_path in file_paths:
            self.file_queue.put(file_path)
        
        # Add poison pills
        for _ in range(self.num_threads):
            self.file_queue.put(None)
        
        # Wait for completion
        self.file_queue.join()
        for t in threads:
            t.join()
        
        # Collect results
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())
        
        return results
    
    def get_progress(self) -> Dict:
        """Get current progress"""
        return {
            "scanned": self.progress["scanned"],
            "total": self.progress["total"],
            "percent": (self.progress["scanned"] / self.progress["total"] * 100) if self.progress["total"] > 0 else 0,
            "errors": self.progress["errors"]
        }
    
    def stop(self):
        """Stop all threads"""
        self.stop_flag.set()


class ProgressTracker:
    def __init__(self, total: int, callback: Optional[Callable] = None):
        """
        Track progress of long operations
        
        Args:
            total: Total number of items
            callback: Optional callback function(current, total, percent)
        """
        self.total = total
        self.current = 0
        self.callback = callback
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        
        if self.callback:
            percent = (self.current / self.total * 100) if self.total > 0 else 0
            self.callback(self.current, self.total, percent)
    
    def get_progress(self) -> Dict:
        """Get current progress info"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        percent = (self.current / self.total * 100) if self.total > 0 else 0
        
        # Estimate remaining time
        if self.current > 0:
            rate = self.current / elapsed
            remaining_items = self.total - self.current
            eta_seconds = remaining_items / rate if rate > 0 else 0
        else:
            eta_seconds = 0
        
        return {
            "current": self.current,
            "total": self.total,
            "percent": percent,
            "elapsed_seconds": elapsed,
            "eta_seconds": eta_seconds
        }


class FileOperationQueue:
    def __init__(self):
        """Queue for batching file operations"""
        self.operations = []
        self.completed = []
        self.failed = []
    
    def add_operation(self, operation_type: str, source: Path, destination: Path, metadata: Dict = None):
        """
        Add operation to queue
        
        Args:
            operation_type: "move", "copy", "delete"
            source: Source file path
            destination: Destination file path
            metadata: Optional metadata dict
        """
        self.operations.append({
            "type": operation_type,
            "source": source,
            "destination": destination,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def execute_all(self, verify_integrity: bool = True) -> Dict:
        """
        Execute all queued operations
        
        Args:
            verify_integrity: If True, verify file integrity after operations
            
        Returns:
            Results dictionary
        """
        results = {
            "success": 0,
            "failed": 0,
            "operations": []
        }
        
        for operation in self.operations:
            try:
                if operation["type"] == "move":
                    shutil.move(str(operation["source"]), str(operation["destination"]))
                elif operation["type"] == "copy":
                    shutil.copy2(str(operation["source"]), str(operation["destination"]))
                elif operation["type"] == "delete":
                    operation["source"].unlink()
                
                # Verify integrity if requested
                if verify_integrity and operation["type"] in ["move", "copy"]:
                    if not self.verify_file_integrity(operation["source"], operation["destination"]):
                        raise Exception("Integrity check failed")
                
                self.completed.append(operation)
                results["success"] += 1
                results["operations"].append({"status": "success", "operation": operation})
            
            except Exception as e:
                self.failed.append({"operation": operation, "error": str(e)})
                results["failed"] += 1
                results["operations"].append({"status": "failed", "operation": operation, "error": str(e)})
        
        self.operations = []  # Clear queue
        return results
    
    def verify_file_integrity(self, source: Path, destination: Path) -> bool:
        """
        Verify file was copied/moved correctly
        
        Args:
            source: Original file (might not exist after move)
            destination: Destination file
            
        Returns:
            True if integrity verified, False otherwise
        """
        try:
            # For moves, source won't exist, so just check destination exists
            if not destination.exists():
                return False
            
            # If source still exists, compare sizes
            if source.exists():
                return source.stat().st_size == destination.stat().st_size
            
            return True
        except:
            return False
    
    def rollback_last_batch(self) -> Dict:
        """
        Rollback last batch of completed operations
        
        Returns:
            Rollback results
        """
        results = {
            "rolled_back": 0,
            "failed": 0
        }
        
        for operation in reversed(self.completed):
            try:
                if operation["type"] == "move":
                    # Move back to original location
                    shutil.move(str(operation["destination"]), str(operation["source"]))
                elif operation["type"] == "copy":
                    # Delete the copy
                    operation["destination"].unlink()
                elif operation["type"] == "delete":
                    # Can't undo delete
                    results["failed"] += 1
                    continue
                
                results["rolled_back"] += 1
            except Exception as e:
                results["failed"] += 1
        
        self.completed = []
        return results
    
    def save_transaction_log(self, filepath: Path):
        """Save transaction log to file"""
        log_data = {
            "operations": [
                {
                    "type": op["type"],
                    "source": str(op["source"]),
                    "destination": str(op["destination"]),
                    "timestamp": op["timestamp"]
                }
                for op in self.completed
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=4)
    
    def clear_queue(self):
        """Clear all queued operations"""
        self.operations = []


class TransactionManager:
    def __init__(self):
        """Manage file operations with transaction support"""
        self.transaction_log = []
        self.in_transaction = False
    
    def begin_transaction(self):
        """Start a new transaction"""
        self.in_transaction = True
        self.transaction_log = []
    
    def record_operation(self, operation_type: str, source: Path, destination: Path):
        """Record an operation in the transaction"""
        self.transaction_log.append({
            "type": operation_type,
            "source": str(source),
            "destination": str(destination),
            "timestamp": datetime.now().isoformat()
        })
    
    def commit(self):
        """Commit the transaction"""
        self.in_transaction = False
        # Transaction log is kept for rollback if needed
    
    def rollback(self) -> Dict:
        """Rollback the entire transaction"""
        results = {
            "rolled_back": 0,
            "failed": 0,
            "errors": []
        }
        
        for operation in reversed(self.transaction_log):
            try:
                if operation["type"] == "move":
                    # Move back
                    shutil.move(operation["destination"], operation["source"])
                    results["rolled_back"] += 1
                elif operation["type"] == "copy":
                    # Delete copy
                    Path(operation["destination"]).unlink()
                    results["rolled_back"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))
        
        self.transaction_log = []
        self.in_transaction = False
        
        return results
