from pydoc import cli
from typing import Literal, Sequence
from pydantic import BaseModel

from google import genai
from google.genai import types

class CoursePrereq(BaseModel):
    course_code: str
    concurrent_allowed: bool
    end_number: str | None


class ResponseModel(BaseModel):
    operator: Literal["AND", "OR"]
    operands: Sequence[ResponseModel | CoursePrereq]

client = genai.Client()

def parse_prereqs(reqs_text: str) -> dict:
    system_prompt = (
        "You must create an abstract syntax tree representation of course "
        "prerequisites. You must only respond with a JSON object matching the "
        "schema provided."
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=reqs_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=ResponseModel.model_json_schema()
            )
        )
