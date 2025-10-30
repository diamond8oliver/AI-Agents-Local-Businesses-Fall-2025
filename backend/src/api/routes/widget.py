from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/widget", tags=["widget"])

@router.get("/widget.js")
async def get_widget():
    widget_path = os.path.join(os.path.dirname(__file__), "../../../static/widget.js")
    return FileResponse(widget_path, media_type="application/javascript")
