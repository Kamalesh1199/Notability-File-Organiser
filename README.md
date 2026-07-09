# 🗂️ Notability File Organizer

A automated Python utility to seamlessly organize your chaotic dump of PDF and Notability notes into a cleanly structured, type-separated directory hierarchy based on a simple JSON configuration.

## ✨ Features

* **Type-Based Routing:** Automatically separates your files into distinct root folders based on their extension (`PDF Notes`, `Notability Notes`, and `Other Formats`).
* **Dynamic Directory Creation:** No need to manually create folders. The script parses your JSON hierarchy and builds the required directory tree on the fly.
* **Discrepancy Logging:** Cross-references your JSON map against your actual files. It logs warnings if a file defined in the JSON is missing from the dump, or if there are unmapped files sitting in the dump.
* **Safe Overwrites:** Safely unlinks and overwrites existing destination files without leaving duplicates or causing errors.
* **Visual Progress Bars:** Utilizes `tqdm` to provide beautiful, real-time terminal progress bars for both scanning and moving phases.
* **OS Friendly:** Automatically ignores hidden  and other hidden system files.

## 🛠️ Prerequisites

* **Python 3.7+**
* **tqdm** library (for progress bars)

Install the required dependency using pip:

```bash
pip install tqdm
```

## 🚀 Getting Started

### 1. Set Up Your Directory
Ensure you have the following files in your working directory:
* `organizer.py` (The main script)
* `hierarchy.json` (Your configuration file)

### 2. Configure `hierarchy.json`
Define your desired folder structure in JSON format. Use the special key `"__files__"` to assign a list of filenames (without their extensions) to a specific folder level.

**Example `hierarchy.json`:**
```json
{
  "University": {
    "__files__": ["Orientation_Details"],
    "Semester_1": {
      "__files__": ["Math_101", "Physics_101"]
    }
  },
  "Work": {
    "__files__": ["Onboarding_Checklist", "System_Architecture"],
    "Meetings": {
      "__files__": ["Client_Sync_01", "Team_Standup"]
    }
  },
  "Personal": {
    "__files__": ["Daily_Journal", "Expense_Tracker"]
  }
}
```

### 3. Update Paths
Open `organizer.py` and modify the three path variables at the bottom of the script to match your local environment:

```python
if __name__ == "__main__":
    PARENT_DUMP_DIR = "./Notes_Dump"       # Path containing all your unorganized files
    JSON_CONFIG = "./hierarchy.json"       # Path to your JSON configuration
    ORGANIZED_OUTPUT = "./Organized_Notes" # Path where the organized folders will be built
    
    organize_notes(PARENT_DUMP_DIR, JSON_CONFIG, ORGANIZED_OUTPUT)
```

### 4. Run the Script
Execute the script from your terminal:

```bash
python3 organizer.py
```

## 🔍 How It Works

1. **Initialization:** The script validates your paths and creates the dump and destination directories if they don't exist.
2. **Mapping:** It parses `hierarchy.json` and builds a complete relative path map for every unique filename defined.
3. **Scanning:** It recursively scans your `PARENT_DUMP_DIR`, skipping hidden files, and records all valid notes.
4. **Validation:** It compares the scanned files against the JSON map, logging out any discrepancies so you can update your config or find missing notes.
5. **Moving:** It iterates through the files, determines the appropriate type-folder (`PDF_Notes` or `Notability_Notes`), constructs the final path, creates necessary subdirectories, and moves the files.

## ⚠️ Important Notes
* 🚨 **CRITICAL: Unique File Names Required!** This script relies heavily on the file's base name (e.g., `Math_101`) to map it to the correct folder destination. Therefore, **every note must have a strictly unique name** across your entire dump. If you have multiple files with the exact same name, the script will overwrite them or route them incorrectly based on the JSON mapping.
* **Destructive Move:** This script uses `shutil.move()`. It will physically move files out of your dump directory. If you want to keep the originals in the dump, modify the script to use `shutil.copy2()` instead.
* **Unmapped Files:** Any files present in your dump directory that are *not* defined in `hierarchy.json` will be left untouched in the dump directory.
