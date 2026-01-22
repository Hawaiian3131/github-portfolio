"""
File Preview and Metadata Module
Preview images, PDFs, and extract file metadata
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import hashlib


class FileMetadata:
    def __init__(self, file_path: Path):
        """
        Extract file metadata
        
        Args:
            file_path: Path to file
        """
        self.file_path = file_path
        self.metadata = self.extract_metadata()
    
    def extract_metadata(self) -> Dict:
        """Extract all available metadata"""
        try:
            stat = self.file_path.stat()
            
            metadata = {
                "name": self.file_path.name,
                "path": str(self.file_path.absolute()),
                "extension": self.file_path.suffix,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "size_gb": round(stat.st_size / (1024 * 1024 * 1024), 3),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_hidden": self.file_path.name.startswith('.'),
                "is_system": False,  # Would need Windows-specific check
                "md5": None,
                "sha256": None
            }
            
            # Add EXIF data for images
            if self.file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                metadata.update(self.extract_image_metadata())
            
            return metadata
        except Exception as e:
            return {"error": str(e)}
    
    def extract_image_metadata(self) -> Dict:
        """Extract image-specific metadata (EXIF)"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            img = Image.open(self.file_path)
            
            metadata = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "exif": {}
            }
            
            # Extract EXIF data
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    metadata["exif"][tag] = str(value)
            
            return metadata
        except ImportError:
            return {"exif_error": "PIL/Pillow not installed"}
        except Exception as e:
            return {"exif_error": str(e)}
    
    def calculate_hash(self, algorithm: str = "md5") -> str:
        """
        Calculate file hash
        
        Args:
            algorithm: "md5" or "sha256"
            
        Returns:
            Hash string
        """
        try:
            if algorithm == "md5":
                hasher = hashlib.md5()
            elif algorithm == "sha256":
                hasher = hashlib.sha256()
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            with open(self.file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_formatted_size(self) -> str:
        """Get human-readable file size"""
        size = self.metadata.get("size_bytes", 0)
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        
        return f"{size:.2f} PB"
    
    def get_age_days(self) -> int:
        """Get file age in days"""
        try:
            modified = datetime.fromisoformat(self.metadata["modified"])
            return (datetime.now() - modified).days
        except:
            return 0


class FilePreview:
    @staticmethod
    def get_image_thumbnail(file_path: Path, size: tuple = (200, 200)):
        """
        Get image thumbnail
        
        Args:
            file_path: Path to image
            size: Thumbnail size (width, height)
            
        Returns:
            PIL Image object or None
        """
        try:
            from PIL import Image
            
            img = Image.open(file_path)
            img.thumbnail(size)
            return img
        except ImportError:
            return None
        except Exception as e:
            return None
    
    @staticmethod
    def get_pdf_first_page(file_path: Path, dpi: int = 150):
        """
        Get first page of PDF as image
        
        Args:
            file_path: Path to PDF
            dpi: Resolution
            
        Returns:
            PIL Image object or None
        """
        try:
            from pdf2image import convert_from_path
            
            images = convert_from_path(str(file_path), dpi=dpi, first_page=1, last_page=1)
            return images[0] if images else None
        except ImportError:
            return None
        except Exception as e:
            return None
    
    @staticmethod
    def get_text_preview(file_path: Path, lines: int = 10) -> Optional[str]:
        """
        Get preview of text file
        
        Args:
            file_path: Path to text file
            lines: Number of lines to preview
            
        Returns:
            Preview text or None
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                preview_lines = []
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    preview_lines.append(line.rstrip())
                
                return '\n'.join(preview_lines)
        except Exception as e:
            return None


class FileSearch:
    def __init__(self, search_root: Path):
        """
        Search for files
        
        Args:
            search_root: Root directory to search
        """
        self.search_root = search_root
    
    def search_by_name(self, query: str, case_sensitive: bool = False) -> List[Path]:
        """
        Search files by name
        
        Args:
            query: Search query
            case_sensitive: Case-sensitive search
            
        Returns:
            List of matching file paths
        """
        results = []
        
        if not case_sensitive:
            query = query.lower()
        
        for file_path in self.search_root.rglob('*'):
            if file_path.is_file():
                name = file_path.name if case_sensitive else file_path.name.lower()
                if query in name:
                    results.append(file_path)
        
        return results
    
    def search_by_extension(self, extensions: List[str]) -> List[Path]:
        """
        Search files by extension
        
        Args:
            extensions: List of extensions (e.g., ['.jpg', '.png'])
            
        Returns:
            List of matching file paths
        """
        results = []
        extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
        
        for file_path in self.search_root.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                results.append(file_path)
        
        return results
    
    def search_by_size(self, min_mb: Optional[float] = None, max_mb: Optional[float] = None) -> List[Path]:
        """
        Search files by size
        
        Args:
            min_mb: Minimum size in MB
            max_mb: Maximum size in MB
            
        Returns:
            List of matching file paths
        """
        results = []
        
        for file_path in self.search_root.rglob('*'):
            if file_path.is_file():
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    
                    if min_mb is not None and size_mb < min_mb:
                        continue
                    if max_mb is not None and size_mb > max_mb:
                        continue
                    
                    results.append(file_path)
                except:
                    continue
        
        return results
    
    def search_by_date(self, days_old: Optional[int] = None, newer_than_days: Optional[int] = None) -> List[Path]:
        """
        Search files by modification date
        
        Args:
            days_old: Files older than this many days
            newer_than_days: Files newer than this many days
            
        Returns:
            List of matching file paths
        """
        results = []
        
        for file_path in self.search_root.rglob('*'):
            if file_path.is_file():
                try:
                    file_age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
                    
                    if days_old is not None and file_age_days < days_old:
                        continue
                    if newer_than_days is not None and file_age_days > newer_than_days:
                        continue
                    
                    results.append(file_path)
                except:
                    continue
        
        return results
    
    def advanced_search(self, 
                       name: Optional[str] = None,
                       extensions: Optional[List[str]] = None,
                       min_mb: Optional[float] = None,
                       max_mb: Optional[float] = None,
                       days_old: Optional[int] = None) -> List[Path]:
        """
        Advanced search with multiple criteria
        
        Args:
            name: Filename contains
            extensions: File extensions
            min_mb: Minimum size
            max_mb: Maximum size
            days_old: Minimum age in days
            
        Returns:
            List of matching file paths
        """
        results = []
        
        for file_path in self.search_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Name filter
            if name and name.lower() not in file_path.name.lower():
                continue
            
            # Extension filter
            if extensions:
                ext_list = [e.lower() if e.startswith('.') else f'.{e.lower()}' for e in extensions]
                if file_path.suffix.lower() not in ext_list:
                    continue
            
            # Size filter
            try:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if min_mb and size_mb < min_mb:
                    continue
                if max_mb and size_mb > max_mb:
                    continue
            except:
                continue
            
            # Age filter
            try:
                if days_old:
                    file_age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
                    if file_age_days < days_old:
                        continue
            except:
                continue
            
            results.append(file_path)
        
        return results
