from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.generator import generate_content_calendar

app = FastAPI(title="Content Calender Generator")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

@app.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    company_details: str = Form(...),
    weekly_focus: str = Form(...)
):
    result = generate_content_calendar(company_details, weekly_focus)
    records = result["df"].to_dict(orient="records")

    return templates.TemplateResponse(
        "result.html",
        {
            "result": request,
            "records": records,
            "file_name": result["file_name"]
        }
    )

@app.get("/download/{file_name}")
def download_file(file_name: str):
    file_path = f"output/{file_name}"
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/vnd.openxmlformats-afficedocument.spreadsheetml.sheet"
    )
