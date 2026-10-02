import os
import shutil
from pathlib import Path


class FileManager:

    def __init__(self, base_directory=None):

        if base_directory is None:
            base_directory = os.getenv(
                "TASKPILOT_WORKSPACE",
                Path(__file__).resolve().parents[1]
            )
    
        self.base_directory = Path(base_directory).expanduser().resolve()

    def _safe_path(self, path):
        """
        Convert a user path into an absolute path and make sure
        it stays inside the allowed base directory.
        """

        requested_path = Path(path).expanduser()

        if not requested_path.is_absolute():
            requested_path = self.base_directory / requested_path

        resolved_path = requested_path.resolve()

        try:
            resolved_path.relative_to(self.base_directory)
        except ValueError:
            raise ValueError(
                "Access denied: path is outside the allowed directory."
            )

        return resolved_path

    def list_files(self, directory="."):
        path = self._safe_path(directory)

        if not path.exists():
            return {
                "success": False,
                "error": "Directory does not exist."
            }

        if not path.is_dir():
            return {
                "success": False,
                "error": "Path is not a directory."
            }

        files = []
        folders = []

        for item in path.iterdir():

            if item.is_file():
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "extension": item.suffix,
                    "size": item.stat().st_size
                })

            elif item.is_dir():
                folders.append({
                    "name": item.name,
                    "path": str(item)
                })

        return {
            "success": True,
            "directory": str(path),
            "files": files,
            "folders": folders
        }

    def find_files(self, pattern, directory="."):
        path = self._safe_path(directory)

        if not path.exists():
            return {
                "success": False,
                "error": "Directory does not exist."
            }

        matches = []

        for item in path.rglob(pattern):
            if item.is_file():
                matches.append({
                    "name": item.name,
                    "path": str(item),
                    "extension": item.suffix,
                    "size": item.stat().st_size
                })

        return {
            "success": True,
            "pattern": pattern,
            "matches": matches
        }

    def rename_file(self, source, new_name):
        source_path = self._safe_path(source)

        if not source_path.exists():
            return {
                "success": False,
                "error": "Source file does not exist."
            }

        if not source_path.is_file():
            return {
                "success": False,
                "error": "Source is not a file."
            }

        destination = source_path.parent / new_name
        destination = self._safe_path(destination)

        if destination.exists():
            return {
                "success": False,
                "error": "A file with that name already exists."
            }

        source_path.rename(destination)

        return {
            "success": True,
            "operation": "rename",
            "old_path": str(source_path),
            "new_path": str(destination)
        }

    def move_file(self, source, destination):
        source_path = self._safe_path(source)
        destination_path = self._safe_path(destination)

        if not source_path.exists():
            return {
                "success": False,
                "error": "Source does not exist."
            }

        if destination_path.is_dir():
            final_path = destination_path / source_path.name
        else:
            final_path = destination_path

        final_path = self._safe_path(final_path)

        if final_path.exists():
            return {
                "success": False,
                "error": "Destination already exists."
            }

        shutil.move(str(source_path), str(final_path))

        return {
            "success": True,
            "operation": "move",
            "source": str(source_path),
            "destination": str(final_path)
        }
    
    def write_file(self, filename, content):
        """Write text to a file inside the allowed base directory."""
        if not filename:
            return {
                "success": False,
                "error": "Filename is required."
            }

        path = self._safe_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(content if content is not None else ""), encoding="utf-8")

        return {
            "success": True,
            "path": str(path),
            "message": f"File saved successfully: {path.name}"
        }

if __name__ == "__main__":

    manager = FileManager()

    print("\n--- File Manager Test ---")

    result = manager.list_files(".")

    print(result)