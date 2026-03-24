import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileTools:
    """File utility class for CRUD operations"""

    def __init__(self, base_path: str = None):
        """
        Initialize FileTools

        Args:
            base_path: Base directory path for file operations. If None, uses current working directory.
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self._ensure_base_path_exists()

    def _ensure_base_path_exists(self):
        """Ensure base path exists, create if necessary"""
        if not self.base_path.exists():
            try:
                self.base_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created base directory: {self.base_path}")
            except Exception as e:
                logger.error(f"Error creating base directory: {e}")
                raise

    def create_file(self, filename: str, content: str = "", encoding: str = 'utf-8') -> bool:
        """
        Create a new file with optional content

        Args:
            filename: Name of the file to create
            content: Initial content (optional)
            encoding: File encoding

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = self.base_path / filename

            if filepath.exists():
                logger.warning(f"File already exists: {filepath}")
                return False

            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)

            logger.info(f"Created file: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error creating file: {e}")
            return False

    def read_file(self, filename: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read content from a file

        Args:
            filename: Name of the file to read
            encoding: File encoding

        Returns:
            File content as string, or None if error
        """
        try:
            filepath = self.base_path / filename

            if not filepath.exists():
                logger.error(f"File not found: {filepath}")
                return None

            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()

            logger.info(f"Read file: {filepath}")
            return content

        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return None

    def update_file(self, filename: str, content: str, encoding: str = 'utf-8',
                    append: bool = False) -> bool:
        """
        Update file content

        Args:
            filename: Name of the file to update
            content: New content
            encoding: File encoding
            append: If True, append to file; if False, overwrite

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = self.base_path / filename

            if not filepath.exists():
                logger.error(f"File not found: {filepath}")
                return False

            mode = 'a' if append else 'w'
            with open(filepath, mode, encoding=encoding) as f:
                f.write(content)

            operation = "Appended to" if append else "Updated"
            logger.info(f"{operation} file: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error updating file: {e}")
            return False

    def delete_file(self, filename: str) -> bool:
        """
        Delete a file

        Args:
            filename: Name of the file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = self.base_path / filename

            if not filepath.exists():
                logger.error(f"File not found: {filepath}")
                return False

            os.remove(filepath)
            logger.info(f"Deleted file: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

    def list_files(self, pattern: str = "*", recursive: bool = False) -> List[Path]:
        """
        List files in the base directory

        Args:
            pattern: Glob pattern for filtering files (e.g., "*.txt")
            recursive: If True, search recursively in subdirectories

        Returns:
            List of file paths
        """
        try:
            if recursive:
                files = list(self.base_path.rglob(pattern))
            else:
                files = list(self.base_path.glob(pattern))

            # Filter only files, not directories
            files = [f for f in files if f.is_file()]

            logger.info(f"Found {len(files)} files matching pattern '{pattern}'")
            return files

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []

    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get file information/metadata

        Args:
            filename: Name of the file

        Returns:
            Dictionary with file info, or None if error
        """
        try:
            filepath = self.base_path / filename

            if not filepath.exists():
                logger.error(f"File not found: {filepath}")
                return None

            stat = filepath.stat()

            info = {
                'name': filepath.name,
                'path': str(filepath),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'accessed': datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'extension': filepath.suffix,
                'is_file': filepath.is_file(),
                'is_directory': filepath.is_dir()
            }

            return info

        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

    def create_directory(self, dirname: str) -> bool:
        """
        Create a directory

        Args:
            dirname: Name of the directory to create

        Returns:
            True if successful, False otherwise
        """
        try:
            dirpath = self.base_path / dirname
            dirpath.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dirpath}")
            return True

        except Exception as e:
            logger.error(f"Error creating directory: {e}")
            return False

    def delete_directory(self, dirname: str, force: bool = False) -> bool:
        """
        Delete a directory

        Args:
            dirname: Name of the directory to delete
            force: If True, delete even if directory is not empty

        Returns:
            True if successful, False otherwise
        """
        try:
            dirpath = self.base_path / dirname

            if not dirpath.exists():
                logger.error(f"Directory not found: {dirpath}")
                return False

            if force:
                shutil.rmtree(dirpath)
            else:
                dirpath.rmdir()

            logger.info(f"Deleted directory: {dirpath}")
            return True

        except Exception as e:
            logger.error(f"Error deleting directory: {e}")
            return False

    def copy_file(self, source_filename: str, destination_filename: str) -> bool:
        """
        Copy a file

        Args:
            source_filename: Name of the source file
            destination_filename: Name of the destination file

        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = self.base_path / source_filename
            dest_path = self.base_path / destination_filename

            if not source_path.exists():
                logger.error(f"Source file not found: {source_path}")
                return False

            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied file from {source_path} to {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Error copying file: {e}")
            return False

    def move_file(self, source_filename: str, destination_filename: str) -> bool:
        """
        Move a file

        Args:
            source_filename: Name of the source file
            destination_filename: Name of the destination file

        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = self.base_path / source_filename
            dest_path = self.base_path / destination_filename

            if not source_path.exists():
                logger.error(f"Source file not found: {source_path}")
                return False

            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Moved file from {source_path} to {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Error moving file: {e}")
            return False

    def search_files(self, keyword: str, recursive: bool = True) -> List[Path]:
        """
        Search files by keyword in filename

        Args:
            keyword: Keyword to search for
            recursive: If True, search recursively

        Returns:
            List of matching file paths
        """
        try:
            all_files = self.list_files(recursive=recursive)
            matching_files = [f for f in all_files if keyword.lower() in f.name.lower()]

            logger.info(f"Found {len(matching_files)} files matching keyword '{keyword}'")
            return matching_files

        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []

    def read_json(self, filename: str) -> Optional[Any]:
        """
        Read and parse JSON file

        Args:
            filename: Name of the JSON file

        Returns:
            Parsed JSON data, or None if error
        """
        try:
            content = self.read_file(filename)
            if content:
                data = json.loads(content)
                logger.info(f"Read JSON file: {filename}")
                return data
            return None

        except Exception as e:
            logger.error(f"Error reading JSON file: {e}")
            return None

    def write_json(self, filename: str, data: Any, indent: int = 4,
                   encoding: str = 'utf-8') -> bool:
        """
        Write data to JSON file

        Args:
            filename: Name of the JSON file
            data: Data to write
            indent: JSON indentation level
            encoding: File encoding

        Returns:
            True if successful, False otherwise
        """
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            result = self.create_file(filename, content, encoding)
            if result:
                logger.info(f"Wrote JSON file: {filename}")
            return result

        except Exception as e:
            logger.error(f"Error writing JSON file: {e}")
            return False

    def get_base_path(self) -> Path:
        """Get the base path"""
        return self.base_path

    def __str__(self):
        """String representation"""
        return f"FileTools(base_path={self.base_path})"

