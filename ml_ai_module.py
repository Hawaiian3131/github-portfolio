"""
Machine Learning & AI Module
Auto-categorization, anomaly detection, smart duplicate detection, content analysis
"""
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pickle
from collections import Counter
import json
from datetime import datetime


class MLFileCategorizer:
    """Machine learning-based file categorization"""
    
    def __init__(self, model_path: Path = None):
        self.model_path = model_path or Path("ml_model.pkl")
        self.vectorizer = None
        self.classifier = None
        self.training_data = []
        self.categories = set()
        
        # Try to load existing model
        if self.model_path.exists():
            self.load_model()
    
    def extract_features(self, file_path: Path) -> Dict:
        """
        Extract features from file for ML
        
        Returns:
            Feature dictionary
        """
        features = {
            'extension': file_path.suffix.lower(),
            'name_length': len(file_path.name),
            'has_number': any(c.isdigit() for c in file_path.name),
            'has_uppercase': any(c.isupper() for c in file_path.stem),
            'word_count': len(file_path.stem.split()),
            'size_kb': 0,
            'keywords': []
        }
        
        try:
            features['size_kb'] = file_path.stat().st_size / 1024
        except:
            pass
        
        # Extract keywords from filename
        name_lower = file_path.stem.lower()
        keywords = ['resume', 'cv', 'invoice', 'receipt', 'photo', 'video', 
                   'report', 'presentation', 'budget', 'tax', 'school', 'project']
        features['keywords'] = [kw for kw in keywords if kw in name_lower]
        
        return features
    
    def train(self, file_paths: List[Path], categories: List[str]):
        """
        Train ML model on labeled data
        
        Args:
            file_paths: List of file paths
            categories: Corresponding categories for each file
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            
            # Extract features
            X = []
            y = []
            
            for file_path, category in zip(file_paths, categories):
                features = self.extract_features(file_path)
                # Create feature string
                feature_str = f"{features['extension']} {' '.join(features['keywords'])}"
                X.append(feature_str)
                y.append(category)
                self.categories.add(category)
            
            # Train vectorizer and classifier
            self.vectorizer = TfidfVectorizer(max_features=100)
            X_vectorized = self.vectorizer.fit_transform(X)
            
            self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.classifier.fit(X_vectorized, y)
            
            # Save model
            self.save_model()
            
            return True, f"Model trained on {len(X)} files"
        
        except ImportError:
            return False, "scikit-learn not installed. Run: pip install scikit-learn"
        except Exception as e:
            return False, f"Training failed: {str(e)}"
    
    def predict(self, file_path: Path) -> Tuple[str, float]:
        """
        Predict category for a file
        
        Returns:
            (predicted_category, confidence)
        """
        if not self.classifier or not self.vectorizer:
            return "Other", 0.0
        
        try:
            features = self.extract_features(file_path)
            feature_str = f"{features['extension']} {' '.join(features['keywords'])}"
            
            X = self.vectorizer.transform([feature_str])
            
            # Get prediction with probability
            prediction = self.classifier.predict(X)[0]
            probabilities = self.classifier.predict_proba(X)[0]
            confidence = max(probabilities)
            
            return prediction, confidence
        except:
            return "Other", 0.0
    
    def save_model(self):
        """Save trained model"""
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'categories': list(self.categories)
        }
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self):
        """Load trained model"""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            self.vectorizer = model_data['vectorizer']
            self.classifier = model_data['classifier']
            self.categories = set(model_data['categories'])
            return True
        except:
            return False


class AnomalyDetector:
    """Detect unusual file patterns and behavior"""
    
    def __init__(self):
        self.baseline = {}
        self.anomalies = []
    
    def establish_baseline(self, file_paths: List[Path]):
        """
        Establish baseline from normal files
        
        Args:
            file_paths: List of normal files
        """
        sizes = []
        extensions = []
        name_lengths = []
        
        for fp in file_paths:
            if fp.is_file():
                try:
                    sizes.append(fp.stat().st_size)
                    extensions.append(fp.suffix.lower())
                    name_lengths.append(len(fp.name))
                except:
                    pass
        
        self.baseline = {
            'avg_size': np.mean(sizes) if sizes else 0,
            'std_size': np.std(sizes) if sizes else 0,
            'common_extensions': Counter(extensions).most_common(10),
            'avg_name_length': np.mean(name_lengths) if name_lengths else 0
        }
    
    def detect_anomalies(self, file_path: Path) -> Dict:
        """
        Detect if file is anomalous
        
        Returns:
            Anomaly report
        """
        if not self.baseline:
            return {"is_anomaly": False, "reasons": []}
        
        anomalies = []
        
        try:
            # Size anomaly
            size = file_path.stat().st_size
            if self.baseline['std_size'] > 0:
                z_score = abs((size - self.baseline['avg_size']) / self.baseline['std_size'])
                if z_score > 3:  # 3 standard deviations
                    anomalies.append(f"Unusual size (z-score: {z_score:.2f})")
            
            # Extension anomaly
            ext = file_path.suffix.lower()
            common_exts = [e for e, _ in self.baseline['common_extensions']]
            if ext not in common_exts and ext != '':
                anomalies.append(f"Unusual extension: {ext}")
            
            # Name length anomaly
            name_len = len(file_path.name)
            if abs(name_len - self.baseline['avg_name_length']) > 50:
                anomalies.append("Unusual filename length")
            
            # Hidden file
            if file_path.name.startswith('.'):
                anomalies.append("Hidden file")
            
            # Very recent modification (possible malware)
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if (datetime.now() - mod_time).total_seconds() < 60:
                anomalies.append("Very recently modified")
        
        except:
            pass
        
        return {
            "is_anomaly": len(anomalies) > 0,
            "reasons": anomalies,
            "severity": "HIGH" if len(anomalies) >= 3 else "MEDIUM" if len(anomalies) >= 2 else "LOW"
        }


class SmartDuplicateFinder:
    """Find similar (not identical) files"""
    
    def find_similar_files(self, file_paths: List[Path], threshold: float = 0.8) -> List[List[Path]]:
        """
        Find similar files based on multiple criteria
        
        Args:
            file_paths: Files to compare
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            Groups of similar files
        """
        similar_groups = []
        
        # Group by similarity
        for i, file1 in enumerate(file_paths):
            group = [file1]
            
            for file2 in file_paths[i+1:]:
                similarity = self.calculate_similarity(file1, file2)
                if similarity >= threshold:
                    group.append(file2)
            
            if len(group) > 1:
                similar_groups.append(group)
        
        return similar_groups
    
    def calculate_similarity(self, file1: Path, file2: Path) -> float:
        """
        Calculate similarity between two files
        
        Returns:
            Similarity score (0.0-1.0)
        """
        score = 0.0
        factors = 0
        
        # Name similarity
        name_sim = self.string_similarity(file1.stem, file2.stem)
        score += name_sim
        factors += 1
        
        # Extension match
        if file1.suffix == file2.suffix:
            score += 1.0
        factors += 1
        
        # Size similarity
        try:
            size1 = file1.stat().st_size
            size2 = file2.stat().st_size
            size_diff = abs(size1 - size2) / max(size1, size2, 1)
            score += (1.0 - size_diff)
            factors += 1
        except:
            pass
        
        return score / factors if factors > 0 else 0.0
    
    def string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (Jaccard)"""
        s1_set = set(s1.lower().split())
        s2_set = set(s2.lower().split())
        
        if not s1_set and not s2_set:
            return 1.0
        
        intersection = s1_set & s2_set
        union = s1_set | s2_set
        
        return len(intersection) / len(union) if union else 0.0


