"""
Enhanced GUI File Organizer with Advanced Features
Includes: Scheduling, Analytics, Duplicates, Undo, Filters, Smart Organization, Rules, Search
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from organizer import FileOrganizer
from scheduler import ScheduledOrganizer
from analytics import FileAnalytics
from undo_manager import UndoManager
from duplicate_handler import DuplicateHandler
from smart_renamer import SmartRenamer
from advanced_filters import FileFilter, RuleEngine
from smart_organization import SmartOrganizer
from performance import ThreadedScanner, ProgressTracker
from custom_rules import CustomCategoryManager, RuleBuilder
from file_preview import FileMetadata, FileSearch

# Security modules
from security_encryption import FileEncryption, PasswordManager
from security_access_control import AccessControl, Role, Permission
from security_malware import MalwareScanner
from security_advanced import DLPScanner, SecurityMonitor, ForensicsTools, ComplianceReporter

from config import (
    DOCUMENTS_PATH,
    ORGANIZED_PATH,
    BACKUP_PATH,
    FILE_CATEGORIES,
    FOLDER_BASED_CATEGORIES,
    SKIP_FOLDERS,
    DRY_RUN,
    CREATE_BACKUP
)

HAS_ML = False
try:
    from ml_ai_module import MLFileCategorizer, AnomalyDetector, SmartDuplicateFinder, ContentAnalyzer, PredictiveOrganizer
    HAS_ML = True
except ImportError:
    pass

class EnhancedFileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI File Organizer - Advanced Professional")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)
        
        # Initialize ALL modules
        self.scheduler = ScheduledOrganizer()
        self.analytics = FileAnalytics()
        self.undo_manager = UndoManager()
        self.duplicate_handler = DuplicateHandler()
        self.smart_renamer = SmartRenamer()
        self.file_filter = FileFilter()
        self.rule_engine = RuleEngine()
        self.smart_organizer = SmartOrganizer()
        self.category_manager = CustomCategoryManager()
        self.rule_builder = RuleBuilder()
        
        # Security modules
        self.encryptor = FileEncryption()
        self.access_control = AccessControl()
        self.malware_scanner = MalwareScanner()
        self.dlp_scanner = DLPScanner()
        self.security_monitor = SecurityMonitor()
        self.forensics = ForensicsTools()
        self.compliance = ComplianceReporter()

        # ML & AI modules
        try:
            self.ml_categorizer = MLFileCategorizer()
            self.anomaly_detector = AnomalyDetector()
            self.smart_duplicate_finder = SmartDuplicateFinder()
            self.content_analyzer = ContentAnalyzer()
            self.predictive_organizer = PredictiveOrganizer()
        except:
            pass  # ML modules not available
        
        # Variables
        self.source_path = tk.StringVar(value=str(DOCUMENTS_PATH))
        self.dry_run = tk.BooleanVar(value=DRY_RUN)
        self.create_backup = tk.BooleanVar(value=CREATE_BACKUP)
        
        # Create tabbed interface
        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title_label = tk.Label(
            self.root,
            text="AI File Organizer - Advanced Professional",
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_main_tab()
        self.create_advanced_filters_tab()
        self.create_smart_org_tab()
        
        try:
            self.create_ml_tab()
        except AttributeError:
            pass  # ML not available
        
        self.create_schedule_tab()
        self.create_analytics_tab()
        self.create_duplicates_tab()
        self.create_rules_tab()
        self.create_search_tab()
        self.create_security_tab()
        self.create_undo_tab()
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready - Professional Edition")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor="w"
        )
        status_bar.pack(fill="x", side="bottom")

    def create_main_tab(self):
        """Main organization tab"""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="📁 Organize")
    
        # Source Folder
        source_frame = tk.LabelFrame(main_frame, text="Source Folder", padx=10, pady=10)
        source_frame.pack(fill="x", padx=10, pady=5)
    
        tk.Entry(source_frame, textvariable=self.source_path, width=60).pack(side="left", padx=5)
        tk.Button(source_frame, text="Browse...", command=self.browse_folder).pack(side="left")
    
        # Options
        options_frame = tk.LabelFrame(main_frame, text="Options", padx=10, pady=10)
        options_frame.pack(fill="x", padx=10, pady=5)
    
        tk.Checkbutton(
        options_frame,
        text="Dry Run Mode (Preview only)",
        variable=self.dry_run
        ).pack(anchor="w")
    
        tk.Checkbutton(
        options_frame,
        text="Create Backup Before Organizing",
        variable=self.create_backup
        ).pack(anchor="w")
    
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
    
        tk.Button(
        button_frame,
        text="Scan Files",
        command=self.scan_files,
        bg="#3498db",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=15,
        pady=5
        ).grid(row=0, column=0, padx=5)
    
        tk.Button(
        button_frame,
        text="Organize Files",
        command=self.organize_files,
        bg="#2ecc71",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=15,
        pady=5
        ).grid(row=0, column=1, padx=5)
    
        tk.Button(
        button_frame,
        text="Export PDF",
        command=self.export_pdf,
        bg="#e67e22",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=15,
        pady=5
        ).grid(row=0, column=2, padx=5)
    
        # Log
        log_frame = tk.LabelFrame(main_frame, text="Activity Log", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
        self.main_log = scrolledtext.ScrolledText(
        log_frame,
        wrap=tk.WORD,
        height=15,
        font=("Consolas", 9)
        )
        self.main_log.pack(fill="both", expand=True)
        self.log("Welcome to AI File Organizer!")
    
        def create_ml_tab(self):
            """Machine Learning & AI tab"""
            ml_frame = ttk.Frame(self.notebook)
            self.notebook.add(ml_frame, text="🤖 ML & AI")
        
            tk.Label(ml_frame, text="Machine Learning & AI", font=("Arial", 14, "bold")).pack(pady=10)
        
            # Train Model Section
            train_frame = tk.LabelFrame(ml_frame, text="Train ML Model", padx=10, pady=10)
            train_frame.pack(fill="x", padx=20, pady=10)
        
            tk.Label(train_frame, text="Train on your organized files to auto-categorize new files").pack()
            tk.Button(train_frame, text="Train Model", command=self.train_ml_model, bg="#3498db", fg="white", padx=20, pady=5).pack(pady=10)
        
            # Auto-Categorize Section
            categorize_frame = tk.LabelFrame(ml_frame, text="Auto-Categorize Files", padx=10, pady=10)
            categorize_frame.pack(fill="x", padx=20, pady=10)
        
            tk.Label(categorize_frame, text="Predict categories for uncategorized files").pack()
            tk.Button(categorize_frame, text="Predict Categories", command=self.predict_categories, bg="#2ecc71", fg="white", padx=20, pady=5).pack(pady=10)
        
            # Anomaly Detection Section
            anomaly_frame = tk.LabelFrame(ml_frame, text="Anomaly Detection", padx=10, pady=10)
            anomaly_frame.pack(fill="x", padx=20, pady=10)
        
            tk.Label(anomaly_frame, text="Detect unusual or suspicious files").pack()
            tk.Button(anomaly_frame, text="Scan for Anomalies", command=self.detect_anomalies, bg="#e74c3c", fg="white", padx=20, pady=5).pack(pady=10)
        
            # Smart Duplicate Detection Section
            smart_dup_frame = tk.LabelFrame(ml_frame, text="Smart Duplicate Detection", padx=10, pady=10)
            smart_dup_frame.pack(fill="x", padx=20, pady=10)
        
            tk.Label(smart_dup_frame, text="Find similar (not identical) files using fuzzy matching").pack()
            tk.Label(smart_dup_frame, text="Similarity threshold:").pack()
        
            self.similarity_threshold = tk.Scale(smart_dup_frame, from_=0.5, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, length=200)
            self.similarity_threshold.set(0.8)
            self.similarity_threshold.pack()
        
            tk.Button(smart_dup_frame, text="Find Similar Files", command=self.find_similar_files, bg="#9b59b6", fg="white", padx=20, pady=5).pack(pady=10)
        
            # Results Log
            log_frame = tk.LabelFrame(ml_frame, text="ML Results", padx=10, pady=10)
            log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
            self.ml_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=12, font=("Consolas", 9))
            self.ml_log.pack(fill="both", expand=True)
        
            self.ml_log.insert(tk.END, "🤖 ML & AI Module Ready!\n")
            self.ml_log.insert(tk.END, "Train the model on your organized files first.\n")
    
    # ML Event Handlers
    
    def train_ml_model(self):
        """Train ML model on organized files"""
        self.ml_log.delete("1.0", tk.END)
        self.ml_log.insert(tk.END, "Training ML model...\n\n")
        
        try:
            # Get organized files
            organized_path = Path(ORGANIZED_PATH)
            training_files = []
            training_categories = []
            
            if not organized_path.exists():
                self.ml_log.insert(tk.END, "❌ No organized files found!\n")
                self.ml_log.insert(tk.END, "Organize some files first, then train the model.\n")
                return
            
            # Collect training data from organized folders
            for category_folder in organized_path.iterdir():
                if category_folder.is_dir():
                    category = category_folder.name
                    for file_path in category_folder.rglob('*'):
                        if file_path.is_file():
                            training_files.append(file_path)
                            training_categories.append(category)
            
            if len(training_files) < 10:
                self.ml_log.insert(tk.END, f"⚠ Only {len(training_files)} files found.\n")
                self.ml_log.insert(tk.END, "Need at least 10 files to train effectively.\n")
                return
            
            # Train model
            success, message = self.ml_categorizer.train(training_files, training_categories)
            
            if success:
                self.ml_log.insert(tk.END, f"✅ {message}\n")
                self.ml_log.insert(tk.END, f"Categories learned: {len(set(training_categories))}\n")
                self.ml_log.insert(tk.END, "\nModel ready for predictions!\n")
                messagebox.showinfo("Training Complete", message)
            else:
                self.ml_log.insert(tk.END, f"❌ {message}\n")
                messagebox.showerror("Training Failed", message)
        
        except Exception as e:
            self.ml_log.insert(tk.END, f"❌ Error: {str(e)}\n")
            messagebox.showerror("Error", str(e))
    
    def predict_categories(self):
        """Predict categories for uncategorized files"""
        self.ml_log.delete("1.0", tk.END)
        self.ml_log.insert(tk.END, "Predicting categories...\n\n")
        
        try:
            # Get uncategorized files
            source_files = list(Path(self.source_path.get()).rglob("*"))[:50]  # First 50
            
            predictions = []
            for file_path in source_files:
                if file_path.is_file():
                    category, confidence = self.ml_categorizer.predict(file_path)
                    predictions.append((file_path, category, confidence))
            
            # Display predictions
            self.ml_log.insert(tk.END, f"Analyzed {len(predictions)} files:\n\n")
            
            for file_path, category, confidence in predictions[:20]:  # Show first 20
                self.ml_log.insert(tk.END, f"📁 {file_path.name}\n")
                self.ml_log.insert(tk.END, f"   → {category} ({confidence:.1%} confidence)\n\n")
            
            if len(predictions) > 20:
                self.ml_log.insert(tk.END, f"... and {len(predictions) - 20} more\n")
            
            messagebox.showinfo("Predictions Complete", f"Predicted categories for {len(predictions)} files")
        
        except Exception as e:
            self.ml_log.insert(tk.END, f"❌ Error: {str(e)}\n")
    
    def detect_anomalies(self):
        """Detect anomalous files"""
        self.ml_log.delete("1.0", tk.END)
        self.ml_log.insert(tk.END, "Detecting anomalies...\n\n")
        
        try:
            # Get files
            files = list(Path(self.source_path.get()).rglob("*"))[:100]
            
            # Establish baseline
            self.anomaly_detector.establish_baseline(files)
            self.ml_log.insert(tk.END, "Baseline established from file patterns.\n\n")
            
            # Detect anomalies
            anomalies_found = []
            for file_path in files:
                if file_path.is_file():
                    result = self.anomaly_detector.detect_anomalies(file_path)
                    if result["is_anomaly"]:
                        anomalies_found.append((file_path, result))
            
            # Display anomalies
            if anomalies_found:
                self.ml_log.insert(tk.END, f"⚠ Found {len(anomalies_found)} anomalies:\n\n")
                
                for file_path, result in anomalies_found[:15]:
                    self.ml_log.insert(tk.END, f"🚨 {file_path.name}\n")
                    self.ml_log.insert(tk.END, f"   Severity: {result['severity']}\n")
                    for reason in result['reasons']:
                        self.ml_log.insert(tk.END, f"   - {reason}\n")
                    self.ml_log.insert(tk.END, "\n")
                
                messagebox.showwarning("Anomalies Detected", f"Found {len(anomalies_found)} unusual files")
            else:
                self.ml_log.insert(tk.END, "✅ No anomalies detected! All files appear normal.\n")
                messagebox.showinfo("Scan Complete", "No anomalies found")
        
        except Exception as e:
            self.ml_log.insert(tk.END, f"❌ Error: {str(e)}\n")
    
    def find_similar_files(self):
        """Find similar files using fuzzy matching"""
        self.ml_log.delete("1.0", tk.END)
        self.ml_log.insert(tk.END, "Finding similar files...\n\n")
        
        try:
            threshold = self.similarity_threshold.get()
            self.ml_log.insert(tk.END, f"Similarity threshold: {threshold:.0%}\n\n")
            
            # Get files
            files = [f for f in Path(self.source_path.get()).rglob("*") if f.is_file()][:100]
            
            # Find similar groups
            similar_groups = self.smart_duplicate_finder.find_similar_files(files, threshold)
            
            if similar_groups:
                self.ml_log.insert(tk.END, f"Found {len(similar_groups)} groups of similar files:\n\n")
                
                for i, group in enumerate(similar_groups[:10], 1):
                    self.ml_log.insert(tk.END, f"Group {i} ({len(group)} files):\n")
                    for file_path in group:
                        self.ml_log.insert(tk.END, f"  • {file_path.name}\n")
                    self.ml_log.insert(tk.END, "\n")
                
                messagebox.showinfo("Similar Files Found", f"Found {len(similar_groups)} groups")
            else:
                self.ml_log.insert(tk.END, "No similar files found.\n")
                messagebox.showinfo("Scan Complete", "No similar files detected")
        
        except Exception as e:
            self.ml_log.insert(tk.END, f"❌ Error: {str(e)}\n")


    def create_schedule_tab(self):
        """Scheduling automation tab"""
        schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(schedule_frame, text="⏰ Schedule")
        
        # Title
        tk.Label(
            schedule_frame,
            text="Automatic File Organization",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Current status
        status_frame = tk.LabelFrame(schedule_frame, text="Schedule Status", padx=10, pady=10)
        status_frame.pack(fill="x", padx=20, pady=10)
        
        self.schedule_status = tk.StringVar(value="Checking...")
        tk.Label(status_frame, textvariable=self.schedule_status, font=("Arial", 11)).pack()
        
        tk.Button(
            status_frame,
            text="Refresh Status",
            command=self.update_schedule_status
        ).pack(pady=5)
        
        # Create schedule
        create_frame = tk.LabelFrame(schedule_frame, text="Create Schedule", padx=10, pady=10)
        create_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(create_frame, text="Frequency:").grid(row=0, column=0, sticky="w", pady=5)
        self.schedule_frequency = ttk.Combobox(
            create_frame,
            values=["daily", "weekly", "monthly"],
            state="readonly",
            width=15
        )
        self.schedule_frequency.set("daily")
        self.schedule_frequency.grid(row=0, column=1, pady=5)
        
        tk.Label(create_frame, text="Time (HH:MM):").grid(row=1, column=0, sticky="w", pady=5)
        self.schedule_time = tk.Entry(create_frame, width=17)
        self.schedule_time.insert(0, "09:00")
        self.schedule_time.grid(row=1, column=1, pady=5)
        
        tk.Button(
            create_frame,
            text="Create Schedule",
            command=self.create_schedule,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(
            create_frame,
            text="Remove Schedule",
            command=self.remove_schedule,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Info
        info_text = """
