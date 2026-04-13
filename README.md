# Real Estate Listing MCP Server

**Property Intelligence AI**

Built by [MEOK AI Labs](https://meok.ai)

---

An MCP server for real estate professionals and homebuyers. Estimate property valuations, generate professional listings, find comparable sales, calculate mortgage payments, and analyze neighborhoods.

## Tools

| Tool | Description |
|------|-------------|
| `estimate_valuation` | Estimate property value using comp-based methodology with condition, age, and feature adjustments |
| `generate_listing` | Generate professional property listing descriptions in multiple styles |
| `find_comparable_sales` | Find comparable recent sales for pricing analysis |
| `calculate_mortgage` | Calculate monthly mortgage payment with full amortization breakdown |
| `analyze_neighborhood` | Analyze neighborhood characteristics and livability scores against buyer priorities |

## Quick Start

```bash
pip install real-estate-listing-mcp
```

### Claude Desktop

```json
{
  "mcpServers": {
    "real-estate-listing": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "/path/to/real-estate-listing-mcp"
    }
  }
}
```

### Direct Usage

```bash
python server.py
```

## Rate Limits

| Tier | Requests/Hour |
|------|--------------|
| Free | 60 |
| Pro | 5,000 |

## License

MIT - see [LICENSE](LICENSE)

---

*Part of the MEOK AI Labs MCP Marketplace*
