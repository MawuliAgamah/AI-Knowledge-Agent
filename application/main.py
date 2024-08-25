from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


print(f"BASE_DIR: {BASE_DIR}")
print(f"Template Directory: {Path(BASE_DIR, 'templates')}")

app = FastAPI()

templates = Jinja2Templates(str(Path(BASE_DIR, 'templates')))

@app.get('/')
async def name(request: Request):
    print(BASE_DIR)
    return templates.TemplateResponse("base.html", {'request': request, "name": "hello"})