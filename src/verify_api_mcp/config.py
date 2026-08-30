import os

# The API key this server instance authenticates as -- issued via
# https://goodsong.dev/signup (free tier) or a paid key. Set per MCP client
# config, e.g. `"env": {"VERIFY_API_KEY": "vk_..."}` in the client's mcp.json.
VERIFY_API_KEY = os.environ.get("VERIFY_API_KEY", "")

# This server runs on the END USER's machine (installed from PyPI/an MCP
# registry), not ours -- it has no access to our database or core code, so
# it must call the hosted API over HTTP like any other API-key client would.
VERIFY_API_URL = os.environ.get("VERIFY_API_URL", "https://goodsong.dev")
