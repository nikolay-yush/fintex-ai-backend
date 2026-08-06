import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Error occurred. Please provide a feature name!")
        print("Example: uv run task feature user_auth")
        sys.exit(1)

    feature_name = sys.argv[1].lower().replace("-", "_")
    
    base_dir = Path("app/features") / feature_name

    if base_dir.exists():
        print(f" Folder '{base_dir}' already exists!")
        sys.exit(1)

    dirs = [
        base_dir,
        base_dir / "models",
        base_dir / "schemas",
        base_dir / "repositories",
        base_dir / "services",
        base_dir / "exceptions",
    ]

    files = [
        base_dir / "router.py",
        base_dir / "dependencies.py",
        base_dir / "repositories" / "dependencies.py",
        base_dir / "services" / "dependencies.py",

    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        make_file = d / "__init__.py"

        if not make_file.exists():
            make_file.touch()

    for file_path in files:
        file_path.touch()

    print(f" Feature '{feature_name}' successfully created in {base_dir}!")

if __name__ == "__main__":
    main()