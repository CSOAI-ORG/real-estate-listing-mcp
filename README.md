<div align="center">

# Real Estate Listing MCP

**Real Estate Listing MCP Server - Property Intelligence AI**

[![PyPI](https://img.shields.io/pypi/v/meok-real-estate-listing-mcp)](https://pypi.org/project/meok-real-estate-listing-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Real Estate Listing MCP Server - Property Intelligence AI
Built by MEOK AI Labs | https://meok.ai

Property valuation, listing generation, comparable sales,
mortgage calculations, and neighborhood analysis.

## Tools

| Tool | Description |
|------|-------------|
| `estimate_valuation` | Estimate property valuation using comp-based methodology. |
| `generate_listing` | Generate a professional property listing description. |
| `find_comparable_sales` | Find comparable recent sales for pricing analysis. |
| `calculate_mortgage` | Calculate monthly mortgage payment with full breakdown. |
| `analyze_neighborhood` | Analyze neighborhood characteristics and livability scores. |

## Installation

```bash
pip install meok-real-estate-listing-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "real-estate-listing": {
      "command": "python",
      "args": ["-m", "meok_real_estate_listing_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
