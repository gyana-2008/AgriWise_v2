"""
🌾 AGRIWISE AI - Launcher Script
Runs the FastAPI application on http://127.0.0.1:8000 using Uvicorn.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import uvicorn

if __name__ == "__main__":
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    reload = os.environ.get("RELOAD", "false").lower() in ("true", "1")

    print(f"🌾 Starting AGRIWISE AI Platform on http://{host}:{port} ...")
    uvicorn.run("main:app", host=host, port=port, reload=reload, reload_dirs=[backend_dir] if reload else None)
