import asyncio
import os
import base64
from typing import Annotated
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field
import httpx
from urllib.parse import quote_plus

# Fix import path - adjust based on your actual FastMCP version
try:
    from fastmcp.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
except ImportError:
    from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair

# Use FastMCP's error classes if available, fallback to mcp
try:
    from fastmcp import ErrorData, McpError
    from fastmcp.types import INVALID_PARAMS, INTERNAL_ERROR
except ImportError:
    from mcp import ErrorData, McpError
    from mcp.types import INVALID_PARAMS, INTERNAL_ERROR

from mcp.server.auth.provider import AccessToken

load_dotenv()

# ===== env / assertions =====
TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")
NASA_API_KEY = os.environ.get("NASA_API_KEY")

assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"
assert NASA_API_KEY is not None, "Please set NASA_API_KEY in your .env file"

# ===== Auth provider =====
class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="puch-client",
                scopes=["*"],
                expires_at=None,
            )
        return None

# ===== ENABLE STATELESS MODE =====
mcp = FastMCP(
    "NASA Astronomy MCP Server",  # Changed server name
    auth=SimpleBearerAuthProvider(TOKEN),
    stateless_http=True
)

# ===== validate tool =====
@mcp.tool
async def validate() -> str:
    return MY_NUMBER

# ===== NASA Astronomy Tools =====
async def fetch_apod_with_image(date: str = None) -> dict:
    """Fetch Astronomy Picture of the Day with base64 image data"""
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&thumbs=True"
    if date:
        url += f"&date={date}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message="Failed to fetch APOD data"
            ))
        
        data = response.json()
        
        # Fetch the actual image and convert to base64
        image_base64 = None
        if data.get("media_type") == "image":
            image_url = data.get("url")  # or use "hdurl" for high-res
            if image_url:
                try:
                    image_response = await client.get(image_url)
                    if image_response.status_code == 200:
                        image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                except Exception as e:
                    print(f"Failed to fetch image: {e}")
        
        return {
            "title": data.get("title", "Untitled"),
            "date": data.get("date"),
            "explanation": data.get("explanation"),
            "media_type": data.get("media_type"),
            "url": data.get("url"),
            "hdurl": data.get("hdurl"),
            "thumbnail": data.get("thumbnail_url"),
            "image_base64": image_base64  # ← Added base64 image data
        }


async def fetch_planet_info(planet: str) -> dict:
    """Fetch planetary data"""
    url = f"https://api.le-systeme-solaire.net/rest/bodies/{quote_plus(planet.lower())}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 404:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message="Planet not found. Try: mercury, venus, earth, mars, jupiter, saturn, uranus, neptune"
            ))
        
        data = response.json()
        return {
            "name": data.get("englishName"),
            "is_planet": data.get("isPlanet", False),
            "gravity": data.get("gravity"),
            "density": data.get("density"),
            "moons": [moon["moon"] for moon in data.get("moons", [])]
        }

# ===== MCP Tools =====
@mcp.tool(description="Get NASA Astronomy Picture of the Day with image data")
async def get_apod_with_image(
    date: Annotated[str, Field(description="Date in YYYY-MM-DD format (optional)")] = None
) -> dict:
    """Returns today's astronomy picture with base64 image data"""
    try:
        return await fetch_apod_with_image(date)
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"APOD fetch error: {str(e)}"
        ))


@mcp.tool(description="Get planetary information")
async def get_planet(
    planet_name: Annotated[str, Field(description="Planet name (e.g., mars, jupiter)")]
) -> dict:
    """Returns facts about a planet"""
    try:
        return await fetch_planet_info(planet_name)
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Planet fetch error: {str(e)}"
        ))

# ===== run server =====
async def main():
    print("🚀 Starting NASA Astronomy MCP server in STATELESS mode on http://0.0.0.0:8086")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)

if __name__ == "__main__":
    asyncio.run(main())