import os
import json
import httpx
from dotenv import load_dotenv
from openai import OpenAI
from .mcp_client import MCPClient

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CAB_API_URL = os.getenv("CAB_API_URL", "http://localhost:8000/api/cab_details/")
CAB_MCP_TOKEN = os.getenv("CAB_MCP_TOKEN")

mcp_client = MCPClient()

# Lazily initialize OpenAI client to avoid import-time failures in tests
_openai_client: OpenAI | None = None

def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client

system_prompt = """
You are a JSON-based assistant that helps manage users and cabs.
Always return a **valid JSON** response suitable for frontend schema rendering.

You are a helpful assistant that generates structured JSON responses in the ChatSchema format.

All responses must strictly be in **valid JSON** matching this structure:

### ✅ Response Format

{
  "id": "unique-id",
  "message": "Short user-facing message or instruction",
  "components": [
    {
      "id": "unique-component-id",
      "type": "form | select | button | input | text | rating | list | map | switch | date | etc.",
      "label": "Visible label for the UI element",
      "required": true | false,
      "options": [
        { "value": "string", "label": "string" }
      ],
      "children": [ ...nested components... ],
      "validation": {
        "minLength": number,
        "maxLength": number,
        "pattern": "regex-string",
        "message": "validation message"
      },
      "apiConfig": {
        "endpoint": "https://api.example.com/path",
        "method": "GET | POST | PUT | DELETE",
        "headers": { "Authorization": "Bearer token" }
      }
    }
  ]
}

Available tools:

1️⃣ get_all_cabs
    - Returns all cabs. (call cab roster backend)
    - Params: none

2️⃣ add_cab
    - Generates a JSON form to add a cab
      Example:
      {
        "id": "add-cab",
        "message": "Please provide cab details",
        "components": [
          {"id": "cab_model_name", "type": "input", "label": "Cab Model Name", "required": true},
          {"id": "cab_reg_name", "type": "input", "label": "Cab Registration Number", "required": true}
        ],
        "tool": "add_cab"
      }

Rules:
- If the query clearly requires fetching cab details → respond with {"tool": "get_all_cabs"}
- Never send plain text. Always wrap everything in valid JSON.
- Decide which tool to call based on the user's message.
- If a form is needed, generate the JSON form in this structure
- Always output a **complete JSON object** — no text outside the JSON.
- `message` should describe the purpose of the interaction.
- Use realistic labels, placeholders, and options.
- Include `apiConfig` when the UI requires data submission or retrieval.
- Do not include explanations or comments.
- Follow the examples provided below for structure consistency.
- Always return JSON in the above schema style, similar to the 'appointment' example.
- Do not provide explanations or reasoning. Only return valid JSON output.
- every response must be wrapped in a JSON object with a "message" key.

"""


async def get_cabs_from_backend():
    headers = {"Authorization": f"Bearer {CAB_MCP_TOKEN}"} if CAB_MCP_TOKEN else {}
    async with httpx.AsyncClient() as http:
        resp = await http.get(CAB_API_URL, headers=headers)
        resp.raise_for_status()
        return resp.json()


async def handle_chat(user_input: str):
    # Optionally ensure MCP is connected for future tool calls
    # Only attempt MCP stdio connection if an explicit script path is provided
    backend_main = os.getenv("CAB_MCP_SERVER")
    if backend_main and not mcp_client.session:
        try:
            await mcp_client.connect(backend_main)
            _ = await mcp_client.list_tools()
        except Exception:
            # Non-fatal; backend HTTP will still work
            pass

    try:
        client = _get_openai_client()
    except Exception:
        # If OpenAI is not configured, return a minimal JSON indicating setup is needed
        return {
            "id": "config-missing",
            "message": "Model not configured. Set OPENAI_API_KEY to enable chat.",
            "components": [
                {
                    "id": "setup-info",
                    "type": "text",
                    "label": "Configuration",
                    "required": False,
                    "children": [],
                }
            ],
        }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {"message": "Sorry, invalid response format from model."}

    if parsed.get("tool") == "get_all_cabs":
        cabs = await get_cabs_from_backend()
        return {
            "id": "cab-list",
            "message": "Here are all available cabs:",
            "components": [
                {
                    "id": "list",
                    "type": "list",
                    "label": "Available Cabs",
                    "list": cabs,
                }
            ],
        }

    return parsed