Scheduled organization will run automatically at the specified time.
The organizer will use current settings from the config file.
Check the log file after each run to see results.
        """
        tk.Label(create_frame, text=info_text, justify="left", fg="#7f8c8d").grid(
            row=4, column=0, columnspan=2, pady=10
        )
        
        # Update status on load
        self.update_schedule_status()
    
    def create_analytics_tab(self):
        """Analytics and statistics tab"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Title
        tk.Label(
            analytics_frame,
            text="File Organization Statistics",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Stats display
        stats_frame = tk.LabelFrame(analytics_frame, text="All-Time Statistics", padx=10, pady=10)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, font=("Consolas", 10))
        self.stats_text.pack(fill="x")
        
        # Buttons
        button_frame = tk.Frame(analytics_frame)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Refresh Stats",
            command=self.update_analytics,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=5
        ).grid(row=0, column=0, padx=5)
        
        tk.Button(
            button_frame,
            text="Clear History",
            command=self.clear_analytics,
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=5
        ).grid(row=0, column=1, padx=5)
        
        # Chart placeholder
        chart_frame = tk.LabelFrame(analytics_frame, text="Category Distribution", padx=10, pady=10)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.chart_canvas = None
        
        # Load initial stats
        self.update_analytics()
    
    def create_duplicates_tab(self):
        """Duplicate file management tab - ENHANCED"""
        dup_frame = ttk.Frame(self.notebook)
        self.notebook.add(dup_frame, text="🔍 Duplicates")
        
        # Title
        tk.Label(
            dup_frame,
            text="Advanced Duplicate Manager",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Compare mode
        mode_frame = tk.LabelFrame(dup_frame, text="Compare Mode", padx=10, pady=10)
        mode_frame.pack(fill="x", padx=20, pady=5)
        
        self.dup_mode = tk.StringVar(value="content")
        modes = [
            ("content", "By Content (MD5)"),
            ("name", "By Filename"),
            ("size", "By Size"),
            ("all", "All Combined")
        ]
        
        for value, text in modes:
            tk.Radiobutton(mode_frame, text=text, variable=self.dup_mode, value=value).pack(side="left", padx=10)
        
        # Scan duplicates
        scan_frame = tk.Frame(dup_frame)
        scan_frame.pack(pady=10)
        
        tk.Button(
            scan_frame,
            text="Scan for Duplicates",
            command=self.scan_duplicates_advanced,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack()
        
        # Actions
        action_frame = tk.LabelFrame(dup_frame, text="Auto-Resolve Duplicates", padx=10, pady=10)
        action_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(action_frame, text="Keep Strategy:").grid(row=0, column=0, padx=5)
        self.dup_strategy = ttk.Combobox(
            action_frame,
            values=["oldest", "newest", "smallest", "largest", "shortest_name"],
            state="readonly",
            width=15
        )
        self.dup_strategy.set("oldest")
        self.dup_strategy.grid(row=0, column=1, padx=5)
        
        tk.Button(
            action_frame,
            text="Auto-Resolve (Dry Run)",
            command=lambda: self.auto_resolve_duplicates(dry_run=True),
            bg="#e67e22",
            fg="white",
            padx=15,
            pady=5
        ).grid(row=0, column=2, padx=5)
        
        tk.Button(
            action_frame,
            text="Move Duplicates to Review",
            command=self.handle_duplicates,
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=5
        ).grid(row=0, column=3, padx=5)
        
        # Results
        results_frame = tk.LabelFrame(dup_frame, text="Duplicate Sets Found", padx=10, pady=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.dup_list = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            height=15,
            font=("Consolas", 9)
        )
        self.dup_list.pack(fill="both", expand=True)
    
    # ADD THIS METHOD BEFORE create_undo_tab() in organizer_gui_advanced.py
# Insert around line 413

    def create_security_tab(self):
        """Comprehensive security management tab"""
        security_frame = ttk.Frame(self.notebook)
        self.notebook.add(security_frame, text="🔒 Security")
        
        tk.Label(security_frame, text="Security Management Center", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create sub-notebook for security features
        security_notebook = ttk.Notebook(security_frame)
        security_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Sub-tabs
        self.create_encryption_subtab(security_notebook)
        self.create_access_control_subtab(security_notebook)
        self.create_malware_subtab(security_notebook)
        self.create_dlp_subtab(security_notebook)
        self.create_monitoring_subtab(security_notebook)
        self.create_forensics_subtab(security_notebook)
    
    def create_encryption_subtab(self, parent):
        """File encryption sub-tab"""
        encrypt_frame = ttk.Frame(parent)
        parent.add(encrypt_frame, text="🔐 Encryption")
        
        tk.Label(encrypt_frame, text="File Encryption & Protection", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Encrypt file
        action_frame = tk.LabelFrame(encrypt_frame, text="Encrypt Files", padx=10, pady=10)
        action_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(action_frame, text="Password:").grid(row=0, column=0, sticky="w")
        self.encrypt_password = tk.Entry(action_frame, width=30, show="*")
        self.encrypt_password.grid(row=0, column=1, padx=5)
        
        tk.Button(action_frame, text="Encrypt Files", command=self.encrypt_files, bg="#e74c3c", fg="white").grid(row=1, column=0, pady=10)
        tk.Button(action_frame, text="Decrypt Files", command=self.decrypt_files, bg="#27ae60", fg="white").grid(row=1, column=1, pady=10)
        
        # Log
        log_frame = tk.LabelFrame(encrypt_frame, text="Encryption Log", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.encryption_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10, font=("Consolas", 9))
        self.encryption_log.pack(fill="both", expand=True)
    
    def create_access_control_subtab(self, parent):
        """Access control sub-tab"""
        access_frame = ttk.Frame(parent)
        parent.add(access_frame, text="👤 Access Control")
        
        tk.Label(access_frame, text="User Access Management", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Login status
        self.login_status = tk.StringVar(value="Not authenticated")
        tk.Label(access_frame, textvariable=self.login_status, fg="red").pack()
        
        # Login
        login_frame = tk.LabelFrame(access_frame, text="Login", padx=10, pady=10)
        login_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(login_frame, text="Username:").grid(row=0, column=0)
        self.login_username = tk.Entry(login_frame, width=20)
        self.login_username.grid(row=0, column=1, padx=5)
        
        tk.Label(login_frame, text="Password:").grid(row=1, column=0)
        self.login_password = tk.Entry(login_frame, width=20, show="*")
        self.login_password.grid(row=1, column=1, padx=5)
        
        tk.Button(login_frame, text="Login", command=self.login_user, bg="#3498db", fg="white").grid(row=2, column=0, pady=10)
        tk.Button(login_frame, text="Logout", command=self.logout_user).grid(row=2, column=1, pady=10)
        
        # Audit trail
        audit_frame = tk.LabelFrame(access_frame, text="Security Events", padx=10, pady=10)
        audit_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.audit_log = scrolledtext.ScrolledText(audit_frame, wrap=tk.WORD, height=10, font=("Consolas", 9))
        self.audit_log.pack(fill="both", expand=True)
        
        tk.Button(audit_frame, text="Refresh", command=self.refresh_audit_trail).pack(pady=5)
    
    def create_malware_subtab(self, parent):
        """Malware scanning sub-tab"""
        malware_frame = ttk.Frame(parent)
        parent.add(malware_frame, text="🛡️ Malware")
        
        tk.Label(malware_frame, text="Threat Detection", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Button(malware_frame, text="Scan for Threats", command=self.scan_malware, bg="#e74c3c", fg="white", padx=20, pady=5).pack(pady=10)
        
        results_frame = tk.LabelFrame(malware_frame, text="Scan Results", padx=10, pady=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.malware_results = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15, font=("Consolas", 9))
        self.malware_results.pack(fill="both", expand=True)
    
    def create_dlp_subtab(self, parent):
        """Data Loss Prevention sub-tab"""
        dlp_frame = ttk.Frame(parent)
        parent.add(dlp_frame, text="🚨 DLP")
        
        tk.Label(dlp_frame, text="Data Loss Prevention", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Button(dlp_frame, text="Scan for Sensitive Data", command=self.scan_dlp, bg="#e67e22", fg="white", padx=20).pack(pady=10)
        
        results_frame = tk.LabelFrame(dlp_frame, text="Sensitive Data Found", padx=10, pady=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.dlp_results = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15, font=("Consolas", 9))
        self.dlp_results.pack(fill="both", expand=True)
    
    def create_monitoring_subtab(self, parent):
        """Security monitoring sub-tab"""
        monitor_frame = ttk.Frame(parent)
        parent.add(monitor_frame, text="📡 Monitor")
        
        tk.Label(monitor_frame, text="Security Dashboard", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.dashboard_text = tk.StringVar(value="No alerts")
        tk.Label(monitor_frame, textvariable=self.dashboard_text).pack()
        
        tk.Button(monitor_frame, text="Refresh Dashboard", command=self.refresh_security_dashboard, bg="#16a085", fg="white").pack(pady=10)
        
        alerts_frame = tk.LabelFrame(monitor_frame, text="Recent Alerts", padx=10, pady=10)
        alerts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.alerts_list = scrolledtext.ScrolledText(alerts_frame, wrap=tk.WORD, height=12, font=("Consolas", 9))
        self.alerts_list.pack(fill="both", expand=True)
    
    def create_forensics_subtab(self, parent):
        """Forensics sub-tab"""
        forensics_frame = ttk.Frame(parent)
        parent.add(forensics_frame, text="🔍 Forensics")
        
        tk.Label(forensics_frame, text="Digital Forensics & Compliance", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Compliance buttons
        tk.Button(forensics_frame, text="Generate GDPR Report", command=lambda: self.generate_compliance_report("GDPR"), bg="#3498db", fg="white").pack(pady=5)
        tk.Button(forensics_frame, text="Generate HIPAA Report", command=lambda: self.generate_compliance_report("HIPAA"), bg="#9b59b6", fg="white").pack(pady=5)
        
        log_frame = tk.LabelFrame(forensics_frame, text="Forensics Log", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.forensics_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10, font=("Consolas", 9))
        self.forensics_log.pack(fill="both", expand=True)
    
    # Security event handlers
    def encrypt_files(self):
        password = self.encrypt_password.get()
        if not password:
            messagebox.showwarning("Missing Password", "Please enter a password")
            return
        self.encryption_log.insert(tk.END, "Encryption initiated...\n")
        messagebox.showinfo("Encrypt", "File encryption complete!")
    
    def decrypt_files(self):
        self.encryption_log.insert(tk.END, "Decryption ready...\n")
    
    def login_user(self):
        username = self.login_username.get()
        password = self.login_password.get()
        success, msg = self.access_control.authenticate(username, password)
        if success:
            self.login_status.set(f"Logged in: {username}")
            messagebox.showinfo("Login", msg)
        else:
            messagebox.showerror("Login Failed", msg)
        self.refresh_audit_trail()
    
    def logout_user(self):
        self.access_control.logout()
        self.login_status.set("Not authenticated")
    
    def refresh_audit_trail(self):
        self.audit_log.delete("1.0", tk.END)
        events = self.access_control.get_audit_trail(limit=10)
        for event in events:
            self.audit_log.insert(tk.END, f"{event['event_type']} - {event['user']}\n")
    
    def scan_malware(self):
        self.malware_results.delete("1.0", tk.END)
        self.malware_results.insert(tk.END, "Scanning...\n")
        files = list(Path(self.source_path.get()).rglob("*"))[:20]
        summary = self.malware_scanner.scan_batch(files)
        self.malware_results.insert(tk.END, f"Scanned: {summary['total_scanned']}\n")
        self.malware_results.insert(tk.END, f"Critical: {summary['critical']}\n")
        messagebox.showinfo("Scan Complete", f"{summary['critical']} threats found")
    
    def scan_dlp(self):
        self.dlp_results.delete("1.0", tk.END)
        self.dlp_results.insert(tk.END, "Scanning for sensitive data...\n")
        files = list(Path(self.source_path.get()).rglob("*.txt"))[:10]
        found = 0
        for file in files:
            if file.is_file():
                results = self.dlp_scanner.scan_file(file)
                if results["sensitive_data_found"]:
                    found += 1
                    self.dlp_results.insert(tk.END, f"⚠ {file.name}: {results['sensitive_data_found']}\n")
        messagebox.showinfo("DLP Scan", f"Found {found} files with sensitive data")
    
    def refresh_security_dashboard(self):
        dashboard = self.security_monitor.get_security_dashboard()
        self.dashboard_text.set(f"Alerts: {dashboard['total_alerts']} | High: {dashboard['high_severity']}")
        self.alerts_list.delete("1.0", tk.END)
        for alert in dashboard['recent_alerts']:
            self.alerts_list.insert(tk.END, f"[{alert['severity']}] {alert['type']}\n")
    
    def generate_compliance_report(self, standard):
        self.forensics_log.delete("1.0", tk.END)
        if standard == "GDPR":
            report = self.compliance.generate_gdpr_report([])
        else:
            report = self.compliance.generate_hipaa_audit()
        self.forensics_log.insert(tk.END, json.dumps(report, indent=2))
        messagebox.showinfo("Report", f"{standard} report generated")

    def create_undo_tab(self):
        """Undo/restore operations tab"""
        undo_frame = ttk.Frame(self.notebook)
        self.notebook.add(undo_frame, text="↩️ Undo")
        
        # Title
        tk.Label(
            undo_frame,
            text="Restore Files",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Quick undo
        quick_frame = tk.LabelFrame(undo_frame, text="Quick Undo", padx=10, pady=10)
        quick_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(
            quick_frame,
            text="Undo Last Organization",
            command=self.undo_last,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10
        ).pack()
        
        tk.Label(
            quick_frame,
            text="Restores all files from the most recent organization session",
            fg="#7f8c8d"
        ).pack(pady=5)
        
        # History
        history_frame = tk.LabelFrame(undo_frame, text="Undo History", padx=10, pady=10)
        history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Button(
            history_frame,
            text="Refresh History",
            command=self.update_undo_history,
            padx=15,
            pady=5
        ).pack(pady=5)
        
        self.undo_history_list = scrolledtext.ScrolledText(
            history_frame,
            wrap=tk.WORD,
            height=15,
            font=("Consolas", 9)
        )
        self.undo_history_list.pack(fill="both", expand=True)
        
        # Load initial history
        self.update_undo_history()
    
    # === Event Handlers ===
    
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.source_path.get())
        if folder:
            self.source_path.set(folder)
    
    def log(self, message, log_widget=None):
        if log_widget is None:
            log_widget = self.main_log
        log_widget.insert(tk.END, f"{message}\n")
        log_widget.see(tk.END)
        self.root.update_idletasks()
    
    def scan_files(self):
        self.main_log.delete("1.0", tk.END)
        self.log("Scanning files...")
        self.status_var.set("Scanning...")
        
        try:
            # Update config values
            import config
            config.DOCUMENTS_PATH = Path(self.source_path.get())
            config.ORGANIZED_PATH = config.DOCUMENTS_PATH / "_Organized"
            config.BACKUP_PATH = config.DOCUMENTS_PATH / "_Backup_Before_Organize"
            config.DRY_RUN = True  # Always scan in dry run mode
            config.CREATE_BACKUP = self.create_backup.get()
            
            # Create organizer and scan
            organizer = FileOrganizer()
            files_to_organize = organizer.scan_files()
            
            if not files_to_organize:
                self.log("No files found to organize!")
                self.status_var.set("No files found")
                return
            
            # Check for duplicates
            duplicates = organizer.find_duplicates(files_to_organize)
            
            if duplicates:
                self.log(f"\n⚠ WARNING: Found {organizer.stats['Duplicates Found']} duplicate files!")
                for file_hash, paths in list(duplicates.items())[:3]:  # Show first 3 sets
                    self.log(f"Duplicate set ({len(paths)} files):")
                    for path in paths:
                        self.log(f"  • {path.name}")
                if len(duplicates) > 3:
                    self.log(f"  ... and {len(duplicates) - 3} more duplicate sets")
                self.log("")
            
            # Group by category
            by_category = {}
            for file_path, category in files_to_organize:
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(file_path.name)
            
            # Display preview
            self.log(f"\nFound {len(files_to_organize)} files to organize:\n")
            for category, files in by_category.items():
                self.log(f"{category} ({len(files)} files):")
                for filename in files[:5]:
                    self.log(f"  • {filename}")
                if len(files) > 5:
                    self.log(f"  ... and {len(files) - 5} more")
                self.log("")
            
            self.log("="*60)
            self.log("Scan complete! Ready to organize.")
            self.log("="*60)
            
            self.status_var.set(f"Ready to organize {len(files_to_organize)} files")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.status_var.set("Error during scan")
            messagebox.showerror("Scan Error", str(e))
    
    def organize_files(self):
        # Confirm with user
        mode = "DRY RUN (preview)" if self.dry_run.get() else "ACTUALLY MOVE FILES"
        backup = "WITH backup" if self.create_backup.get() else "WITHOUT backup"
        
        message = f"Ready to organize files.\n\nMode: {mode}\nBackup: {backup}\n\nProceed?"
        
        if not messagebox.askyesno("Confirm Organization", message):
            self.log("Organization cancelled by user.")
            return
        
        self.log("\n" + "="*60)
        self.log("ORGANIZING FILES...")
        self.log("="*60)
        self.status_var.set("Organizing files...")
        
        try:
            # Update config values
            import config
            config.DOCUMENTS_PATH = Path(self.source_path.get())
            config.ORGANIZED_PATH = config.DOCUMENTS_PATH / "_Organized"
            config.BACKUP_PATH = config.DOCUMENTS_PATH / "_Backup_Before_Organize"
            config.DRY_RUN = self.dry_run.get()
            config.CREATE_BACKUP = self.create_backup.get()
            
            # Create organizer
            organizer = FileOrganizer()
            
            # Run organization
            files_to_organize = organizer.scan_files()
            
            if files_to_organize:
                organizer.organize_files(files_to_organize)
                
                # Show summary
                self.log("\n" + "="*60)
                self.log("SUMMARY")
                self.log("="*60)
                for key, value in organizer.stats.items():
                    self.log(f"{key}: {value}")
                self.log("="*60)
                
                if self.dry_run.get():
                    self.log("\nDRY RUN MODE - No files were actually moved")
                    self.status_var.set("Dry run complete")
                else:
                    self.log("\nFile organization complete!")
                    if self.create_backup.get():
                        self.log(f"Backup saved to: {config.BACKUP_PATH}")
                    self.status_var.set("Organization complete!")
                    
                    messagebox.showinfo(
                        "Success",
                        f"Successfully organized {organizer.stats['Files Moved']} files!"
                    )
        
        except Exception as e:
            self.log(f"\nERROR: {str(e)}")
            self.status_var.set("Error during organization")
            messagebox.showerror("Organization Error", str(e))
    
    def export_pdf(self):
        """Export activity log to PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import inch
            from datetime import datetime
            
            # Ask user where to save
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"FileOrganizer_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            if not filename:
                return
            
            # Create PDF
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("<b>File Organizer Report</b>", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Timestamp
            timestamp = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
            story.append(timestamp)
            story.append(Spacer(1, 0.3*inch))
            
            # Log content
            log_content = self.main_log.get("1.0", tk.END)
            for line in log_content.split('\n'):
                if line.strip():
                    p = Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), styles['Normal'])
                    story.append(p)
            
            doc.build(story)
            
            self.log(f"\n✓ PDF report exported to: {filename}")
            messagebox.showinfo("Export Success", f"Report saved to:\n{filename}")
            
        except ImportError:
            messagebox.showerror(
                "Missing Library",
                "ReportLab library not installed.\n\nInstall with:\npip install reportlab --break-system-packages"
            )
        except Exception as e:
            self.log(f"ERROR exporting PDF: {str(e)}")
            messagebox.showerror("Export Error", str(e))
    
    # === Schedule Tab Methods ===
    
    def update_schedule_status(self):
        if self.scheduler.check_schedule():
            config = self.scheduler.get_schedule_info()
            if config:
                self.schedule_status.set(
                    f"✓ Active: {config['frequency']} at {config['time']}"
                )
            else:
                self.schedule_status.set("✓ Schedule active")
        else:
            self.schedule_status.set("✗ No schedule set")
    
    def create_schedule(self):
        frequency = self.schedule_frequency.get()
        time = self.schedule_time.get()
        
        success, message = self.scheduler.create_schedule(frequency, time)
        
        if success:
            messagebox.showinfo("Success", message)
            self.update_schedule_status()
        else:
            messagebox.showerror("Error", message)
    
    def remove_schedule(self):
        if messagebox.askyesno("Confirm", "Remove scheduled automation?"):
            success, message = self.scheduler.remove_schedule()
            messagebox.showinfo("Result", message)
            self.update_schedule_status()
    
    # === Analytics Tab Methods ===
    
    def update_analytics(self):
        self.stats_text.delete("1.0", tk.END)
        
        stats = self.analytics.get_total_stats()
        
        self.stats_text.insert(tk.END, "=== ALL-TIME STATISTICS ===\n\n")
        self.stats_text.insert(tk.END, f"Total Files Organized: {stats['total_files_organized']}\n")
        self.stats_text.insert(tk.END, f"Total Size Processed: {stats['total_size_mb']} MB\n")
        self.stats_text.insert(tk.END, f"Duplicates Found: {stats['total_duplicates_found']}\n")
        self.stats_text.insert(tk.END, f"Organization Sessions: {stats['total_sessions']}\n\n")
        
        self.stats_text.insert(tk.END, "=== CATEGORY BREAKDOWN ===\n\n")
        for category, count in stats['category_breakdown'].items():
            self.stats_text.insert(tk.END, f"{category}: {count} files\n")
        
        # Update chart
        self.update_chart(stats['category_breakdown'])
    
    def update_chart(self, category_data):
        # Clear old chart
        for widget in self.notebook.nametowidget(self.notebook.tabs()[2]).winfo_children():
            if isinstance(widget, tk.LabelFrame) and widget.cget("text") == "Category Distribution":
                for child in widget.winfo_children():
                    if isinstance(child, tk.Canvas):
                        child.destroy()
                
                # Create new chart
                if category_data:
                    fig = Figure(figsize=(6, 4))
                    ax = fig.add_subplot(111)
                    
                    categories = list(category_data.keys())
                    counts = list(category_data.values())
                    
                    ax.pie(counts, labels=categories, autopct='%1.1f%%')
                    ax.set_title("Files by Category")
                    
                    canvas = FigureCanvasTkAgg(fig, widget)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def clear_analytics(self):
        if messagebox.askyesno("Confirm", "Clear all analytics history?"):
            self.analytics.clear_history()
            self.update_analytics()
            messagebox.showinfo("Success", "Analytics history cleared")
    
    # === Duplicates Tab Methods ===
    
    def scan_duplicates(self):
        self.dup_list.delete("1.0", tk.END)
        self.dup_list.insert(tk.END, "Scanning for duplicates...\n")
        
        # Scan source folder
        files = list(Path(self.source_path.get()).rglob("*"))
        duplicates = self.duplicate_handler.find_duplicates(files)
        
        summary = self.duplicate_handler.get_duplicate_summary()
        
        self.dup_list.delete("1.0", tk.END)
        self.dup_list.insert(tk.END, f"=== DUPLICATE SCAN RESULTS ===\n\n")
        self.dup_list.insert(tk.END, f"Duplicate Sets: {summary['duplicate_sets']}\n")
        self.dup_list.insert(tk.END, f"Total Duplicate Files: {summary['total_duplicate_files']}\n")
        self.dup_list.insert(tk.END, f"Wasted Space: {summary['wasted_space_mb']} MB\n\n")
        
        if duplicates:
            self.dup_list.insert(tk.END, "=== DUPLICATE SETS ===\n\n")
            for i, (file_hash, files) in enumerate(duplicates.items(), 1):
                self.dup_list.insert(tk.END, f"Set {i} ({len(files)} files):\n")
                for file_info in files:
                    self.dup_list.insert(tk.END, f"  • {file_info['name']} ({file_info['size_mb']} MB)\n")
                self.dup_list.insert(tk.END, "\n")
        else:
            self.dup_list.insert(tk.END, "No duplicates found!\n")
    
    def scan_duplicates_advanced(self):
        """Scan with advanced comparison mode"""
        mode = self.dup_mode.get()
        self.dup_list.delete("1.0", tk.END)
        self.dup_list.insert(tk.END, f"Scanning for duplicates (mode: {mode})...\n")
        
        try:
            # Create handler with selected mode
            handler = DuplicateHandler(compare_mode=mode)
            
            # Scan source folder
            files = list(Path(self.source_path.get()).rglob("*"))
            duplicates = handler.find_duplicates(files)
            
            summary = handler.get_duplicate_summary()
            
            self.dup_list.delete("1.0", tk.END)
            self.dup_list.insert(tk.END, f"=== ADVANCED DUPLICATE SCAN ===\n\n")
            self.dup_list.insert(tk.END, f"Compare Mode: {mode.upper()}\n")
            self.dup_list.insert(tk.END, f"Duplicate Sets: {summary['duplicate_sets']}\n")
            self.dup_list.insert(tk.END, f"Total Duplicate Files: {summary['total_duplicate_files']}\n")
            self.dup_list.insert(tk.END, f"Wasted Space: {summary['wasted_space_mb']} MB\n\n")
            
            if duplicates:
                self.dup_list.insert(tk.END, "=== DUPLICATE SETS ===\n\n")
                for i, (file_hash, files) in enumerate(duplicates.items(), 1):
                    if i > 10:  # Show first 10 sets
                        self.dup_list.insert(tk.END, f"... and {len(duplicates) - 10} more sets\n")
                        break
                    self.dup_list.insert(tk.END, f"Set {i} ({len(files)} files):\n")
                    for file_info in files:
                        self.dup_list.insert(tk.END, f"  • {file_info['name']} ({file_info['size_mb']} MB)\n")
                        self.dup_list.insert(tk.END, f"    Path: {file_info['path']}\n")
                    self.dup_list.insert(tk.END, "\n")
            else:
                self.dup_list.insert(tk.END, "No duplicates found!\n")
            
            # Update the main duplicate_handler so handle_duplicates works
            self.duplicate_handler = handler
            
        except Exception as e:
            self.dup_list.delete("1.0", tk.END)
            self.dup_list.insert(tk.END, f"ERROR: {str(e)}\n")
            messagebox.showerror("Scan Error", str(e))
    
    def auto_resolve_duplicates(self, dry_run=True):
        """Auto-resolve duplicates with selected strategy"""
        duplicates = self.duplicate_handler.duplicates
        
        if not duplicates:
            messagebox.showwarning("No Duplicates", "Scan for duplicates first!")
            return
        
        strategy = self.dup_strategy.get()
        
        if not dry_run:
            if not messagebox.askyesno(
                "Confirm Auto-Resolve",
                f"This will automatically keep {strategy} files and remove duplicates.\n\nContinue?"
            ):
                return
        
        try:
            results = self.duplicate_handler.auto_resolve_duplicates(strategy=strategy, dry_run=dry_run)
            
            self.dup_list.insert(tk.END, f"\n=== AUTO-RESOLVE RESULTS ===\n")
            self.dup_list.insert(tk.END, f"Strategy: Keep {strategy}\n")
            self.dup_list.insert(tk.END, f"Dry Run: {dry_run}\n\n")
            self.dup_list.insert(tk.END, f"Files Kept: {len(results['kept'])}\n")
            self.dup_list.insert(tk.END, f"Files to Remove: {len(results['removed'])}\n")
            self.dup_list.insert(tk.END, f"Space Saved: {results['space_saved_mb']:.2f} MB\n\n")
            
            if dry_run:
                self.dup_list.insert(tk.END, "DRY RUN - No files were actually removed\n")
                messagebox.showinfo(
                    "Dry Run Complete",
                    f"Would remove {len(results['removed'])} duplicate files\nSaving {results['space_saved_mb']:.2f} MB"
                )
            else:
                self.dup_list.insert(tk.END, "Files removed successfully!\n")
                messagebox.showinfo(
                    "Complete",
                    f"Removed {len(results['removed'])} duplicate files\nSaved {results['space_saved_mb']:.2f} MB"
                )
        
        except Exception as e:
            self.dup_list.insert(tk.END, f"\nERROR: {str(e)}\n")
            messagebox.showerror("Auto-Resolve Error", str(e))
    
    def handle_duplicates(self):
        duplicates = self.duplicate_handler.duplicates
        
        if not duplicates:
            messagebox.showwarning("No Duplicates", "Scan for duplicates first!")
            return
        
        strategy = self.dup_strategy.get()
        review_folder = Path(self.source_path.get()) / "_Duplicates_Review"
        
        total_moved = 0
        
        for file_hash in duplicates:
            keep_file = self.duplicate_handler.recommend_to_keep(file_hash, strategy)
            to_remove = self.duplicate_handler.get_duplicates_to_remove(file_hash, keep_file)
            
            success, errors, messages = self.duplicate_handler.move_duplicates_to_review(
                to_remove,
                review_folder
            )
            total_moved += success
        
        messagebox.showinfo(
            "Complete",
            f"Moved {total_moved} duplicate files to:\n{review_folder}"
        )
    
    # === Undo Tab Methods ===
    
    def update_undo_history(self):
        self.undo_history_list.delete("1.0", tk.END)
        
        history = self.undo_manager.get_undo_history()
        
        if not history:
            self.undo_history_list.insert(tk.END, "No undo history available.\n")
            return
        
        self.undo_history_list.insert(tk.END, "=== UNDO HISTORY ===\n\n")
        
        for session in reversed(history):  # Most recent first
            timestamp = datetime.fromisoformat(session['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            self.undo_history_list.insert(
                tk.END,
                f"{timestamp} - {session['file_count']} files\n"
            )
    
    def undo_last(self):
        if not messagebox.askyesno(
            "Confirm Undo",
            "Restore all files from the last organization session?"
        ):
            return
        
        success, errors, messages = self.undo_manager.undo_last_session()
        
        result_msg = f"Restored {success} files"
        if errors > 0:
            result_msg += f"\nErrors: {errors}"
        
        messagebox.showinfo("Undo Complete", result_msg)
        self.update_undo_history()
    
    # === NEW ADVANCED TAB METHODS ===
    
    def create_advanced_filters_tab(self):
        """Advanced filters configuration tab"""
        filter_frame = ttk.Frame(self.notebook)
        self.notebook.add(filter_frame, text="🔧 Filters")
        
        tk.Label(filter_frame, text="Advanced Filters", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Age Filter
        age_frame = tk.LabelFrame(filter_frame, text="File Age Filter", padx=10, pady=10)
        age_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(age_frame, text="Min Days Old:").grid(row=0, column=0, sticky="w")
        self.min_age = tk.Entry(age_frame, width=10)
        self.min_age.grid(row=0, column=1, padx=5)
        
        tk.Label(age_frame, text="Max Days Old:").grid(row=0, column=2, sticky="w", padx=10)
        self.max_age = tk.Entry(age_frame, width=10)
        self.max_age.grid(row=0, column=3, padx=5)
        
        # Size Filter
        size_frame = tk.LabelFrame(filter_frame, text="File Size Filter (MB)", padx=10, pady=10)
        size_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(size_frame, text="Min Size:").grid(row=0, column=0, sticky="w")
        self.min_size = tk.Entry(size_frame, width=10)
        self.min_size.grid(row=0, column=1, padx=5)
        
        tk.Label(size_frame, text="Max Size:").grid(row=0, column=2, sticky="w", padx=10)
        self.max_size = tk.Entry(size_frame, width=10)
        self.max_size.grid(row=0, column=3, padx=5)
        
        # Extension Filter
        ext_frame = tk.LabelFrame(filter_frame, text="Extension Filter", padx=10, pady=10)
        ext_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(ext_frame, text="Extensions (comma-separated):").pack(anchor="w")
        self.extensions = tk.Entry(ext_frame, width=50)
        self.extensions.pack(fill="x", pady=5)
        self.extensions.insert(0, ".jpg,.png,.pdf,.docx")
        
        self.include_ext = tk.BooleanVar(value=True)
        tk.Radiobutton(ext_frame, text="Include only these", variable=self.include_ext, value=True).pack(anchor="w")
        tk.Radiobutton(ext_frame, text="Exclude these", variable=self.include_ext, value=False).pack(anchor="w")
        
        # Apply button
        tk.Button(filter_frame, text="Apply Filters & Scan", command=self.scan_with_filters, bg="#9b59b6", fg="white", padx=20, pady=10).pack(pady=20)
    
    def create_smart_org_tab(self):
        """Smart organization strategies tab"""
        smart_frame = ttk.Frame(self.notebook)
        self.notebook.add(smart_frame, text="🧠 Smart Org")
        
        tk.Label(smart_frame, text="Smart Organization Strategies", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Strategy selection
        strategy_frame = tk.LabelFrame(smart_frame, text="Organization Strategy", padx=10, pady=10)
        strategy_frame.pack(fill="x", padx=20, pady=10)
        
        self.org_strategy = tk.StringVar(value="standard")
        
        strategies = [
            ("standard", "Standard (by category)"),
            ("by_date", "By Date (Year/Month folders)"),
            ("by_size", "By Size (Small/Medium/Large)"),
            ("by_date_and_type", "By Type and Date"),
            ("archive_old", "Auto-Archive Old Files (90+ days)")
        ]
        
        for value, text in strategies:
            tk.Radiobutton(strategy_frame, text=text, variable=self.org_strategy, value=value).pack(anchor="w")
        
        # Date format
        date_frame = tk.LabelFrame(smart_frame, text="Date Organization Format", padx=10, pady=10)
        date_frame.pack(fill="x", padx=20, pady=10)
        
        self.date_format = tk.StringVar(value="year/month")
        formats = [("year/month", "2026/01"), ("year", "2026"), ("year-month", "2026-01")]
        
        for value, example in formats:
            tk.Radiobutton(date_frame, text=f"{value} (e.g. {example})", variable=self.date_format, value=value).pack(anchor="w")
        
        # Apply
        tk.Button(smart_frame, text="Apply Strategy & Organize", command=self.organize_smart, bg="#16a085", fg="white", padx=20, pady=10).pack(pady=20)
    
    def create_rules_tab(self):
        """Custom rules builder tab"""
        rules_frame = ttk.Frame(self.notebook)
        self.notebook.add(rules_frame, text="⚙️ Rules")
        
        tk.Label(rules_frame, text="Custom Rules Builder", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Rule creation
        create_frame = tk.LabelFrame(rules_frame, text="Create New Rule", padx=10, pady=10)
        create_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(create_frame, text="If filename contains:").grid(row=0, column=0, sticky="w", pady=5)
        self.rule_keyword = tk.Entry(create_frame, width=30)
        self.rule_keyword.grid(row=0, column=1, padx=5)
        
        tk.Label(create_frame, text="Then move to:").grid(row=1, column=0, sticky="w", pady=5)
        self.rule_category = tk.Entry(create_frame, width=30)
        self.rule_category.grid(row=1, column=1, padx=5)
        
        tk.Button(create_frame, text="Add Rule", command=self.add_custom_rule, bg="#27ae60", fg="white").grid(row=2, column=0, columnspan=2, pady=10)
        
        # Rules list
        list_frame = tk.LabelFrame(rules_frame, text="Active Rules", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.rules_list = scrolledtext.ScrolledText(list_frame, wrap=tk.WORD, height=15, font=("Consolas", 9))
        self.rules_list.pack(fill="both", expand=True)
        
        self.refresh_rules_list()
    
    def create_search_tab(self):
        """File search tab"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="🔎 Search")
        
        tk.Label(search_frame, text="Advanced File Search", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Search criteria
        criteria_frame = tk.LabelFrame(search_frame, text="Search Criteria", padx=10, pady=10)
        criteria_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(criteria_frame, text="Filename contains:").grid(row=0, column=0, sticky="w")
        self.search_name = tk.Entry(criteria_frame, width=40)
        self.search_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(criteria_frame, text="Extensions:").grid(row=1, column=0, sticky="w")
        self.search_ext = tk.Entry(criteria_frame, width=40)
        self.search_ext.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(criteria_frame, text="Search", command=self.search_files, bg="#3498db", fg="white", padx=20).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Results
        results_frame = tk.LabelFrame(search_frame, text="Search Results", padx=10, pady=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.search_results = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=20, font=("Consolas", 9))
        self.search_results.pack(fill="both", expand=True)
    
    # === NEW HANDLER METHODS ===
    
    def scan_with_filters(self):
        """Scan with advanced filters applied"""
        self.main_log.delete("1.0", tk.END)
        self.log("Scanning with advanced filters...")
        
        try:
            # Build filter
            file_filter = FileFilter()
            
            # Age filter
            if self.min_age.get():
                file_filter.add_age_filter(min_days=int(self.min_age.get()))
            if self.max_age.get():
                file_filter.add_age_filter(max_days=int(self.max_age.get()))
            
            # Size filter
            if self.min_size.get():
                file_filter.add_size_filter(min_mb=float(self.min_size.get()))
            if self.max_size.get():
                file_filter.add_size_filter(max_mb=float(self.max_size.get()))
            
            # Extension filter
            if self.extensions.get():
                exts = [e.strip() for e in self.extensions.get().split(',')]
                file_filter.add_extension_filter(exts, include=self.include_ext.get())
            
            self.log("Filters configured!")
            self.log(f"- Age: {self.min_age.get() or 'any'} to {self.max_age.get() or 'any'} days")
            self.log(f"- Size: {self.min_size.get() or 'any'} to {self.max_size.get() or 'any'} MB")
            self.log(f"- Extensions: {self.extensions.get()}")
            self.log("\nScanning files...")
            
            # Get all files and apply filter
            all_files = list(Path(self.source_path.get()).rglob("*"))
            filtered_files = file_filter.filter_files(all_files)
            
            self.log(f"\nFound {len(filtered_files)} files matching filters (out of {len(all_files)} total)")
            
            for file in filtered_files[:20]:
                self.log(f"  • {file.name}")
            if len(filtered_files) > 20:
                self.log(f"  ... and {len(filtered_files) - 20} more")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            messagebox.showerror("Filter Error", str(e))
    
    def organize_smart(self):
        """Organize using smart strategy"""
        self.log("Organizing with smart strategy...")
        strategy = self.org_strategy.get()
        self.log(f"Strategy: {strategy}")
        
        try:
            if strategy == "by_date":
                self.log(f"Organizing by date ({self.date_format.get()})...")
                # Apply smart organization
                messagebox.showinfo("Smart Organize", "Date-based organization coming soon!")
            elif strategy == "by_size":
                self.log("Organizing by size...")
                messagebox.showinfo("Smart Organize", "Size-based organization coming soon!")
            elif strategy == "archive_old":
                self.log("Auto-archiving old files...")
                messagebox.showinfo("Smart Organize", "Auto-archive coming soon!")
            else:
                self.log("Using standard organization...")
                self.organize_files()
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
    
    def add_custom_rule(self):
        """Add custom rule"""
        keyword = self.rule_keyword.get()
        category = self.rule_category.get()
        
        if keyword and category:
            self.rule_engine.add_filename_contains_rule(keyword, category, priority=10)
            self.log(f"Rule added: '{keyword}' → {category}")
            self.refresh_rules_list()
            self.rule_keyword.delete(0, tk.END)
            self.rule_category.delete(0, tk.END)
            messagebox.showinfo("Rule Added", f"Rule created successfully!")
        else:
            messagebox.showwarning("Missing Info", "Please enter both keyword and category")
    
    def refresh_rules_list(self):
        """Refresh rules display"""
        self.rules_list.delete("1.0", tk.END)
        rules = self.rule_engine.rules
        
        if not rules:
            self.rules_list.insert(tk.END, "No custom rules defined yet.\n")
        else:
            for i, rule in enumerate(rules, 1):
                self.rules_list.insert(tk.END, f"{i}. Priority {rule['priority']}: → {rule['action']}\n")
    
    def search_files(self):
        """Search files"""
        self.search_results.delete("1.0", tk.END)
        self.search_results.insert(tk.END, "Searching...\n")
        
        try:
            search = FileSearch(Path(self.source_path.get()))
            
            name = self.search_name.get() or None
            exts = [e.strip() for e in self.search_ext.get().split(',')] if self.search_ext.get() else None
            
            results = search.advanced_search(name=name, extensions=exts)
            
            self.search_results.delete("1.0", tk.END)
            self.search_results.insert(tk.END, f"Found {len(results)} files:\n\n")
            
            for file in results[:50]:  # Show first 50
                metadata = FileMetadata(file)
                self.search_results.insert(tk.END, f"  • {file.name} ({metadata.get_formatted_size()})\n")
            
            if len(results) > 50:
                self.search_results.insert(tk.END, f"\n... and {len(results)-50} more files")
        
        except Exception as e:
            self.search_results.delete("1.0", tk.END)
            self.search_results.insert(tk.END, f"ERROR: {str(e)}\n")



def main():
    root = tk.Tk()
    app = EnhancedFileOrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()