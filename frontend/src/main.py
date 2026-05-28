from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(name="chat_page.html", request=request)
