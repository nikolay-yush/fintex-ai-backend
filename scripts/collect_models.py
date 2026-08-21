import sys
from pathlib import Path


def collect_models():
    models_path = Path("app/features")
    collected_models_path = Path("app/shared/")

    if not models_path.exists():
        print("No models found!")
        sys.exit(1)

    if not collected_models_path.exists():
        collected_models_path.mkdir(parents=True)
        (collected_models_path / "__init__.py").touch()
        (collected_models_path / "models.py").touch()

    with open(collected_models_path / "models.py", "w") as f:
        for model in models_path.rglob("*"):
            if model.name.startswith("_") or "__pycache__" in model.parts:
                continue

            if model.name == "models.py" or model.parent.name == "models":
                import_path = ".".join(model.parts).split("app.")[-1].removesuffix(".py")
                import_statement = f"from app.{import_path} import *\n"

                f.write(import_statement)
                print(import_statement.strip()) 

                
print("Collecting models...")
collect_models()