# Importing Union and Optional for type hinting in Python
from typing import Union, Optional

# Importing FastAPI and other necessary classes from the fastapi module
from fastapi import FastAPI, Request, Form, File, UploadFile

# Importing HTMLResponse from fastapi.responses to send HTML responses
from fastapi.responses import HTMLResponse

# Importing Jinja2Templates to enable server-side rendering with Jinja2 templates
from fastapi.templating import Jinja2Templates

# Importing StaticFiles to serve static files (like CSS, JavaScript, images)
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# For handling HTML templates and serving static files such as CSS, JavaScript, and images in a FastAPI application
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/chat_with_pdf", response_class=HTMLResponse)
async def get_chat_with_pdf(request: Request):
    return templates.TemplateResponse("chat_with_pdf.html", {"request": request})

@app.post("/chat_with_pdf", response_class=HTMLResponse)
async def post_chat_with_pdf(request: Request, file: UploadFile = File(...)):
    # Handle PDF chat logic here
    return templates.TemplateResponse("chat_with_pdf.html", {"request": request, "result": "PDF processed"})

@app.get("/chat_with_youtube", response_class=HTMLResponse)
async def get_chat_with_youtube(request: Request):
    return templates.TemplateResponse("chat_with_youtube.html", {"request": request})

@app.post("/chat_with_youtube", response_class=HTMLResponse)
async def post_chat_with_youtube(request: Request, url: str = Form(...)):
    # Handle YouTube chat logic here
    return templates.TemplateResponse("chat_with_youtube.html", {"request": request, "result": "YouTube video processed"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)