# Advanced Features - File Organizer v2.0

## 🎉 New Features Added!

You now have 4 powerful new modules:

1. **Scheduled Automation** (scheduler.py)
2. **File Analytics** (analytics.py)  
3. **Undo Manager** (undo_manager.py)
4. **Advanced Duplicate Handler** (duplicate_handler.py)

---

## 📥 Installation

Download these 4 new files to C:\Projects\FileOrganizer:
- scheduler.py
- analytics.py
- undo_manager.py
- duplicate_handler.py

---

## 1. ⏰ Scheduled Automation

**Automatically run file organization on a schedule!**

### Quick Start

```python
from scheduler import ScheduledOrganizer

scheduler = ScheduledOrganizer()

# Run daily at 9 AM
scheduler.create_schedule(
    frequency="daily",
    time="09:00"
)

# Check if schedule exists
if scheduler.check_schedule():
    print("Scheduler is active!")

# Remove schedule
scheduler.remove_schedule()
```

### Frequencies
- `"daily"` - Every day at specified time
- `"weekly"` - Every Monday at specified time
- `"monthly"` - First day of month at specified time

### Features
- Creates Windows Task Scheduler task
- Runs in background automatically
- Can be enabled/disabled anytime

---

## 2. 📊 File Analytics

**Track your file organization history with detailed statistics!**

### Quick Start

```python
from analytics import FileAnalytics

analytics = FileAnalytics()

# Get all-time stats
stats = analytics.get_total_stats()
print(f"Total files organized: {stats['total_files_organized']}")
print(f"Total size: {stats['total_size_mb']} MB")

# Get category breakdown
categories = analytics.get_category_distribution()
# Returns: {"School": 45.2%, "Personal": 30.1%, ...}

# Get size by category
sizes = analytics.get_size_by_category()
# Returns: {"School": 125.5 MB, "Personal": 89.3 MB, ...}

# Get recent sessions
recent = analytics.get_recent_sessions(count=5)
```

### What It Tracks
- Total files organized
- Total data size processed
- Files by category (School, Personal, etc.)
- Duplicate files found
- Organization sessions with timestamps

### Data Storage
All analytics stored in: `organization_history.json`

---

## 3. ↩️ Undo Manager

**Restore files to their original locations - complete undo capability!**

### Quick Start

```python
from undo_manager import UndoManager

undo = UndoManager()

# Undo last organization session
success, errors, messages = undo.undo_last_session()
print(f"Restored {success} files")

# Get undo history
history = undo.get_undo_history()
for session in history:
    print(f"{session['timestamp']}: {session['file_count']} files")

# Undo specific session by ID
undo.undo_session(session_id="2026-01-21T10:30:00")
```

### Features
- **Complete restore** - Files moved back to exact original locations
- **Session-based** - Undo entire organization sessions
- **Safe** - Won't overwrite existing files
- **History** - See all past operations

### How It Works
1. Every file move is recorded with source and destination
2. Operations grouped by session (timestamp)
3. Undo reverses the moves
4. Original folder structure is recreated

---

## 4. 🔍 Advanced Duplicate Handler

**Smart duplicate detection with comparison and management!**

### Quick Start

```python
from duplicate_handler import DuplicateHandler
from pathlib import Path

handler = DuplicateHandler()

# Find duplicates in a folder
files = list(Path("C:/Documents").rglob("*"))
duplicates = handler.find_duplicates(files)

# Get summary
summary = handler.get_duplicate_summary()
print(f"Found {summary['duplicate_sets']} sets of duplicates")
print(f"Wasted space: {summary['wasted_space_mb']} MB")

# Compare duplicates
for file_hash in duplicates:
    comparison = handler.compare_duplicates(file_hash)
    
    # Get recommendation
    keep_file = handler.recommend_to_keep(
        file_hash, 
        strategy="oldest"  # or "newest", "smallest", "largest"
    )
    
    # Get files to remove
    to_remove = handler.get_duplicates_to_remove(file_hash, keep_file)
    
    # Move duplicates to review folder
    handler.move_duplicates_to_review(
        to_remove,
        review_folder="C:/Documents/_Duplicates_Review"
    )
```

### Strategies for Keeping Files
- **oldest** - Keep the oldest file (by creation date)
- **newest** - Keep the most recent file
- **smallest** - Keep smallest file size
- **largest** - Keep largest file size
- **shortest_name** - Keep file with shortest filename

### Features
- **Content-based detection** - Uses MD5 hash (not just filename)
- **Side-by-side comparison** - Compare file details
- **Smart recommendations** - Suggests which duplicate to keep
- **Safe removal** - Move duplicates to review folder
- **Space savings** - Shows how much space you can recover

---

## 🔗 Integration Example

Here's how to use all features together:

```python
from scheduler import ScheduledOrganizer
from analytics import FileAnalytics
from undo_manager import UndoManager
from duplicate_handler import DuplicateHandler
from organizer import FileOrganizer

# 1. Set up scheduled automation
scheduler = ScheduledOrganizer()
scheduler.create_schedule(frequency="daily", time="09:00")

# 2. Run organization
organizer = FileOrganizer()
files_to_organize = organizer.scan_files()

# 3. Check for duplicates first
handler = DuplicateHandler()
duplicates = handler.find_duplicates([f[0] for f in files_to_organize])

if duplicates:
    print(f"Warning: Found {len(duplicates)} sets of duplicates!")
    # Handle duplicates before organizing

# 4. Organize files
organizer.organize_files(files_to_organize)

# 5. Record session for undo
undo = UndoManager()
# (Undo manager is automatically integrated in organizer.py)

# 6. Track analytics
analytics = FileAnalytics()
analytics.record_session(
    organizer.stats,
    files_organized=[(f[0], f[1], f[0].stat().st_size) for f in files_to_organize]
)

# 7. View stats
print(analytics.get_total_stats())
```

---

## 📁 Files Created by Advanced Features

- `schedule_config.json` - Scheduler configuration
- `organization_history.json` - Analytics data
- `undo_log.json` - Undo operations history
- `run_organizer_scheduled.bat` - Windows scheduler batch file

---

## 🚀 Next Steps

These modules are ready to use! You can:

1. **Test each module individually** using the Quick Start examples
2. **Integrate into your GUI** (I can help with this!)
3. **Add more features** from your list (File Renaming, Cloud Backup, etc.)

---

## 💡 Want to Add These to Your GUI?

I can create an enhanced GUI with tabs for:
- **Main** - Current organize functionality  
- **Schedule** - Set up automation
- **Analytics** - View statistics and charts
- **Duplicates** - Manage duplicate files
- **History** - Undo past operations

**Ready to integrate these into your GUI?** Let me know!

---

Built by Tyler Noble - Keiser University IT Cybersecurity
Advanced Features v2.0 - January 2026
