# Full PC Mode - Organize Your Entire Computer

## ⚠️ IMPORTANT SAFETY INFORMATION

Full PC Mode scans your ENTIRE computer and organizes files across all drives. This is powerful but requires careful setup.

---

## 🛡️ Built-in Protection

Your File Organizer will **AUTOMATICALLY SKIP** these critical directories:

### Windows System Files
- Windows/
- Program Files/
- Program Files (x86)/
- ProgramData/
- System Volume Information/
- $Recycle.Bin/

### Games (Protected Automatically)
- SteamLibrary/
- Steam/
- Epic Games/
- Origin Games/
- Battle.net/
- GOG Games/
- Riot Games/
- Xbox Games/
- WindowsApps/
- Saved Games/
- My Games/

### This AI Project (Protected!)
- FileOrganizer/ ← **Your project files are safe!**

### Cloud Storage
- OneDrive/
- Google Drive/
- Dropbox/
- iCloud Drive/

### Development Files
- node_modules/
- .git/
- venv/
- __pycache__/

### System Files (By Extension)
- .sys, .dll, .exe, .msi, .bat, .cmd, .ps1
- .ini, .cfg, .conf, .reg, .dat

---

## 📋 Setup Full PC Mode

### Step 1: Update config.py

Open `config.py` and change line 10:

```python
# Change this:
SCAN_MODE = "single_folder"

# To this:
SCAN_MODE = "full_pc"
```

### Step 2: Configure Safety Limits

In `config.py`, these safety settings protect you:

```python
MAX_FILES_FULL_PC = 10000      # Max files in one scan
MIN_FILE_SIZE_BYTES = 1024     # Skip tiny files (1 KB)
MAX_FILE_SIZE_MB = 5000        # Skip huge files (5 GB)
DRY_RUN = True                 # ALWAYS test in dry run first!
CREATE_BACKUP = True           # ALWAYS create backups!
```

### Step 3: Where Files Go

In full PC mode, organized files go to:
```
C:\OrganizedFiles\
├── School\
├── Personal\
├── Finance\
├── Documents\
├── Images\
├── Videos\
└── ... (all categories)
```

---

## 🚀 How to Use Full PC Mode

### First Run - DRY RUN (Required!)

**ALWAYS do a dry run first!**

```powershell
# Make sure DRY_RUN = True in config.py
python organizer.py
```

This will:
- Show you EVERY file it would organize
- NOT move anything
- Let you verify it's safe

### Review the Preview

Check the log carefully:
- Are any protected directories being scanned? (They shouldn't be!)
- Are game files being found? (They shouldn't be!)
- Are system files being found? (They shouldn't be!)

### If Everything Looks Safe

```python
# In config.py, change:
DRY_RUN = False
```

Then run:
```powershell
python organizer.py
```

---

## 🎯 What Gets Organized

### ✅ WILL Be Organized:
- Your personal documents
- Downloaded files
- Pictures/photos
- Videos
- Music files
- PDFs
- Spreadsheets
- Presentations
- Code files (in your personal projects)
- Archives (.zip, .rar)

### ❌ WILL NOT Be Organized:
- Windows system files
- Program files
- Game installations
- Game saves
- Your FileOrganizer project
- Cloud sync folders
- System configurations
- DLLs, EXEs, system files

---

## 🔧 Customizing Protected Directories

Want to protect additional folders? Add them to `config.py`:

```python
PROTECTED_SYSTEM_DIRS = [
    # ... (existing list)
    
    # Add your custom protections:
    "My Important Project",
    "Work Files",
    "Family Photos Archive",
]
```

---

## 📊 Full PC Mode in GUI

The Advanced GUI supports Full PC mode:

1. **Organize Tab**: Shows source as "Full PC Scan" instead of single folder
2. **Analytics**: Tracks files across entire PC
3. **Duplicates**: Finds duplicates system-wide
4. **Undo**: Can restore files from anywhere

---

## ⚙️ Advanced Settings

### Scan Multiple Drives

```python
DRIVES_TO_SCAN = ["C:\\", "D:\\", "E:\\"]
```

### Change Output Location

```python
ORGANIZED_PATH = Path(r"D:\MyOrganizedFiles")
```

### Adjust File Size Limits

```python
MIN_FILE_SIZE_BYTES = 10240    # 10 KB (skip smaller)
MAX_FILE_SIZE_MB = 1000        # 1 GB (skip larger)
```

---

## 🐛 Troubleshooting

### "Too many files found"

Increase the limit in config.py:
```python
MAX_FILES_FULL_PC = 20000
```

### "Permission denied" errors

Some system files are locked. This is normal and safe - they'll be skipped automatically.

### Want to organize specific folders only

Instead of full PC mode, add multiple paths:
```python
SCAN_MODE = "multi_folder"
FOLDERS_TO_SCAN = [
    r"C:\Users\Noble\Desktop",
    r"C:\Users\Noble\Downloads",
    r"D:\Projects"
]
```

---

## 💡 Best Practices

1. **Always dry run first** - Review what will be organized
2. **Start with backups enabled** - `CREATE_BACKUP = True`
3. **Check protected directories** - Make sure nothing critical is exposed
4. **Review the log file** - Check `organizer.log` after each run
5. **Test undo** - Make sure you can restore if needed

---

## 🔒 Safety Guarantees

The File Organizer will:
- ✅ Never touch Windows system files
- ✅ Never touch game installations
- ✅ Never touch its own files
- ✅ Always create backups (if enabled)
- ✅ Always log every operation
- ✅ Always allow undo
- ✅ Never delete files (only moves them)

---

## 📝 Example Workflow

```powershell
# 1. Enable full PC mode
# Edit config.py: SCAN_MODE = "full_pc"

# 2. Dry run to preview
python organizer.py

# 3. Review the log
notepad organizer.log

# 4. If safe, enable actual run
# Edit config.py: DRY_RUN = False

# 5. Run for real
python organizer.py

# 6. Check organized files
explorer C:\OrganizedFiles

# 7. If something's wrong, undo
python organizer_gui_advanced.py
# Click Undo tab → "Undo Last Organization"
```

---

## 🎉 Result

Your entire PC will be organized into:
```
C:\OrganizedFiles\
├── School\ (738 files, 2.4 GB)
├── Personal\ (234 files, 890 MB)
├── Finance\ (45 files, 12 MB)
├── Documents\ (1,234 files, 450 MB)
├── Images\ (5,678 files, 15 GB)
├── Videos\ (234 files, 50 GB)
├── Music\ (2,456 files, 18 GB)
└── Code\ (890 files, 234 MB)
```

All while keeping your games, Windows, and this project completely safe!

---

**Questions or Issues?**

Check:
1. `organizer.log` - Detailed operation log
2. Protected directories list in config.py
3. Undo history in GUI

**Remember: When in doubt, DRY RUN first!**

---

Built by Tyler Noble
Keiser University - IT Cybersecurity
Full PC Mode - January 2026
