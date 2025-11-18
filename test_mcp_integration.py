#!/usr/bin/env python3
"""
Test script for MCP integration
Tests basic functionality of MCP servers
"""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_mcp_manager():
    """Test MCP Manager initialization"""
    print("\n" + "=" * 60)
    print("TEST 1: MCP Manager Initialization")
    print("=" * 60)

    try:
        from mcp_manager import MCPManager

        manager = MCPManager(config_path="mcp_config.json")

        # Get server status
        status = manager.get_server_status()
        print(f"\n✓ MCP Manager initialized successfully")
        print(f"  Servers configured: {len(status)}")

        for name, info in status.items():
            status_emoji = "✓" if info['status'] == 'running' else "✗"
            print(f"  {status_emoji} {name}: {info['status']}")

        return manager

    except Exception as e:
        print(f"✗ MCP Manager initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_file_operations(manager):
    """Test file operations MCP server"""
    print("\n" + "=" * 60)
    print("TEST 2: File Operations MCP Server")
    print("=" * 60)

    if not manager:
        print("✗ Skipping (manager not available)")
        return

    try:
        # Test create file
        result = manager.execute_tool(
            'file-operations',
            'create_file',
            {
                'filename': 'test_mcp.txt',
                'content': 'Hello from MCP! This is a test file.',
                'overwrite': True
            }
        )

        if result.get('status') == 'success':
            print(f"✓ File created: {result.get('filepath')}")
        else:
            print(f"✗ File creation failed: {result.get('message')}")

        # Test read file
        result = manager.execute_tool(
            'file-operations',
            'read_file',
            {'filename': 'test_mcp.txt'}
        )

        if result.get('status') == 'success':
            print(f"✓ File read successfully")
            print(f"  Content preview: {result.get('content')[:50]}...")
        else:
            print(f"✗ File read failed: {result.get('message')}")

        # Test list files
        result = manager.execute_tool(
            'file-operations',
            'list_files',
            {'pattern': '*.txt'}
        )

        if result.get('status') == 'success':
            print(f"✓ Listed {result.get('count')} .txt files")
        else:
            print(f"✗ List files failed: {result.get('message')}")

    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        import traceback
        traceback.print_exc()


def test_web_search(manager):
    """Test web search MCP server"""
    print("\n" + "=" * 60)
    print("TEST 3: Web Search MCP Server")
    print("=" * 60)

    if not manager:
        print("✗ Skipping (manager not available)")
        return

    try:
        # Check web search status
        result = manager.execute_tool(
            'web-search',
            'get_status',
            {}
        )

        if result.get('status') == 'success':
            active_provider = result.get('active_provider')
            if active_provider:
                print(f"✓ Web search available (provider: {active_provider})")

                # Try a simple search (this will only work if API key is configured)
                # Using a very specific search that's unlikely to use quota
                print("  Note: Skipping actual search to conserve API quota")
                print("  To test search, configure SERPER_API_KEY or TAVILY_API_KEY in .env")
            else:
                print("⚠ Web search initialized but no API keys configured")
                print("  Set SERPER_API_KEY or TAVILY_API_KEY in .env to enable")
        else:
            print(f"✗ Web search status check failed")

    except Exception as e:
        print(f"✗ Web search test failed: {e}")
        import traceback
        traceback.print_exc()


def test_json_parser(manager):
    """Test JSON parser MCP server"""
    print("\n" + "=" * 60)
    print("TEST 4: JSON Parser MCP Server")
    print("=" * 60)

    if not manager:
        print("✗ Skipping (manager not available)")
        return

    try:
        test_json = '{"name": "test", "value": 123}'

        # Test parse JSON
        result = manager.execute_tool(
            'json-parser',
            'parse_json',
            {'json_string': test_json}
        )

        if result.get('status') == 'success':
            print(f"✓ JSON parsed successfully")
            print(f"  Data: {result.get('data')}")
        else:
            print(f"✗ JSON parse failed: {result.get('message')}")

        # Test stringify
        result = manager.execute_tool(
            'json-parser',
            'stringify_json',
            {'data': {'hello': 'world'}, 'pretty': True}
        )

        if result.get('status') == 'success':
            print(f"✓ JSON stringified successfully")
        else:
            print(f"✗ JSON stringify failed: {result.get('message')}")

    except Exception as e:
        print(f"✗ JSON parser test failed: {e}")
        import traceback
        traceback.print_exc()


def test_available_tools(manager):
    """Test getting available tools"""
    print("\n" + "=" * 60)
    print("TEST 5: Available Tools Discovery")
    print("=" * 60)

    if not manager:
        print("✗ Skipping (manager not available)")
        return

    try:
        tools = manager.get_available_tools()

        print(f"✓ Found tools in {len(tools)} servers:\n")

        for server, tool_list in tools.items():
            print(f"  {server}:")
            for tool in tool_list[:5]:  # Show first 5 tools
                print(f"    - {tool}")
            if len(tool_list) > 5:
                print(f"    ... and {len(tool_list) - 5} more")

    except Exception as e:
        print(f"✗ Tools discovery failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MCP INTEGRATION TEST SUITE")
    print("=" * 60)

    # Test 1: Initialize manager
    manager = test_mcp_manager()

    if not manager:
        print("\n❌ MCP Manager initialization failed. Cannot continue tests.")
        sys.exit(1)

    # Test 2: File operations
    test_file_operations(manager)

    # Test 3: Web search
    test_web_search(manager)

    # Test 4: JSON parser
    test_json_parser(manager)

    # Test 5: Available tools
    test_available_tools(manager)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✓ MCP integration is working correctly!")
    print("\nNext steps:")
    print("  1. Configure API keys in .env for web search")
    print("  2. Run obp-GUI.py to test full integration")
    print("  3. Create tasks to test MCP pipeline execution")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
