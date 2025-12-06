from google.genai.errors import APIError
from billiken_blueprint.ai.genai_client import genai_client
from pydantic import BaseModel
import time
from google.genai import types
from venv import logger
client = genai_client

debounce = 3
last_query_t = 0

class ResponseModel(BaseModel):
    keywords: list[str]

def user_input_to_keywords(user_input: str) -> list[str]:
    global last_query_t
    t = time.time()
    if t - last_query_t < debounce:
        time.sleep(debounce - (t - last_query_t))
    last_query_t = t

    system_prompt = (
        "A user inputs their interests, aspirations, goals, what they want to "
        "learn, or what they want to do after graduation. You must create a "
        "list of keywords based on the user's input. These keywords will be "
        "used against vector embeddings of course descriptions to find courses "
        "that are most relevant to the user's input, so be broad and specify "
        "technologies, general concepts, and high level skills."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_json_schema=ResponseModel.model_json_schema(),
            ),
        )
        validated_data = ResponseModel.model_validate_json(response.text)

        logger.info("Generated keywords: %s", validated_data.keywords)

        return validated_data.keywords

    except APIError as e:
        logger.error(f"API Error: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        raise

if __name__ == "__main__":
    result = user_input_to_keywords("I want to be a pilot at NASA.")
    print(result)