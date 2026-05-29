import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import your primary pipeline function directly
from find_skill_gaps import find_skill_gaps, MODEL_NAME
from prompt_model import prompt_model

app = FastAPI()

# Read the database location from environment variables as required
DB_PATH = os.getenv("DATABASE_PATH", "data/jobs_d3_eval.db")


class ChatPayload(BaseModel):
    message: str
    pdf_text: str


@app.post("/chat")
async def process_chat(payload: ChatPayload):
    try:
        user_query = payload.message.strip()
        resume_text = payload.pdf_text.strip()
        user_query_lower = user_query.lower()

        # ---------------------------------------------------------------------
        # SCENARIO 3: User uploads a PDF AND asks for "skill gaps"
        # ---------------------------------------------------------------------
        is_skill_gap_request = any(
            kw in user_query_lower for kw in ["skill gap", "gaps", "missing skill"]
        )

        if resume_text and is_skill_gap_request:
            # 1. Define the temporary workspace file using Path object
            temp_resume_path = Path("temp_uploaded_resume.txt")

            # 2. Write the incoming payload text directly using Path utility
            temp_resume_path.write_text(resume_text, encoding="utf-8")

            try:
                # 3. Call your primary pipeline function (passing the string representation)
                result = find_skill_gaps(str(temp_resume_path), DB_PATH)
                sorted_gaps = result.gaps
            finally:
                # 4. Clean up the file using Path's unlink method (safely checked)
                if temp_resume_path.is_file():
                    temp_resume_path.unlink()

            if sorted_gaps:
                gap_list_str = ", ".join([f"`{g}`" for g in sorted_gaps[:15]])
                return {
                    "reply": (
                        f"📊 **Skill Gap Analysis Matrix**\n\n"
                        f"I scanned your resume text against our core jobs database tracking your profile using the primary hybrid analytical pipeline.\n\n"
                        f"❌ **Identified Technical Gaps ({len(sorted_gaps)}):**\n{gap_list_str}\n\n"
                        f"💡 *Recommendation:* Focus your next personal projects or courses on mastering these tools to better match the target job market profiles."
                    )
                }
            else:
                return {
                    "reply": "✅ **Perfect Alignment!** I checked your profile against the entire database and found zero technical skill gaps!"
                }

        # ---------------------------------------------------------------------
        # SCENARIO 2: User uploads a PDF (General inquiry or prompt instructions)
        # ---------------------------------------------------------------------
        elif resume_text:
            system_prompt = (
                f"You are an AI Resume Assistant. The user has uploaded the text content of their resume below.\n"
                f"Answer their question or request professionally using the context provided.\n\n"
                f"--- BEGIN RESUME TEXT ---\n{resume_text}\n--- END RESUME TEXT ---\n\n"
                f"User Question: {user_query if user_query else 'Please provide a brief professional summary of this resume.'}"
            )

            ai_response = prompt_model(MODEL_NAME, system_prompt)
            return {"reply": ai_response}

        # ---------------------------------------------------------------------
        # SCENARIO 1: Normal casual message (No PDF attached)
        # ---------------------------------------------------------------------
        else:
            if not user_query:
                return {
                    "reply": "👋 Hello! Type a message or upload your resume as a PDF to get started!"
                }

            ai_response = prompt_model(MODEL_NAME, user_query)
            return {"reply": ai_response}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An processing error occurred inside the AI backend engine: {str(e)}",
        )
