import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

# Fetch the backend URL from environment variables.
# Default to localhost for local testing, but Docker will override this.
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8001")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(name="chat_page.html", request=request)


@app.post("/chat")
async def forward_chat(payload: dict):
    """
    Acts as a Reverse Proxy. Receives JSON from the browser
    and forwards it to the containerized Python backend.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Forward the payload to the backend container
            response = await client.post(f"{BACKEND_URL}/chat", json=payload, timeout=42.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=500, detail=f"Backend communication failed: {exc}"
            )

#import os
#from fastapi import FastAPI, Request, HTTPException
#from fastapi.templating import Jinja2Templates
#import httpx

#app = FastAPI()
#templates = Jinja2Templates(directory="src/templates")

## Fetch the backend URL from environment variables.
#BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")


#@app.get("/")
#async def read_root(request: Request):
#    return templates.TemplateResponse(name="chat_page.html", request=request)


#@app.post("/chat")
#async def forward_chat(payload: dict):
#    """
#    MOCK MODE FOR TESTING: Receives JSON from the browser, logs the payload
#    to the console, and returns a mock reply without calling the backend.
#    """
#    # 1. Extract values sent by your updated chat_page.html JavaScript
#    user_message = payload.get("message", "")
#    pdf_text = payload.get("pdf_text", "")

#    # 2. Print to your terminal so you can verify the data arrived correctly
#    print("\n--- [TESTING] Received Payload From Frontend ---")
#    print(f"User Message: {user_message}")
#    print(f"PDF Text Length: {len(pdf_text)} characters")
#    if pdf_text:
#        print(f"PDF Text Snippet: {pdf_text[:200]}...")
#    print("------------------------------------------------\n")

#    # 3. Simulate a successful processing cycle from a fake AI backend
#    if pdf_text:
#        mock_reply = (
#            f"🤖 [Mock AI] I received your message: '{user_message}'. "
#            f"I also successfully processed the attached PDF file "
#            f"({len(pdf_text)} characters found)!"
#        )
#    else:
#        mock_reply = f"🤖 [Mock AI] I received your message: '{user_message}'."

#    # 4. Return the expected JSON dictionary back to your JavaScript fetch() block
#    return {"reply": mock_reply}

#    # --- Commented out backend proxy connection for testing ---
#    # async with httpx.AsyncClient() as client:
#    #     try:
#    #         response = await client.post(f"{BACKEND_URL}/chat", json=payload)
#    #         response.raise_for_status()
#    #         return response.json()
#    #     except httpx.HTTPError as exc:
#    #         raise HTTPException(
#    #             status_code=500, detail=f"Backend communication failed: {exc}"
#    #         )
