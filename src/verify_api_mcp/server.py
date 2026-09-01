"""MCP server: exposes verify_citation, verify_url, verify_package,
verify_repo, verify_case, and verify_seller as tools.

A thin HTTP client against the hosted Verify API at https://goodsong.dev,
authenticated the same way any other API-key caller is
(Authorization: Bearer <key>). Has no access to the API's database or core
verification code -- it just calls the public endpoints.
"""

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from verify_api_mcp.config import VERIFY_API_KEY, VERIFY_API_URL

server = MCPServer(
    name="verify-api",
    title="Verify API",
    description=(
        "Deterministic, evidence-backed verification for citations, URLs, packages, "
        "GitHub repos, legal case citations, and x402 sellers -- catches fabricated or "
        "retracted citations, dead/altered links, hallucinated or unsafe dependencies, "
        "abandoned repos, and inconsistent or sanctioned x402 marketplace listings "
        "before an agent acts on them."
    ),
)


async def _call_api(path: str, payload: dict) -> dict:
    if not VERIFY_API_KEY:
        raise ToolError(
            "No API key configured for this MCP server. Set VERIFY_API_KEY in the "
            "client's MCP config to a key from subscribing at "
            "https://goodsong.dev/#pricing (no free tier). If you'd rather not "
            "subscribe, the same API also accepts x402 pay-per-call directly -- "
            "see https://goodsong.dev for details -- but MCP itself always needs a key."
        )
    body = {k: v for k, v in payload.items() if v is not None}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{VERIFY_API_URL}{path}",
                json=body,
                headers={"Authorization": f"Bearer {VERIFY_API_KEY}"},
            )
    except httpx.RequestError as e:
        raise ToolError(f"Could not reach the Verify API at {VERIFY_API_URL}: {e}") from e

    if resp.status_code == 401:
        raise ToolError("VERIFY_API_KEY is invalid or revoked.")
    if resp.status_code == 402:
        detail = resp.json().get("error", {}).get("message", "Monthly call quota exceeded.")
        raise ToolError(detail)
    if resp.status_code >= 400:
        raise ToolError(f"Verify API returned {resp.status_code}: {resp.text[:200]}")
    return resp.json()


@server.tool(
    description=(
        "Verify a citation: does it exist, is it retracted, and do the given title/"
        "authors/year/journal match the canonical record? Checked against Crossref "
        "(includes Retraction Watch data) with OpenAlex as a fallback when no DOI "
        "is given. Provide a doi and/or a title."
    )
)
async def verify_citation(
    doi: str | None = None,
    title: str | None = None,
    authors: list[str] | None = None,
    year: int | None = None,
    journal: str | None = None,
) -> dict:
    return await _call_api(
        "/verify/citation",
        {"doi": doi, "title": title, "authors": authors, "year": year, "journal": journal},
    )


@server.tool(
    description=(
        "Verify a URL: does it resolve, what's the final status and redirect chain, "
        "is it archived on the Wayback Machine, and (optionally) does expected text "
        "appear on the page. Checked via direct fetch and the Internet Archive."
    )
)
async def verify_url(
    url: str,
    expected_content: str | None = None,
    expected_date: str | None = None,
) -> dict:
    return await _call_api(
        "/verify/url",
        {"url": url, "expected_content": expected_content, "expected_date": expected_date},
    )


@server.tool(
    description=(
        "Verify a package: does it exist, is it deprecated or yanked, and does it have "
        "known vulnerabilities? Checked against the npm/PyPI/crates.io registry plus "
        "OSV.dev advisories. Catches an agent installing a hallucinated or squatted "
        "package name. ecosystem must be one of: npm, pypi, crates."
    )
)
async def verify_package(
    ecosystem: str,
    name: str,
    version: str | None = None,
) -> dict:
    return await _call_api(
        "/verify/package",
        {"ecosystem": ecosystem, "name": name, "version": version},
    )


@server.tool(
    description=(
        "Verify a GitHub repo: does it exist, is it archived or disabled? Catches an "
        "agent recommending or depending on a repo that's been renamed, taken down, "
        "or abandoned. Checked against the GitHub REST API."
    )
)
async def verify_repo(owner: str, repo: str) -> dict:
    return await _call_api("/verify/repo", {"owner": owner, "repo": repo})


@server.tool(
    description=(
        "Verify a legal case citation: does it exist, and does the given case name "
        "match the canonical record? Catches a fabricated case citation, including a "
        "real-looking citation number paired with an invented case name. Checked "
        "against CourtListener. Does not check whether a case is still good law."
    )
)
async def verify_case(citation: str, case_name: str | None = None) -> dict:
    return await _call_api("/verify/case", {"citation": citation, "case_name": case_name})


@server.tool(
    description=(
        "Verify an x402 seller before paying it: does it exist and respond with a "
        "well-formed 402 challenge, is its own declared input/output schema internally "
        "consistent, and is its payout address sanctioned? Checked live against the "
        "seller itself plus a sanctions oracle and on-chain wallet history (Base payTo "
        "addresses only). Confirms the checkable things about a seller check out -- not "
        "a guarantee of trustworthiness, which no free source can promise. method "
        "defaults to POST; set it to GET if that's what triggers the seller's 402."
    )
)
async def verify_seller(resource_url: str, method: str | None = None) -> dict:
    return await _call_api("/verify/seller", {"resource_url": resource_url, "method": method})


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
