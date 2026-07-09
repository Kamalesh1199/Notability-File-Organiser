import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Set


# Configure console logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def build_target_mapping(hierarchy: dict, current_path: Path, mapping: Dict[str, Path]) -> Dict[str, Path]:
    """
    Recursively parses the JSON hierarchy to map unique filenames to their target folder paths.
    """
    for key, value in hierarchy.items():
        if key == "__files__":
            if isinstance(value, list):
                for filename in value:
                    mapping[filename] = current_path
        elif isinstance(value, dict):
            # It's a subfolder, recurse deeper
            build_target_mapping(value, current_path / key, mapping)
    
    return mapping


def organize_notes(parent_dump_path: str, json_path: str, target_root_path: str):
    parent_dir = Path(parent_dump_path).resolve()
    target_root = Path(target_root_path).resolve()
    json_file = Path(json_path).resolve()

    if not parent_dir.exists():
        logging.error(f"Parent directory not found: {parent_dir}")
        return
    if not json_file.exists():
        logging.error(f"JSON configuration not found: {json_file}")
        return

    # Load JSON and build mapping
    with open(json_file, 'r', encoding='utf-8') as f:
        hierarchy = json.load(f)
    
    expected_mapping: Dict[str, Path] = {}
    build_target_mapping(hierarchy, target_root, expected_mapping)
    expected_files: Set[str] = set(expected_mapping.keys())

    # Scan the dump directory for all files (ignoring directories)
    found_files: Set[str] = set()
    files_to_move = []

    for file_path in parent_dir.rglob("*"):
        if file_path.is_file():
            # Exclude hidden macOS files like .DS_Store
            if file_path.name.startswith("."):
                continue
            
            file_stem = file_path.stem
            found_files.add(file_stem)
            files_to_move.append(file_path)

    # 1. Find and log discrepancies
    missing_in_dump = expected_files - found_files
    missing_in_json = found_files - expected_files

    if missing_in_dump:
        logging.warning(f"Files defined in JSON but missing in dump folders: {', '.join(missing_in_dump)}")
    if missing_in_json:
        logging.warning(f"Files found in dump but missing from JSON configuration: {', '.join(missing_in_json)}")

    # 2. Create target directories and move files
    moved_count = 0
    for file_path in files_to_move:
        file_stem = file_path.stem
        
        # Only move if the file is defined in the JSON
        if file_stem in expected_mapping:
            destination_dir = expected_mapping[file_stem]
            destination_dir.mkdir(parents=True, exist_ok=True)
            
            destination_file = destination_dir / file_path.name
            
            # Handle potential conflicts
            if destination_file.exists():
                logging.warning(f"File already exists at destination, skipping: {destination_file}")
                continue
                
            shutil.move(str(file_path), str(destination_file))
            moved_count += 1
        else:
            # File is in dump but not in JSON (already logged above, but we leave it untouched)
            pass

    logging.info(f"Process complete. Successfully moved {moved_count} files.")


if __name__ == "__main__":
    # Update these paths to match your local environment
    PARENT_DUMP_DIR = "./Notes_Dump"      # The folder containing your pdf and ntb subfolders
    JSON_CONFIG = "./hierarchy.json"      # Path to your constants file
    ORGANIZED_OUTPUT = "./Organized_Notes" # Where the final structured folders will be created
    
    organize_notes(PARENT_DUMP_DIR, JSON_CONFIG, ORGANIZED_OUTPUT)
