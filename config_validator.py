#!/usr/bin/env python3
"""
Configuration Validator for Parallax Voice Office
Validates all configuration files and environment settings
"""

import os
import sys
import yaml
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validates configuration files and settings"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def validate_all(self) -> bool:
        """Run all validations"""
        logger.info("="*70)
        logger.info("Parallax Voice Office - Configuration Validator")
        logger.info("="*70)

        self.validate_processor_config()
        self.validate_mcp_config()
        self.validate_env_file()
        self.validate_task_configs()
        self.validate_directories()
        self.validate_parallax_connection()

        return self.print_results()

    def validate_processor_config(self):
        """Validate processor_config.yaml"""
        logger.info("\n[1/6] Validating processor_config.yaml...")

        config_file = Path("processor_config.yaml")
        if not config_file.exists():
            self.errors.append("processor_config.yaml not found")
            return

        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)

            # Check required sections
            if 'parallax' not in config:
                self.errors.append("Missing 'parallax' section in processor_config.yaml")
            else:
                parallax = config['parallax']

                # Check required fields
                required_fields = ['host', 'port', 'model']
                for field in required_fields:
                    if field not in parallax:
                        self.errors.append(f"Missing '{field}' in parallax configuration")

                # Validate values
                if 'host' in parallax and not parallax['host']:
                    self.warnings.append("Parallax host is empty, using default 'localhost'")

                if 'port' in parallax:
                    port = parallax['port']
                    if not isinstance(port, int) or port < 1 or port > 65535:
                        self.errors.append(f"Invalid Parallax port: {port}")

                if 'model' in parallax and not parallax['model']:
                    self.errors.append("Parallax model is not specified")
                else:
                    self.info.append(f"Using model: {parallax.get('model', 'unknown')}")

                # Check optional fields
                if 'max_workers' in parallax:
                    max_workers = parallax['max_workers']
                    if not isinstance(max_workers, int) or max_workers < 1:
                        self.warnings.append(f"Invalid max_workers: {max_workers}, should be >= 1")

                if 'timeout' in parallax:
                    timeout = parallax['timeout']
                    if not isinstance(timeout, (int, float)) or timeout < 0:
                        self.warnings.append(f"Invalid timeout: {timeout}, should be >= 0")

            logger.info("  ✓ processor_config.yaml is valid")

        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML in processor_config.yaml: {e}")
        except Exception as e:
            self.errors.append(f"Error reading processor_config.yaml: {e}")

    def validate_mcp_config(self):
        """Validate mcp_config.json"""
        logger.info("\n[2/6] Validating mcp_config.json...")

        config_file = Path("mcp_config.json")
        if not config_file.exists():
            self.warnings.append("mcp_config.json not found (MCP tools won't be available)")
            return

        try:
            with open(config_file) as f:
                config = json.load(f)

            if 'mcpServers' not in config:
                self.warnings.append("No mcpServers defined in mcp_config.json")
                return

            servers = config['mcpServers']
            server_count = len(servers)

            self.info.append(f"Found {server_count} MCP server(s) configured")

            for server_name, server_config in servers.items():
                if 'command' not in server_config:
                    self.warnings.append(f"MCP server '{server_name}' missing 'command' field")

                # Check for API keys in environment
                if 'env' in server_config:
                    for env_key in server_config['env'].keys():
                        if not os.getenv(env_key):
                            self.warnings.append(
                                f"MCP server '{server_name}' requires {env_key} environment variable"
                            )

            logger.info("  ✓ mcp_config.json is valid")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in mcp_config.json: {e}")
        except Exception as e:
            self.errors.append(f"Error reading mcp_config.json: {e}")

    def validate_env_file(self):
        """Validate .env file and environment variables"""
        logger.info("\n[3/6] Validating environment variables...")

        env_file = Path(".env")
        if not env_file.exists():
            self.warnings.append(".env file not found (using .env.example as template)")

        # Check important environment variables
        env_vars = {
            'SERPER_API_KEY': 'Web search via Serper',
            'TAVILY_API_KEY': 'Web search via Tavily',
        }

        has_search_key = False
        for var_name, description in env_vars.items():
            if os.getenv(var_name):
                self.info.append(f"✓ {var_name} is set ({description})")
                if 'API_KEY' in var_name:
                    has_search_key = True
            else:
                if var_name in ['SERPER_API_KEY', 'TAVILY_API_KEY']:
                    pass  # Don't warn if one is missing, only if both are
                else:
                    self.info.append(f"  {var_name} not set ({description})")

        if not has_search_key:
            self.warnings.append(
                "No web search API key found. Set SERPER_API_KEY or TAVILY_API_KEY for web search features"
            )

        logger.info("  ✓ Environment variables checked")

    def validate_task_configs(self):
        """Validate task configuration YAML files"""
        logger.info("\n[4/6] Validating task configurations...")

        task_config_dir = Path("task_configs")
        if not task_config_dir.exists():
            self.errors.append("task_configs directory not found")
            return

        yaml_files = list(task_config_dir.glob("*.yaml")) + list(task_config_dir.glob("*.yml"))

        if not yaml_files:
            self.warnings.append("No task configuration files found in task_configs/")
            return

        self.info.append(f"Found {len(yaml_files)} task configuration file(s)")

        for yaml_file in yaml_files:
            try:
                with open(yaml_file) as f:
                    config = yaml.safe_load(f)

                # Basic validation
                if 'type' not in config:
                    self.warnings.append(f"{yaml_file.name}: missing 'type' field")

                if 'steps' not in config:
                    self.warnings.append(f"{yaml_file.name}: missing 'steps' field")
                elif not isinstance(config['steps'], list):
                    self.errors.append(f"{yaml_file.name}: 'steps' should be a list")

            except yaml.YAMLError as e:
                self.errors.append(f"Invalid YAML in {yaml_file.name}: {e}")
            except Exception as e:
                self.errors.append(f"Error reading {yaml_file.name}: {e}")

        logger.info("  ✓ Task configurations checked")

    def validate_directories(self):
        """Validate required directories exist"""
        logger.info("\n[5/6] Validating directories...")

        required_dirs = {
            'workspace': 'File operations workspace',
            'results': 'Task results storage',
            'data': 'Database storage',
            'logs': 'Application logs',
            'task_configs': 'Task configuration files'
        }

        for dir_name, description in required_dirs.items():
            dir_path = Path(dir_name)
            if not dir_path.exists():
                self.warnings.append(f"Directory '{dir_name}' not found (will be created: {description})")
                try:
                    dir_path.mkdir(exist_ok=True)
                    self.info.append(f"  Created {dir_name}/")
                except Exception as e:
                    self.errors.append(f"Failed to create {dir_name}/: {e}")
            else:
                # Check if writable
                if not os.access(dir_path, os.W_OK):
                    self.errors.append(f"Directory '{dir_name}' is not writable")

        logger.info("  ✓ Directories checked")

    def validate_parallax_connection(self):
        """Validate Parallax connection"""
        logger.info("\n[6/6] Validating Parallax connection...")

        try:
            # Try to import and connect to Parallax
            import socket
            from pathlib import Path

            config_file = Path("processor_config.yaml")
            if not config_file.exists():
                self.warnings.append("Cannot test Parallax connection: processor_config.yaml not found")
                return

            with open(config_file) as f:
                config = yaml.safe_load(f)

            parallax_config = config.get('parallax', {})
            host = parallax_config.get('host', 'localhost')
            port = parallax_config.get('port', 50051)

            # Try to connect to Parallax
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)

            try:
                result = sock.connect_ex((host, port))
                if result == 0:
                    self.info.append(f"✓ Parallax is reachable at {host}:{port}")
                else:
                    self.warnings.append(
                        f"Cannot connect to Parallax at {host}:{port}. "
                        f"Make sure Parallax is running: 'parallax serve'"
                    )
            finally:
                sock.close()

        except ImportError:
            self.warnings.append("Cannot validate Parallax connection (dependencies not installed)")
        except Exception as e:
            self.warnings.append(f"Parallax connection check failed: {e}")

        logger.info("  ✓ Parallax connection checked")

    def print_results(self) -> bool:
        """Print validation results"""
        logger.info("\n" + "="*70)
        logger.info("Validation Results")
        logger.info("="*70)

        if self.errors:
            logger.error(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                logger.error(f"  • {error}")

        if self.warnings:
            logger.warning(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"  • {warning}")

        if self.info:
            logger.info(f"\nℹ️  INFO ({len(self.info)}):")
            for info in self.info:
                logger.info(f"  • {info}")

        logger.info("\n" + "="*70)

        if self.errors:
            logger.error("❌ Configuration validation FAILED")
            logger.error("Please fix the errors above before running the application.")
            return False
        elif self.warnings:
            logger.warning("⚠️  Configuration validation passed with warnings")
            logger.warning("The application will run, but some features may not work correctly.")
            return True
        else:
            logger.info("✅ Configuration validation PASSED")
            logger.info("All systems ready!")
            return True

def main():
    parser = argparse.ArgumentParser(
        description="Validate Parallax Voice Office configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--strict', action='store_true',
                       help='Treat warnings as errors')

    args = parser.parse_args()

    validator = ConfigValidator()
    result = validator.validate_all()

    if args.strict and validator.warnings:
        logger.error("\n--strict mode: treating warnings as errors")
        sys.exit(1)

    sys.exit(0 if result else 1)

if __name__ == '__main__':
    main()
