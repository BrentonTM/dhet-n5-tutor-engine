import os

DIRECTORIES = [
    "config",
    "data/dhet_curriculum",
    "data/timetables",
    "data/databases",
    "data/past_papers",
    "src/ingestion",
    "src/database",
    "src/engines",
    "src/tutor",
    "src/skills",
    "src/automation",
    "src/voice",
    "src/ui",
    "tests",
    "logs",
]


def build_folder_structure():
    print("=== Phase 2: Generating Folder Structure ===")
    created_count = 0

    for directory in DIRECTORIES:
        os.makedirs(directory, exist_ok=True)
        print(f"[CREATED] {directory}")
        created_count += 1

        if directory.startswith("src/"):
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    f.write(f"# Module initializer for {directory}\n")
                print(f"  └── Created {init_file}")

    print(f"\nFolder structure creation complete. Total folders: {created_count}")


if __name__ == "__main__":
    build_folder_structure()
