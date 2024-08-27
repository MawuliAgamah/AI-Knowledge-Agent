from pathlib import Path

import uvicorn  

from fastapi import FastAPI, Request,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Set up the base directory and path to templates
BASE_DIR = Path(__file__).resolve().parent



# initialise the fast api application
app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR/'static'), name="static")


app.add_middleware(GZipMiddleware)

templates = Jinja2Templates(directory=BASE_DIR / 'templates')

# Define the route for the home page
@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    posts = [
        {"id": 1, "title": "fastapi.blog title 1", "body": "Learn FastAPI with the fastapi.blog team 1"},
        {"id": 2, "title": "fastapi.blog title 2", "body": "Learn FastAPI with the fastapi.blog team 2"},
        {"id": 3, "title": "fastapi.blog title 3", "body": "Learn FastAPI with the fastapi.blog team 3"},
    ]
    context = {
        "request": request,
        "posts": posts,
        "title": "Home Page"
    }
    return templates.TemplateResponse("index.html", context)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/handle_prompt")
async def handle_prompt(prompt: str = Form(...)):
    # Process the prompt here
    print(prompt)
    return JSONResponse({
        "msg": "Prompt received successfully",
        "prompt": prompt,
    })


if __name__ == "__main__":
    uvicorn.run( "main:app", port = 8000,host = '0.0.0.0',reload=True)