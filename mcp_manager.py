"""
Model Context Protocol (MCP) Server Manager
Manages lifecycle and execution of MCP servers for Parallax Voice Office
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MCPServerInfo:
    """Information about an MCP server"""
    name: str
    enabled: bool
    type: str
    description: str
    config: Dict[str, Any]
    status: str = "stopped"  # stopped, running, error
    last_used: Optional[str] = None
    error_message: Optional[str] = None


class MCPManager:
    """
    Manages MCP servers and their execution
    Provides a unified interface for tool execution
    """

    def __init__(self, config_path: str = "mcp_config.json"):
        self.config_path = Path(config_path)
        self.servers: Dict[str, MCPServerInfo] = {}
        self.server_instances: Dict[str, Any] = {}

        # Load configuration
        self.load_config()

        # Initialize enabled servers
        self.initialize_servers()

    def load_config(self):
        """Load MCP configuration from JSON file"""
        if not self.config_path.exists():
            logger.warning(f"MCP config file not found: {self.config_path}")
            self.config = {"mcpServers": {}, "global_settings": {}}
            return

        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

            # Parse server configurations
            for name, config in self.config.get('mcpServers', {}).items():
                self.servers[name] = MCPServerInfo(
                    name=name,
                    enabled=config.get('enabled', False),
                    type=config.get('type', 'internal'),
                    description=config.get('description', ''),
                    config=config
                )

            logger.info(f"Loaded {len(self.servers)} MCP server configurations")

        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            self.config = {"mcpServers": {}, "global_settings": {}}

    def initialize_servers(self):
        """Initialize all enabled MCP servers"""
        for name, server_info in self.servers.items():
            if server_info.enabled:
                try:
                    self._initialize_server(name, server_info)
                except Exception as e:
                    logger.error(f"Failed to initialize MCP server '{name}': {e}")
                    server_info.status = "error"
                    server_info.error_message = str(e)

    def _initialize_server(self, name: str, server_info: MCPServerInfo):
        """Initialize a specific MCP server"""
        if server_info.type == "internal":
            # Import and initialize internal server
            if name == "file-operations":
                from mcp_file_server import MCPFileServer
                workspace = server_info.config.get('workspace', './workspace')
                self.server_instances[name] = MCPFileServer(workspace=workspace)
                server_info.status = "running"
                logger.info(f"✅ Initialized file-operations MCP server (workspace: {workspace})")

            elif name == "web-search":
                from mcp_web_search import MCPWebSearchServer
                self.server_instances[name] = MCPWebSearchServer(
                    provider=server_info.config.get('provider', 'auto'),
                    max_results=server_info.config.get('max_results', 10),
                    cache_enabled=server_info.config.get('cache_enabled', True),
                    cache_ttl=server_info.config.get('cache_ttl_seconds', 3600)
                )
                server_info.status = "running"
                logger.info(f"✅ Initialized web-search MCP server")

            elif name == "json-parser":
                from mcp_json_parser import MCPJSONParser
                self.server_instances[name] = MCPJSONParser()
                server_info.status = "running"
                logger.info(f"✅ Initialized json-parser MCP server")

            elif name == "http-client":
                from mcp_http_client import MCPHTTPClient
                self.server_instances[name] = MCPHTTPClient(
                    timeout=server_info.config.get('timeout_seconds', 30),
                    max_retries=server_info.config.get('max_retries', 3)
                )
                server_info.status = "running"
                logger.info(f"✅ Initialized http-client MCP server")

            else:
                logger.warning(f"Unknown internal MCP server type: {name}")

        elif server_info.type == "external":
            # External servers would be started as separate processes
            logger.warning(f"External MCP servers not yet implemented: {name}")

    def execute_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on a specific MCP server

        Args:
            server_name: Name of the MCP server (e.g., 'file-operations')
            tool_name: Name of the tool to execute (e.g., 'create_file')
            parameters: Parameters to pass to the tool

        Returns:
            Result dictionary from the tool execution
        """
        # Check if server exists and is running
        if server_name not in self.servers:
            return {
                "status": "error",
                "message": f"MCP server '{server_name}' not found"
            }

        server_info = self.servers[server_name]

        if not server_info.enabled:
            return {
                "status": "error",
                "message": f"MCP server '{server_name}' is not enabled"
            }

        if server_info.status != "running":
            return {
                "status": "error",
                "message": f"MCP server '{server_name}' is not running (status: {server_info.status})"
            }

        if server_name not in self.server_instances:
            return {
                "status": "error",
                "message": f"MCP server '{server_name}' instance not found"
            }

        # Execute the tool
        try:
            server_instance = self.server_instances[server_name]

            # Update last used timestamp
            server_info.last_used = datetime.now().isoformat()

            # Call the tool method
            if hasattr(server_instance, tool_name):
                tool_method = getattr(server_instance, tool_name)
                result = tool_method(**parameters)
                return result
            else:
                return {
                    "status": "error",
                    "message": f"Tool '{tool_name}' not found on server '{server_name}'"
                }

        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}' on server '{server_name}': {e}")
            return {
                "status": "error",
                "message": f"Tool execution failed: {str(e)}"
            }

    def get_available_tools(self, server_name: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get list of available tools from MCP servers

        Args:
            server_name: Optional server name to get tools from specific server

        Returns:
            Dictionary mapping server names to list of available tools
        """
        available_tools = {}

        servers_to_check = [server_name] if server_name else self.server_instances.keys()

        for name in servers_to_check:
            if name in self.server_instances and self.servers[name].status == "running":
                server_instance = self.server_instances[name]

                # Get available methods (tools) from the server instance
                tools = [
                    method for method in dir(server_instance)
                    if not method.startswith('_') and callable(getattr(server_instance, method))
                ]
                available_tools[name] = tools

        return available_tools

    def get_server_status(self, server_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of MCP servers"""
        if server_name:
            if server_name in self.servers:
                info = self.servers[server_name]
                return {
                    "name": info.name,
                    "enabled": info.enabled,
                    "status": info.status,
                    "description": info.description,
                    "last_used": info.last_used,
                    "error": info.error_message
                }
            return {"error": f"Server '{server_name}' not found"}

        # Return status of all servers
        return {
            name: {
                "enabled": info.enabled,
                "status": info.status,
                "description": info.description,
                "last_used": info.last_used
            }
            for name, info in self.servers.items()
        }

    def shutdown(self):
        """Shutdown all MCP servers"""
        for name, server_instance in self.server_instances.items():
            try:
                if hasattr(server_instance, 'shutdown'):
                    server_instance.shutdown()
                logger.info(f"Shutdown MCP server: {name}")
            except Exception as e:
                logger.error(f"Error shutting down MCP server '{name}': {e}")

        self.server_instances.clear()

    def reload_config(self):
        """Reload configuration and reinitialize servers"""
        logger.info("Reloading MCP configuration")
        self.shutdown()
        self.servers.clear()
        self.load_config()
        self.initialize_servers()
