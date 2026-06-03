import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine
import models
from routers import auth, admin_tokens, admin_scripts, admin_logs, scripts, logs

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IsyShell API",
    version="1.0.0",
    description="Secure shell script execution microservice for Isy.One"
)

app.include_router(auth.router)
app.include_router(admin_tokens.router)
app.include_router(admin_scripts.router)
app.include_router(admin_logs.router)
app.include_router(scripts.router)
app.include_router(logs.router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir) and os.listdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/admin", include_in_schema=False)
    def admin_ui():
        return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "isyshell"}
