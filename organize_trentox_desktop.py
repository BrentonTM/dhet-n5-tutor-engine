from pathlib import Path
import shutil

def organize_trentox_workspace():
    desktop_path = Path.home() / "Desktop"
    target_root = desktop_path / "Trentox_Tutor_Engine"
    
    # Ensure root structure exists
    target_root.mkdir(parents=True, exist_ok=True)
    (target_root / "src" / "phases").mkdir(parents=True, exist_ok=True)
    (target_root / "data" / "past_papers").mkdir(parents=True, exist_ok=True)
    (target_root / "config").mkdir(parents=True, exist_ok=True)
    (target_root / "scripts").mkdir(parents=True, exist_ok=True)
    
    keywords = ["dhet", "n5", "tutor", "engine", "past_paper", "trentox", "phase"]
    
    moved_count = 0
    skipped_count = 0
    
    print(f"[*] Scanning Desktop at: {desktop_path}\n")
    
    for item in desktop_path.iterdir():
        # Skip the target folder itself, hidden files, and git repos
        if item.name == "Trentox_Tutor_Engine" or item.name.startswith(".") or item.name == ".git":
            continue
            
        item_lower = item.name.lower()
        is_relevant = any(kw in item_lower for kw in keywords)
        
        if not is_relevant:
            continue  # Ignore unrelated desktop files (like games or personal docs)
            
        # Determine destination
        if item.is_dir():
            if "phase" in item_lower:
                destination = target_root / "src" / "phases"
            else:
                destination = target_root / "src"
        else:
            ext = item.suffix.lower()
            if ext in [".pdf", ".txt", ".csv"]:
                destination = target_root / "data" / "past_papers"
            elif ext in [".yaml", ".yml", ".env", ".json"]:
                destination = target_root / "config"
            else:
                destination = target_root / "scripts"
                
        destination.mkdir(parents=True, exist_ok=True)
        target_path = destination / item.name
        
        try:
            if not target_path.exists():
                shutil.move(str(item), str(target_path))
                print(f"[+] Moved: {item.name} -> {destination.relative_to(desktop_path)}")
                moved_count += 1
            else:
                # If it already exists, merge contents if both are directories
                if item.is_dir() and target_path.is_dir():
                    for sub_item in item.iterdir():
                        sub_target = target_path / sub_item.name
                        if not sub_target.exists():
                            shutil.move(str(sub_item), str(sub_target))
                    # Remove the now-empty source folder
                    shutil.rmtree(str(item))
                    print(f"[~] Merged existing folder contents: {item.name}")
                    moved_count += 1
                else:
                    print(f"[!] Skipped (already exists): {item.name}")
                    skipped_count += 1
        except Exception as e:
            print(f"[x] Error handling {item.name}: {e}")

    print(f"\n[Done] Successfully organized/merged: {moved_count} | Skipped: {skipped_count}")

if __name__ == "__main__":
    organize_trentox_workspace()