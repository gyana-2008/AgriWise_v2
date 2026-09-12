"""
🌾 AGRIWISE AI - Root Launcher Script
Allows running from repository root on Render / Production or Local.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import uvicorn

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Check if backend is directly under base_dir or inside agriwise-ai
    if os.path.exists(os.path.join(base_dir, "backend")):
        backend_dir = os.path.join(base_dir, "backend")
    elif os.path.exists(os.path.join(base_dir, "agriwise-ai", "backend")):
        backend_dir = os.path.join(base_dir, "agriwise-ai", "backend")
    else:
        backend_dir = base_dir

    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    reload = os.environ.get("RELOAD", "false").lower() in ("true", "1")

    print(f"🌾 Starting AGRIWISE AI Platform on http://{host}:{port} ...")
    uvicorn.run("main:app", host=host, port=port, reload=reload, reload_dirs=[backend_dir] if reload else None)
