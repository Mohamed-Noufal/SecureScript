"""
MCP server configurations for security analysis tools.

Provides configuration and initialization for Model Context Protocol
servers used in security scanning.
"""

import os
from typing import Dict, Any
from agents.mcp import MCPServerStdio, create_static_tool_filter


def get_semgrep_server_params() -> Dict[str, Any]:
    """Get configuration parameters for Semgrep MCP server.
    
    Returns:
        Dictionary with command, args, and environment variables
    """
    env = {
        "PYTHONUNBUFFERED": "1",
    }

    return {
        "command": "uvx",
        "args": [
            "--with",
            "mcp==1.12.2",
            "--quiet",
            "semgrep-mcp==0.8.1",
        ],
        "env": env,
    }


def create_semgrep_server() -> MCPServerStdio:
    """Create and configure Semgrep MCP server instance.
    
    Returns:
        Configured MCPServerStdio instance for Semgrep scanning
    """
    params = get_semgrep_server_params()
    return MCPServerStdio(
        params=params,
        client_session_timeout_seconds=120,
        tool_filter=create_static_tool_filter(allowed_tool_names=["semgrep_scan"]),
    )