class ContentAnalyzer:
    """Analyze file content beyond extension"""
    
    def analyze_content(self, file_path: Path) -> Dict:
        """
        Analyze actual file content
        
        Returns:
            Content analysis report
        """
        result = {
            "file": str(file_path),
            "detected_type": "unknown",
            "confidence": 0.0,
            "properties": {}
        }
        
        try:
            # Read first few bytes
            with open(file_path, 'rb') as f:
                header = f.read(512)
            
            # Detect file type by magic bytes
            if header.startswith(b'%PDF'):
                result["detected_type"] = "PDF"
                result["confidence"] = 1.0
            elif header.startswith(b'PK\x03\x04'):
                result["detected_type"] = "ZIP/Office"
                result["confidence"] = 0.9
            elif header.startswith(b'\xff\xd8\xff'):
                result["detected_type"] = "JPEG"
                result["confidence"] = 1.0
            elif header.startswith(b'\x89PNG'):
                result["detected_type"] = "PNG"
                result["confidence"] = 1.0
            elif header[:4] in [b'RIFF', b'AVI ']:
                result["detected_type"] = "Audio/Video"
                result["confidence"] = 0.8
            
            # Text file detection
            try:
                text = header.decode('utf-8')
                if text.isprintable():
                    result["detected_type"] = "Text"
                    result["confidence"] = 0.7
            except:
                pass
        
        except:
            pass
        
        return result


class PredictiveOrganizer:
    """Predict where files should go based on patterns"""
    
    def __init__(self):
        self.patterns = {}
        self.history_file = Path("organization_patterns.json")
        self.load_patterns()
    
    def learn_pattern(self, file_path: Path, category: str):
        """Learn from user's organization"""
        pattern_key = f"{file_path.suffix}_{len(file_path.stem)}"
        
        if pattern_key not in self.patterns:
            self.patterns[pattern_key] = Counter()
        
        self.patterns[pattern_key][category] += 1
        self.save_patterns()
    
    def predict_category(self, file_path: Path) -> Tuple[str, float]:
        """
        Predict category based on learned patterns
        
        Returns:
            (predicted_category, confidence)
        """
        pattern_key = f"{file_path.suffix}_{len(file_path.stem)}"
        
        if pattern_key in self.patterns:
            most_common = self.patterns[pattern_key].most_common(1)
            if most_common:
                category, count = most_common[0]
                total = sum(self.patterns[pattern_key].values())
                confidence = count / total
                return category, confidence
        
        return "Unknown", 0.0
    
    def save_patterns(self):
        """Save learned patterns"""
        data = {k: dict(v) for k, v in self.patterns.items()}
        with open(self.history_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_patterns(self):
        """Load learned patterns"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            self.patterns = {k: Counter(v) for k, v in data.items()}


# Export all classes
__all__ = [
    'MLFileCategorizer',
    'AnomalyDetector',
    'SmartDuplicateFinder',
    'ContentAnalyzer',
    'PredictiveOrganizer'
]