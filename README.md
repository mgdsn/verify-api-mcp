# Verify API MCP Server

MCP server for [Verify API](https://goodsong.dev): a pay-per-call verification
service that gives agents a fast, structured, evidence-backed yes/no/unknown on
claims they'd otherwise guess at.

Stop your agent from citing things that don't exist, installing things that
shouldn't, or paying sellers that don't check out. Eight tools, one answer
each, evidence attached.

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
- **`verify_repo`** -- does a GitHub repo exist, is it archived or disabled?
  Checked against the GitHub REST API. Catches an agent recommending or
  depending on a renamed, taken-down, or abandoned repo.
- **`verify_case`** -- does a legal case citation exist, and does the given
  case name match the canonical record? Checked against CourtListener. Catches
  a fabricated case citation, including a real-looking citation number paired
  with an invented case name. Existence only -- does not check whether a case
  is still good law.
- **`verify_filing`** -- given a filer's SEC CIK and a claimed accession
  number, does that filing exist, and does its form type/filing date match
  what's claimed? Checked against SEC EDGAR's submissions API. Catches a
  fabricated or misattributed filing citation, including a real-looking
  accession number paired with an invented form type or date.
- **`verify_drug`** -- given a claim_type (`approval`, `ndc`, or `recall`) and
  its identifier, does that FDA record exist, and does the given name match
  the canonical record? Checked against openFDA. Catches a fabricated or
  misattributed drug approval, NDC listing, or recall citation.
  Existence/status only -- not medical advice.
- **`verify_seller`** -- before paying an x402 seller, does it exist and
  respond with a well-formed 402 challenge, is its own declared input/output
  schema internally consistent, and is its payout address sanctioned? Checked
  live against the seller itself plus a sanctions oracle and on-chain wallet
  history (Base payTo addresses only). Confirms the checkable things check
  out -- not a guarantee of trustworthiness.

Every response includes a `verdict` (`confirmed` / `contradicted` / `unknown`),
the individual `checks` that were run, and `evidence` with source URLs so a
human can verify the answer themselves. `unknown` is a valid, honest answer --
this server never guesses to avoid it.

## Install

```bash
pip install verify-api-mcp
```

## Configure

The primary way to use Verify API is [x402](https://www.x402.org) pay-per-call
(no key, no account, from $0.005/call -- $0.01 for `verify_case`) -- but this
MCP server specifically needs a subscription key instead, since x402 requires
a wallet most MCP clients don't have. Get one by subscribing to a plan at
[goodsong.dev/#pricing](https://goodsong.dev/#pricing) (Solo, $15/mo, or Team,
$49/mo) -- the key is issued immediately on the checkout success page. There's
no free tier.

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
