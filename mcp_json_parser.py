"""
MCP JSON/YAML Parser Server
Provides JSON and YAML parsing and manipulation tools
"""

import json
import yaml
import logging
from typing import Dict, Any, Union, List

logger = logging.getLogger(__name__)


class MCPJSONParser:
    """
    MCP server for JSON and YAML parsing and manipulation
    """

    def __init__(self):
        logger.info("JSON/YAML parser server initialized")

    def parse_json(self, json_string: str) -> Dict[str, Any]:
        """
        Parse JSON string

        Args:
            json_string: JSON string to parse

        Returns:
            Parsed JSON object or error
        """
        try:
            data = json.loads(json_string)
            return {
                "status": "success",
                "operation": "parse_json",
                "data": data,
                "type": type(data).__name__
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"JSON parse error: {str(e)}"
            }

    def stringify_json(self, data: Union[Dict, List], pretty: bool = True, indent: int = 2) -> Dict[str, Any]:
        """
        Convert Python object to JSON string

        Args:
            data: Python object to convert
            pretty: Whether to pretty-print
            indent: Indentation level (if pretty=True)

        Returns:
            JSON string
        """
        try:
            if pretty:
                json_string = json.dumps(data, indent=indent, ensure_ascii=False)
            else:
                json_string = json.dumps(data, ensure_ascii=False)

            return {
                "status": "success",
                "operation": "stringify_json",
                "json_string": json_string
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"JSON stringify error: {str(e)}"
            }

    def parse_yaml(self, yaml_string: str) -> Dict[str, Any]:
        """
        Parse YAML string

        Args:
            yaml_string: YAML string to parse

        Returns:
            Parsed YAML object or error
        """
        try:
            data = yaml.safe_load(yaml_string)
            return {
                "status": "success",
                "operation": "parse_yaml",
                "data": data,
                "type": type(data).__name__
            }
        except yaml.YAMLError as e:
            return {
                "status": "error",
                "message": f"YAML parse error: {str(e)}"
            }

    def stringify_yaml(self, data: Union[Dict, List]) -> Dict[str, Any]:
        """
        Convert Python object to YAML string

        Args:
            data: Python object to convert

        Returns:
            YAML string
        """
        try:
            yaml_string = yaml.dump(data, default_flow_style=False, allow_unicode=True)

            return {
                "status": "success",
                "operation": "stringify_yaml",
                "yaml_string": yaml_string
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"YAML stringify error: {str(e)}"
            }

    def validate_json(self, json_string: str) -> Dict[str, Any]:
        """
        Validate JSON syntax

        Args:
            json_string: JSON string to validate

        Returns:
            Validation result
        """
        try:
            json.loads(json_string)
            return {
                "status": "success",
                "operation": "validate_json",
                "valid": True,
                "message": "JSON is valid"
            }
        except json.JSONDecodeError as e:
            return {
                "status": "success",
                "operation": "validate_json",
                "valid": False,
                "error": str(e),
                "line": e.lineno,
                "column": e.colno
            }

    def json_to_yaml(self, json_string: str) -> Dict[str, Any]:
        """
        Convert JSON to YAML

        Args:
            json_string: JSON string to convert

        Returns:
            YAML string
        """
        try:
            data = json.loads(json_string)
            yaml_string = yaml.dump(data, default_flow_style=False, allow_unicode=True)

            return {
                "status": "success",
                "operation": "json_to_yaml",
                "yaml_string": yaml_string
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Conversion error: {str(e)}"
            }

    def yaml_to_json(self, yaml_string: str, pretty: bool = True) -> Dict[str, Any]:
        """
        Convert YAML to JSON

        Args:
            yaml_string: YAML string to convert
            pretty: Whether to pretty-print JSON

        Returns:
            JSON string
        """
        try:
            data = yaml.safe_load(yaml_string)
            if pretty:
                json_string = json.dumps(data, indent=2, ensure_ascii=False)
            else:
                json_string = json.dumps(data, ensure_ascii=False)

            return {
                "status": "success",
                "operation": "yaml_to_json",
                "json_string": json_string
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Conversion error: {str(e)}"
            }

    def extract_value(self, data: Union[Dict, List, str], path: str) -> Dict[str, Any]:
        """
        Extract value from JSON/YAML using path notation

        Args:
            data: Data to extract from (dict, list, or JSON string)
            path: Path to value (e.g., 'user.address.city' or 'items[0].name')

        Returns:
            Extracted value
        """
        try:
            # Parse if string
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    data = yaml.safe_load(data)

            # Navigate path
            current = data
            parts = path.replace('[', '.').replace(']', '').split('.')

            for part in parts:
                if part.isdigit():
                    current = current[int(part)]
                else:
                    current = current[part]

            return {
                "status": "success",
                "operation": "extract_value",
                "path": path,
                "value": current
            }
        except (KeyError, IndexError, TypeError) as e:
            return {
                "status": "error",
                "message": f"Path not found: {path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Extraction error: {str(e)}"
            }
