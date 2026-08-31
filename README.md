# Verify API MCP Server

MCP server for [Verify API](https://goodsong.dev): a pay-per-call verification
service that gives agents a fast, structured, evidence-backed yes/no/unknown on
claims they'd otherwise guess at.

Stop your agent from citing things that don't exist, or installing things that
shouldn't. Three tools, one answer each, evidence attached.

## Tools

- **`verify_citation`** -- does a citation exist, is it retracted, and does the
  given title/authors/year/journal match the canonical record? Checked against
  Crossref (includes Retraction Watch data) with OpenAlex as a fallback.
- **`verify_url`** -- does a URL resolve, what's the final status and redirect
  chain, is it archived on the Wayback Machine, and (optionally) does expected
  text appear on the page?
- **`verify_package`** -- does an npm/PyPI/crates.io package exist, is it
  deprecated or yanked, and does it have known vulnerabilities? Checked against
  the registry plus OSV.dev advisories. Catches an agent installing a
  hallucinated or squatted package name.

Every response includes a `verdict` (`confirmed` / `contradicted` / `unknown`),
the individual `checks` that were run, and `evidence` with source URLs so a
human can verify the answer themselves. `unknown` is a valid, honest answer --
this server never guesses to avoid it.

## Install

```bash
pip install verify-api-mcp
```

## Configure

Get an API key by subscribing to a plan at [goodsong.dev/#pricing](https://goodsong.dev/#pricing)
(Solo, $15/mo, or Team, $49/mo) -- the key is issued immediately on the
checkout success page. There's no free tier, but no commitment either: the
same API also accepts [x402](https://www.x402.org) pay-per-call (no key, no
account, $0.005/call) if you'd rather try it that way first -- this MCP
server specifically needs a key, since x402 requires a wallet most MCP
clients don't have.

Then add your key to your MCP client's config (e.g. `mcp.json`):

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
