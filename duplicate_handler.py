"""
Advanced Duplicate File Handler
Compare, preview, and manage duplicate files
"""
import hashlib
from pathlib import Path
from datetime import datetime


class DuplicateHandler:
    def __init__(self, compare_mode: str = "content"):
        """
        Initialize duplicate handler
        
        Args:
            compare_mode: "content" (MD5), "name", "size", or "all"
        """
        self.duplicates = {}
        self.compare_mode = compare_mode
    
    def find_duplicates(self, files_to_check, similarity_threshold: float = 1.0):
        """
        Find all duplicate files
        
        Args:
            files_to_check: List of file paths
            similarity_threshold: 0.0-1.0, for fuzzy matching (1.0 = exact match)
            
        Returns:
            Dictionary mapping hash/key to list of duplicate file info
        """
        hash_map = {}
        duplicates = {}
        
        for file_path in files_to_check:
            if not file_path.is_file():
                continue
            
            # Generate comparison key based on mode
            if self.compare_mode == "content":
                file_key = self.get_file_hash(file_path)
            elif self.compare_mode == "name":
                file_key = file_path.name.lower()
            elif self.compare_mode == "size":
                file_key = str(file_path.stat().st_size)
            elif self.compare_mode == "all":
                # Combined: name + size + content
                file_key = f"{file_path.name.lower()}_{file_path.stat().st_size}_{self.get_file_hash(file_path)}"
            else:
                file_key = self.get_file_hash(file_path)
            
            file_info = self.get_file_info(file_path)
            
            if file_key:
                if file_key in hash_map:
                    # Found a duplicate
                    if file_key not in duplicates:
                        duplicates[file_key] = [hash_map[file_key]]
                    duplicates[file_key].append(file_info)
                else:
                    hash_map[file_key] = file_info
        
        self.duplicates = duplicates
        return duplicates
    
    def get_file_hash(self, file_path):
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def get_file_info(self, file_path):
        """Get detailed file information"""
        try:
            stat = file_path.stat()
            return {
                "path": str(file_path),
                "name": file_path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": file_path.suffix
            }
        except Exception:
            return None
    
    def compare_duplicates(self, file_hash):
        """
        Compare all duplicates of a specific hash
        
        Returns:
            List of file info dictionaries sorted by various criteria
        """
        if file_hash not in self.duplicates:
            return None
        
        files = self.duplicates[file_hash]
        
        return {
            "by_size": sorted(files, key=lambda x: x["size_bytes"]),
            "by_date": sorted(files, key=lambda x: x["created"]),
            "by_name": sorted(files, key=lambda x: x["name"]),
            "original": files  # Unsorted
        }
    
    def recommend_to_keep(self, file_hash, strategy="oldest"):
        """
        Recommend which duplicate to keep
        
        Args:
            file_hash: Hash of duplicate set
            strategy: "oldest", "newest", "smallest", "largest", "shortest_name"
            
        Returns:
            File info dictionary of recommended file to keep
        """
        if file_hash not in self.duplicates:
            return None
        
        files = self.duplicates[file_hash]
        
        if strategy == "oldest":
            return min(files, key=lambda x: x["created"])
        elif strategy == "newest":
            return max(files, key=lambda x: x["created"])
        elif strategy == "smallest":
            return min(files, key=lambda x: x["size_bytes"])
        elif strategy == "largest":
            return max(files, key=lambda x: x["size_bytes"])
        elif strategy == "shortest_name":
            return min(files, key=lambda x: len(x["name"]))
        else:
            return files[0]  # Default to first found
    
    def get_duplicates_to_remove(self, file_hash, keep_file):
        """
        Get list of duplicates to remove (all except the one to keep)
        
        Args:
            file_hash: Hash of duplicate set
            keep_file: File info dictionary of file to keep
            
        Returns:
            List of file info dictionaries to remove
        """
        if file_hash not in self.duplicates:
            return []
        
        return [
            f for f in self.duplicates[file_hash]
            if f["path"] != keep_file["path"]
        ]
    
    def move_duplicates_to_review(self, duplicates, review_folder):
        """
        Move duplicate files to a review folder
        
        Args:
            duplicates: List of file info dictionaries
            review_folder: Path to review folder
            
        Returns:
            (success_count, error_count, messages)
        """
        import shutil
        
        review_path = Path(review_folder)
        review_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        error_count = 0
        messages = []
        
        for file_info in duplicates:
            try:
                source = Path(file_info["path"])
                destination = review_path / source.name
                
                # Handle name conflicts in review folder
                counter = 1
                while destination.exists():
                    stem = source.stem
                    suffix = source.suffix
                    destination = review_path / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                shutil.move(str(source), str(destination))
                messages.append(f"Moved to review: {source.name}")
                success_count += 1
                
            except Exception as e:
                messages.append(f"Error moving {file_info['name']}: {str(e)}")
                error_count += 1
        
        return success_count, error_count, messages
    
    def auto_resolve_duplicates(self, strategy: str = "oldest", dry_run: bool = True) -> Dict:
        """
        Automatically resolve all duplicates using specified strategy
        
        Args:
            strategy: "oldest", "newest", "smallest", "largest", "shortest_name"
            dry_run: If True, only show what would be done
            
        Returns:
            Dictionary with results: {
                "kept": List of files kept,
                "removed": List of files that would be removed,
                "space_saved_mb": Amount of space saved
            }
        """
        results = {
            "kept": [],
            "removed": [],
            "space_saved_mb": 0
        }
        
        for file_hash, files in self.duplicates.items():
            if len(files) <= 1:
                continue
            
            # Determine which file to keep
            keep_file = self.recommend_to_keep(file_hash, strategy)
            to_remove = self.get_duplicates_to_remove(file_hash, keep_file)
            
            results["kept"].append(keep_file)
            
            for file_info in to_remove:
                results["removed"].append(file_info)
                results["space_saved_mb"] += file_info["size_mb"]
                
                if not dry_run:
                    # Actually remove the file
                    try:
                        Path(file_info["path"]).unlink()
                    except Exception as e:
                        print(f"Error removing {file_info['path']}: {e}")
        
        return results
    
    def compare_duplicates_side_by_side(self, file_hash: str) -> Dict:
        """
        Show duplicate files side-by-side for comparison
        
        Args:
            file_hash: Hash of duplicate set
            
        Returns:
            Dictionary with comparison data
        """
        if file_hash not in self.duplicates:
            return None
        
        files = self.duplicates[file_hash]
        
        comparison = {
            "count": len(files),
            "files": [],
            "differences": []
        }
        
        for file_info in files:
            comparison["files"].append({
                "name": file_info["name"],
                "path": file_info["path"],
                "size": file_info["size_mb"],
                "created": file_info["created"],
                "modified": file_info["modified"]
            })
        
        # Check for differences
        if len(files) > 1:
            # Compare creation dates
            created_dates = [f["created"] for f in files]
            if len(set(created_dates)) > 1:
                comparison["differences"].append("Different creation dates")
            
            # Compare sizes (might differ slightly for near-duplicates)
            sizes = [f["size_bytes"] for f in files]
            if len(set(sizes)) > 1:
                comparison["differences"].append("Different file sizes")
        
        return comparison
        """Get summary statistics about duplicates"""
        if not self.duplicates:
            return {
                "duplicate_sets": 0,
                "total_duplicate_files": 0,
                "wasted_space_mb": 0
            }
        
        total_files = sum(len(files) for files in self.duplicates.values())
        
        # Calculate wasted space (all duplicates except one per set)
        wasted_space = 0
        for files in self.duplicates.values():
            if len(files) > 1:
                file_size = files[0]["size_bytes"]
                wasted_space += file_size * (len(files) - 1)
        
        return {
            "duplicate_sets": len(self.duplicates),
            "total_duplicate_files": total_files,
            "wasted_space_mb": round(wasted_space / (1024 * 1024), 2)
        }
