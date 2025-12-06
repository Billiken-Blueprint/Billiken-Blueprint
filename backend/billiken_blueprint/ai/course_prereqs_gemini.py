from pydoc import cli
import time
from typing import Literal, Sequence
from venv import logger
from pydantic import BaseModel

from google import genai
from google.genai import types
from google.genai.errors import APIError


class CoursePrereq(BaseModel):
    major_code: str
    course_number: int
    concurrent_allowed: bool
    end_number: int | None


class ResponseModel(BaseModel):
    operator: Literal["AND", "OR"]
    operands: Sequence[ResponseModel | CoursePrereq]


client = genai_client


def parse_prereqs(reqs_text: str) -> dict:
    time.sleep(12)
    system_prompt = (
        "You must create an abstract syntax tree representation of course "
        "prerequisites. You must only respond with a JSON object matching the "
        "schema provided. Course numbers only exist as a full caps major code "
        "followed by a space and then the course number (e.g., CSCI 1010). "
        "If a course range is provided (e.g., CSCI 1010-1090), you must "
        "represent it using the 'end_number' field. If a course cannot be "
        "conformed to a course code (e.g. '1520 on the placement exam'), you must "
        "omit it from the response."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=reqs_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=ResponseModel.model_json_schema(),
            ),
        )

        validated_data = ResponseModel.model_validate_json(response.text)
        return validated_data.model_dump()

    except APIError as e:
        logger.error(f"API Error: {e.message}")
        raise

    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        raise


if __name__ == "__main__":
    text = '<a href="/search/?p=CSCI%205030" data-action="result-detail" data-group="code:CSCI 5030" >CSCI 5030</a> with a grade of C- or higher'
    text = '((0 Course from <a href="/search/?p=CSCI%201010" data-action="result-detail" data-group="code:CSCI 1010"  class="notoffered">CSCI 1010</a>-<a href="/search/?p=CSCI%201090" data-action="result-detail" data-group="code:CSCI 1090"  class="notoffered">1090</a> with a grade of C- or higher, <a href="/search/?p=BME%202000" data-action="result-detail" data-group="code:BME 2000" >BME 2000</a> with a grade of C- or higher, <a href="/search/?p=CVNG%201500" data-action="result-detail" data-group="code:CVNG 1500"  class="notoffered">CVNG 1500</a> with a grade of C- or higher, <a href="/search/?p=MATH%203850" data-action="result-detail" data-group="code:MATH 3850"  class="notoffered">MATH 3850</a> with a grade of C- or higher, <a href="/search/?p=STAT%203850" data-action="result-detail" data-group="code:STAT 3850" >STAT 3850</a> with a grade of C- or higher, <a href="/search/?p=ECE%201001" data-action="result-detail" data-group="code:ECE 1001" >ECE 1001</a> with a grade of C- or higher, or <a href="/search/?p=GIS%204090" data-action="result-detail" data-group="code:GIS 4090"  class="notoffered">GIS 4090</a> with a grade of C- or higher); (<a href="/search/?p=MATH%201200" data-action="result-detail" data-group="code:MATH 1200" >MATH 1200</a> or 0 Course from <a href="/search/?p=MATH%201320" data-action="result-detail" data-group="code:MATH 1320" >MATH 1320</a>-<a href="/search/?p=MATH%204999" data-action="result-detail" data-group="code:MATH 4999"  class="notoffered">4999</a>))'
    d = parse_prereqs(text)
    print(d)
