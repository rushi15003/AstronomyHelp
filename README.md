# NASA Astronomy MCP Server

A stateless MCP server built with [FastMCP](https://pypi.org/project/fastmcp/) that fetches NASA’s Astronomy Picture of the Day (APOD) and planetary information.  
Supports Bearer Token authentication, returns base64 image data for APOD images, and retrieves planetary facts from public APIs.

---

## 🚀 Features

- Stateless MCP server for easy deployment
- Bearer Token–based authentication
- Fetches **NASA Astronomy Picture of the Day** with:
  - Title, date, explanation
  - High-res image URL
  - Base64-encoded image data
- Fetches **planetary data** (gravity, density, moons, etc.)
- Asynchronous `httpx` for fast API calls
- Error handling with MCP standard error codes

---
- Python **3.10+**
- [NASA API Key](https://api.nasa.gov/)
- [Le Systeme Solaire API](https://api.le-systeme-solaire.net/) (no API key required)
- An authentication token for your MCP server (`AUTH_TOKEN`)

---


## 📦 Requirements## ⚙️ Installation & Setup

### 1 Create and activate a virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate 
```
### 2 Install dependencies
```bash
- pip install -r requirements.txt
```
### 3  Set up environment variables
- Create a .env file in the root directory:
```bash
- AUTH_TOKEN=your_auth_token_here
- MY_NUMBER=your_number_here
-  NASA_API_KEY=api_key

```

### 4  Running the Server
```bash
- python main.py
```

📡 API Tools
validate
Verifies the server is running and returns MY_NUMBER.

get_apod_with_image
Fetches NASA’s Astronomy Picture of the Day with base64 image data.

Example input:

```bash
{
  "date": "2025-08-10"
}
```
Example output:
```bash
{
  "title": "The Milky Way Over the Desert",
  "date": "2025-08-10",
  "explanation": "A stunning view of our galaxy...",
  "media_type": "image",
  "url": "https://apod.nasa.gov/apod/image.jpg",
  "hdurl": "https://apod.nasa.gov/apod/image_hd.jpg",
  "thumbnail": null,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAA..."
}
get_planet
Fetches planetary information.
```
Example input:

```bash
{
  "planet_name": "mars"
}
```
Example output:

```bash
{
  "name": "Mars",
  "is_planet": true,
  "gravity": 3.711,
  "density": 3.93,
  "moons": ["Phobos", "Deimos"]
}
```
# 🛡 Authentication
This server uses Bearer Token authentication.
Include the Authorization: Bearer <AUTH_TOKEN> header in every request.

