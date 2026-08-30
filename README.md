# Verify API MCP Server

MCP server for [Verify API](https://goodsong.dev): a pay-per-call verification
service that gives agents a fast, structured, evidence-backed yes/no/unknown on
claims they'd otherwise guess at.

Stop your agent from citing things that don't exist. Two tools, one answer each,
evidence attached.

## Tools

- **`verify_citation`** -- does a citation exist, is it retracted, and does the
  given title/authors/year/journal match the canonical record? Checked against
  Crossref (includes Retraction Watch data) with OpenAlex as a fallback.
- **`verify_url`** -- does a URL resolve, what's the final status and redirect
  chain, is it archived on the Wayback Machine, and (optionally) does expected
  text appear on the page?

Every response includes a `verdict` (`confirmed` / `contradicted` / `unknown`),
the individual `checks` that were run, and `evidence` with source URLs so a
human can verify the answer themselves. `unknown` is a valid, honest answer --
this server never guesses to avoid it.

## Install

```bash
pip install verify-api-mcp
```

## Configure

Get a free API key (100 calls, no card required):

```bash
curl -X POST https://goodsong.dev/signup
```

Then add to your MCP client's config (e.g. `mcp.json`):

```json
{
  "mcpServers": {
    "verify-api": {
      "command": "verify-api-mcp",
      "env": {
        "VERIFY_API_KEY": "vk_..."
      }
    }
  }
}
```

`VERIFY_API_URL` defaults to `https://goodsong.dev` and only needs to be set if
you're pointing at a different deployment.

## License

MIT

<!-- mcp-name: io.github.mgdsn/verify-api-mcp -->
