import sys
import os
import subprocess
from pathlib import Path

def process_file_content(file_path: Path, mod_id: str, mod_name: str):
    """Liest eine Datei ein und ersetzt Platzhalter {{MOD_ID}} und {{MOD_NAME}}."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if "{{MOD_ID}}" in content or "{{MOD_NAME}}" in content:
            new_content = content.replace("{{MOD_ID}}", mod_id).replace("{{MOD_NAME}}", mod_name)
            file_path.write_text(new_content, encoding="utf-8")
            print(f"   - Datei angepasst: {file_path.relative_to(file_path.parents[1] if len(file_path.parents) > 1 else file_path.parent)}")
    except (UnicodeDecodeError, PermissionError):
        # Binärdateien (z.B. Grafiken, JARs) überspringen
        pass

def main():
    if len(sys.argv) < 2:
        print("Fehler: Bitte gib einen Mod-Namen an.")
        print("Nutzung: python CreateProject.py <modname>")
        sys.exit(1)

    mod_name = sys.argv[1]
    mod_id = mod_name.lower()

    repo_url = "https://github.com/klangzwang/MCNF.git"
    original_folder = Path("MCNF")
    target_folder = Path(mod_name)

    # 1. Git Clone
    print(f"1. Clonen des Repositories '{repo_url}'...")
    try:
        subprocess.run(["git", "clone", repo_url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von git clone: {e}")
        sys.exit(1)

    # 2. Ordner umbenennen
    if target_folder.exists():
        print(f"Fehler: Zielordner '{mod_name}' existiert bereits.")
        sys.exit(1)

    if not original_folder.exists():
        print("Fehler: Geclonter Ordner 'MCNF' wurde nicht gefunden.")
        sys.exit(1)

    print(f"2. Benenne Ordner 'MCNF' um in '{mod_name}'...")
    original_folder.rename(target_folder)

    # 3. Inhalte in allen Projektdateien ersetzen (Gradles, Java-Klassen, Configs)
    print("3. Ersetze Platzhalter in Dateiinhalten (Java, Resources, Gradle)...")
    for root, dirs, files in os.walk(target_folder):
        # .git Ordner vom Durchsuchen ausschließen
        if ".git" in dirs:
            dirs.remove(".git")
            
        for file in files:
            file_path = Path(root) / file
            process_file_content(file_path, mod_id, mod_name)

    # 4. Ordner- und Paketstruktur im src-Ordner anpassen
    print("4. Benenne Paket- und Ordnerstrukturen um...")
    # topdown=False durchläuft die Verzeichnisse von unten nach oben (Bottom-Up),
    # damit das Umbenennen von Unterordnern die Pfade von Elternordnern nicht unterbricht.
    for root, dirs, files in os.walk(target_folder, topdown=False):
        if ".git" in root:
            continue
            
        for dir_name in dirs:
            if "{{MOD_ID}}" in dir_name or "{{MOD_NAME}}" in dir_name:
                old_dir_path = Path(root) / dir_name
                new_dir_name = dir_name.replace("{{MOD_ID}}", mod_id).replace("{{MOD_NAME}}", mod_name)
                new_dir_path = Path(root) / new_dir_name
                
                old_dir_path.rename(new_dir_path)
                print(f"   - Ordner umbenannt: {dir_name} -> {new_dir_name}")

    print(f"\nProjekt '{mod_name}' (ID: '{mod_id}') erfolgreich erstellt und Paketstruktur angepasst!")

if __name__ == "__main__":
    main()