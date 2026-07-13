import json
import logging
import shutil

from pathlib import Path
from typing import Dict, Set, List
from tqdm import tqdm


# Configure logging to show timestamp and message
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


def build_relative_mapping(hierarchy: dict, current_rel_path: Path, mapping: Dict[str, Path]) -> Dict[str, Path]:
    """
    Parses the JSON hierarchy to map unique filenames to their relative target folder paths.
    """
    for key, value in hierarchy.items():
        if key == "__files__":
            if isinstance(value, list):
                for filename in value:
                    mapping[filename] = current_rel_path
        elif isinstance(value, dict):
            build_relative_mapping(value, current_rel_path / key, mapping)
    
    return mapping


def organize_notes(parent_dump_path: str, json_path: str, target_root_path: str):
    parent_dir = Path(parent_dump_path).resolve()
    target_root = Path(target_root_path).resolve()
    json_file = Path(json_path).resolve()

    logging.info("Step 1: Initializing and validating paths...")
    
    if not parent_dir.exists():
        logging.error(f"FATAL: Parent directory not found: {parent_dir}")
        return

    if not json_file.exists():
        logging.error(f"FATAL: JSON configuration not found at {json_file}")
        return

    if not target_root.exists():
        logging.info(f"Creating missing target root directory at {target_root}")
        target_root.mkdir(parents=True, exist_ok=True)

    logging.info("Step 2: Loading JSON hierarchy...")
    with open(json_file, 'r', encoding='utf-8') as f:
        hierarchy = json.load(f)
    
    expected_mapping: Dict[str, Path] = {}
    build_relative_mapping(hierarchy, Path(""), expected_mapping)
    expected_files: Set[str] = set(expected_mapping.keys())

    logging.info(f"---> Total files defined in Hierarchy (JSON): {len(expected_files)}")

    logging.info("Step 3: Scanning dump directory for files...")
    all_items = list(parent_dir.rglob("*"))
    files_to_move: List[Path] = []
    found_files: Set[str] = set()

    for file_path in tqdm(all_items, desc="Scanning Dump", unit="file"):
        if file_path.is_file():
            if file_path.name.startswith("."):
                continue # Skip hidden files
            
            found_files.add(file_path.stem)
            files_to_move.append(file_path)

    logging.info(f"---> Total valid files found in Dump: {len(files_to_move)}")

    # Discrepancy checks
    missing_in_dump = expected_files - found_files
    missing_in_json = found_files - expected_files

    if missing_in_dump:
        logging.warning(f"Missing in Dump (defined in JSON but not found): {len(missing_in_dump)} files.")
    if missing_in_json:
        logging.warning(f"Unmapped Files (in Dump but not in JSON): {len(missing_in_json)} files.")

    logging.info("Step 4: Creating type-based folders and moving files...")
    moved_count = 0

    for file_path in tqdm(files_to_move, desc="Moving Files", unit="file"):
        file_stem = file_path.stem
        file_ext = file_path.suffix.lower()
        
        if file_stem in expected_mapping:
            if file_ext == ".pdf":
                type_folder = "PDF Notes"
            elif file_ext in [".note", ".ntb"]:
                type_folder = "Notability Notes"
            else:
                type_folder = "Other Formats"

            rel_path = expected_mapping[file_stem]
            destination_dir = target_root / type_folder / rel_path
            
            if not destination_dir.exists():
                destination_dir.mkdir(parents=True, exist_ok=True)
            
            destination_file = destination_dir / file_path.name
            
            if destination_file.exists():
                destination_file.unlink()
                
            shutil.move(str(file_path), str(destination_file))
            moved_count += 1

    logging.info("Step 5: Organization complete!")
    logging.info(f"Successfully moved and organized {moved_count} files out of {len(files_to_move)} total scanned files.")


if __name__ == "__main__":
    PARENT_DUMP_DIR = "/Users/kamalesh/Documents/Notability/Dump"      
    JSON_CONFIG = "./hierarchy.json"      
    ORGANIZED_OUTPUT = "/Users/kamalesh/Documents/Notability/Organised" 
    
    organize_notes(PARENT_DUMP_DIR, JSON_CONFIG, ORGANIZED_OUTPUT)
