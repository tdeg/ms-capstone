"""
API entry point.
"""
import os
import uvicorn

if __name__ == "__main__":
    if os.environ.get("ENV") == "prod":
        uvicorn.run("app.api:app", host="0.0.0.0", port=8081)
    else:
        uvicorn.run("app.api:app", host="0.0.0.0", port=8081, reload=True)
