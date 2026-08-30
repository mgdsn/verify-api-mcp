"""MCP server: exposes verify_citation and verify_url as tools.

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
        "Deterministic, evidence-backed verification for citations and URLs -- "
        "catches fabricated or retracted citations and dead/altered links before "
        "an agent repeats them."
    ),
)


async def _call_api(path: str, payload: dict) -> dict:
    if not VERIFY_API_KEY:
        raise ToolError(
            "No API key configured for this MCP server. Set VERIFY_API_KEY in the "
            "client's MCP config to a key from POST /signup at https://goodsong.dev/signup."
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


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
