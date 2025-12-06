from billiken_blueprint.domain.courses.course import CourseWithDescription
from billiken_blueprint.ai.genai_client import genai_client
from typing import Sequence
from google.genai import types
from google.genai.errors import APIError
from venv import logger
client = genai_client

def get_retrieval_course_embeddings(courses: Sequence[CourseWithDescription]):

    batch_size = 100
    embeddings = []
    for i in range(0, len(courses), batch_size):
        batch = courses[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} of {len(courses) // batch_size}")
        try:
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=[course.description for course in batch],
                config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )
        except APIError as e:
            logger.error(f"API Error getting course embeddings: {e}")
            raise

        except Exception as e:
            logger.error(f"Error getting course embeddings: {e}")
            raise
        
        embeddings.extend(result.embeddings)
        break
    return embeddings

def get_query_course_embedding(query: str):
    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=query,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            )
        )
        embeddings = result.embeddings[0]
        return embeddings

    except APIError as e:
        logger.error(f"API Error getting query embedding: {e}")
        raise

    except Exception as e:
        logger.error(f"Error getting query embedding: {e}")
        raise