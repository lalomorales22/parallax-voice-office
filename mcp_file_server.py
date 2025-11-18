"""
MCP File Operations Server
Provides file CRUD operations as MCP tools
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPFileServer:
    """
    MCP server for file operations
    Provides comprehensive file and directory management tools
    """

    def __init__(self, workspace: str = "./workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True, parents=True)
        logger.info(f"File operations workspace: {self.workspace.absolute()}")

    def create_file(self, filename: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Create a new file with given content

        Args:
            filename: Name of file to create (relative to workspace)
            content: Content to write to file
            overwrite: Whether to overwrite if file exists (default: False)

        Returns:
            Result dictionary with status and file info
        """
        try:
            filepath = self.workspace / filename

            # Check if file exists
            if filepath.exists() and not overwrite:
                return {
                    "status": "error",
                    "message": f"File already exists: {filename} (use overwrite=true to replace)"
                }

            # Create parent directories
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            filepath.write_text(content)

            return {
                "status": "success",
                "operation": "create_file",
                "filepath": str(filepath.relative_to(self.workspace)),
                "size": filepath.stat().st_size,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error creating file '{filename}': {e}")
            return {"status": "error", "message": str(e)}

    def read_file(self, filename: str) -> Dict[str, Any]:
        """
        Read file contents

        Args:
            filename: Name of file to read (relative to workspace)

        Returns:
            Result dictionary with file content
        """
        try:
            filepath = self.workspace / filename

            if not filepath.exists():
                return {
                    "status": "error",
                    "message": f"File not found: {filename}"
                }

            content = filepath.read_text()

            return {
                "status": "success",
                "operation": "read_file",
                "filepath": str(filepath.relative_to(self.workspace)),
                "content": content,
                "size": filepath.stat().st_size
            }

        except Exception as e:
            logger.error(f"Error reading file '{filename}': {e}")
            return {"status": "error", "message": str(e)}

    def update_file(self, filename: str, content: str, mode: str = "replace") -> Dict[str, Any]:
        """
        Update existing file

        Args:
            filename: Name of file to update
            content: New content
            mode: Update mode - 'replace', 'append', or 'prepend'

        Returns:
            Result dictionary
        """
        try:
            filepath = self.workspace / filename

            if not filepath.exists():
                return {
                    "status": "error",
                    "message": f"File not found: {filename}"
                }

            # Create backup
            backup_path = filepath.with_suffix(filepath.suffix + '.bak')
            shutil.copy2(filepath, backup_path)

            # Update based on mode
            if mode == "append":
                current = filepath.read_text()
                filepath.write_text(current + '\n' + content)
            elif mode == "prepend":
                current = filepath.read_text()
                filepath.write_text(content + '\n' + current)
            else:  # replace
                filepath.write_text(content)

            return {
                "status": "success",
                "operation": "update_file",
                "filepath": str(filepath.relative_to(self.workspace)),
                "mode": mode,
                "backup": str(backup_path.relative_to(self.workspace)),
                "size": filepath.stat().st_size
            }

        except Exception as e:
            logger.error(f"Error updating file '{filename}': {e}")
            return {"status": "error", "message": str(e)}

    def delete_file(self, filename: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        Delete a file

        Args:
            filename: Name of file to delete
            create_backup: Whether to create backup before deletion

        Returns:
            Result dictionary
        """
        try:
            filepath = self.workspace / filename

            if not filepath.exists():
                return {
                    "status": "error",
                    "message": f"File not found: {filename}"
                }

            # Create backup if requested
            if create_backup:
                backup_dir = self.workspace / '.deleted'
                backup_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
                backup_path = backup_dir / backup_name
                shutil.copy2(filepath, backup_path)

            # Delete file
            filepath.unlink()

            return {
                "status": "success",
                "operation": "delete_file",
                "filepath": str(filepath.relative_to(self.workspace)),
                "backup_created": create_backup
            }

        except Exception as e:
            logger.error(f"Error deleting file '{filename}': {e}")
            return {"status": "error", "message": str(e)}

    def list_files(self, pattern: str = "*", recursive: bool = False, include_dirs: bool = False) -> Dict[str, Any]:
        """
        List files in workspace

        Args:
            pattern: Glob pattern to match files (e.g., '*.txt', '**/*.py')
            recursive: Whether to search recursively
            include_dirs: Whether to include directories in results

        Returns:
            Result dictionary with list of files
        """
        try:
            if recursive:
                files = list(self.workspace.rglob(pattern))
            else:
                files = list(self.workspace.glob(pattern))

            file_list = []
            for f in files:
                if f.is_file() or (include_dirs and f.is_dir()):
                    file_list.append({
                        "name": f.name,
                        "path": str(f.relative_to(self.workspace)),
                        "size": f.stat().st_size if f.is_file() else 0,
                        "is_directory": f.is_dir(),
                        "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                    })

            # Sort by path
            file_list.sort(key=lambda x: x['path'])

            return {
                "status": "success",
                "operation": "list_files",
                "pattern": pattern,
                "count": len(file_list),
                "files": file_list
            }

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return {"status": "error", "message": str(e)}

    def search_in_files(self, search_text: str, pattern: str = "**/*", case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Search for text within files

        Args:
            search_text: Text to search for
            pattern: File pattern to search in (default: all files)
            case_sensitive: Whether search should be case-sensitive

        Returns:
            Result dictionary with matches
        """
        try:
            matches = []
            search_term = search_text if case_sensitive else search_text.lower()

            for filepath in self.workspace.rglob(pattern):
                if filepath.is_file():
                    try:
                        content = filepath.read_text()
                        compare_content = content if case_sensitive else content.lower()

                        if search_term in compare_content:
                            # Find matching lines
                            lines = content.split('\n')
                            matching_lines = []

                            for i, line in enumerate(lines, 1):
                                compare_line = line if case_sensitive else line.lower()
                                if search_term in compare_line:
                                    matching_lines.append({
                                        "line_number": i,
                                        "content": line.strip()
                                    })

                            matches.append({
                                "file": str(filepath.relative_to(self.workspace)),
                                "match_count": len(matching_lines),
                                "matches": matching_lines[:10]  # Limit to first 10 matches per file
                            })

                    except (UnicodeDecodeError, PermissionError):
                        # Skip binary files or files we can't read
                        pass

            return {
                "status": "success",
                "operation": "search_in_files",
                "search_text": search_text,
                "files_found": len(matches),
                "matches": matches
            }

        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return {"status": "error", "message": str(e)}

    def copy_file(self, source: str, destination: str, overwrite: bool = False) -> Dict[str, Any]:
        """Copy a file"""
        try:
            src_path = self.workspace / source
            dst_path = self.workspace / destination

            if not src_path.exists():
                return {"status": "error", "message": f"Source not found: {source}"}

            if dst_path.exists() and not overwrite:
                return {"status": "error", "message": f"Destination exists: {destination} (use overwrite=true)"}

            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)

            return {
                "status": "success",
                "operation": "copy_file",
                "source": str(src_path.relative_to(self.workspace)),
                "destination": str(dst_path.relative_to(self.workspace))
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move/rename a file"""
        try:
            src_path = self.workspace / source
            dst_path = self.workspace / destination

            if not src_path.exists():
                return {"status": "error", "message": f"Source not found: {source}"}

            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))

            return {
                "status": "success",
                "operation": "move_file",
                "source": source,
                "destination": destination
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_directory(self, dirname: str) -> Dict[str, Any]:
        """Create a directory"""
        try:
            dirpath = self.workspace / dirname
            dirpath.mkdir(parents=True, exist_ok=True)

            return {
                "status": "success",
                "operation": "create_directory",
                "directory": str(dirpath.relative_to(self.workspace))
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def file_exists(self, filename: str) -> Dict[str, Any]:
        """Check if file or directory exists"""
        try:
            filepath = self.workspace / filename

            return {
                "status": "success",
                "operation": "file_exists",
                "path": filename,
                "exists": filepath.exists(),
                "is_file": filepath.is_file() if filepath.exists() else False,
                "is_directory": filepath.is_dir() if filepath.exists() else False
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            filepath = self.workspace / filename

            if not filepath.exists():
                return {"status": "error", "message": f"File not found: {filename}"}

            stat = filepath.stat()

            return {
                "status": "success",
                "operation": "get_file_info",
                "filename": filename,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": filepath.is_file(),
                "is_directory": filepath.is_dir(),
                "extension": filepath.suffix
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
