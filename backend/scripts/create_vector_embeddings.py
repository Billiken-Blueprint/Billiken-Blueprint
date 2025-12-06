from chromadb.utils.embedding_functions.google_embedding_function import GoogleGenerativeAiEmbeddingFunction
from billiken_blueprint.ai.genai_client import genai_client
from chromadb.api.types import EmbeddingFunction
from chromadb.api.types import Documents
import sys
from pathlib import Path
import time
from google.genai import types
from google.genai.errors import APIError
from venv import logger
import os

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint.ai.course_embeddings import get_retrieval_course_embeddings
from billiken_blueprint.use_cases.get_courses_with_descriptions import get_courses_with_descriptions
from billiken_blueprint import services

class GeminiEmbeddingFunction(EmbeddingFunction):
    RPM = 100
    DEBOUNCE = 60 / RPM
    last_query_time = 0

    def __init__(self):
        self.last_query_time = time.time()
    def __call__(self, texts: Documents) -> list[list[float]]:
        MODEL_ID = "gemini-embedding-001"
        if time.time() - self.last_query_time < self.DEBOUNCE:
            time.sleep(self.DEBOUNCE - (time.time() - self.last_query_time))
        self.last_query_time = time.time()
        try:
            result = genai_client.models.embed_content(
                model=MODEL_ID,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                )
            )
            embeddings = result.embeddings[0].values
            print(embeddings)
            return embeddings

        except APIError as e:
            logger.error(f"API Error getting query embedding: {e}")
            raise

        except Exception as e:
            logger.error(f"Error getting query embedding: {e}")
            raise

async def main():
    RPM = 100
    DEBOUNCE = 60 / RPM
    last_query_time = 0
    MODEL_ID = "gemini-embedding-001"

    courses = await services.course_repository.get_all()
    sections = await services.section_repository.get_all()
    
    courses_with_descriptions = get_courses_with_descriptions(courses, sections)

    client = services.chroma_client
    collection_name = "course_descriptions"
    ef = GoogleGenerativeAiEmbeddingFunction(api_key=os.getenv("GEMINI_API_KEY"), model_name=MODEL_ID, task_type="RETRIEVAL_DOCUMENT",
        api_key_env_var="GEMINI_API_KEY")
    collection = client.get_or_create_collection(
        name=collection_name, 
        embedding_function=ef)
    
    for course in courses_with_descriptions:
        id = f"doc_{course.id}"
        course_int = int(course.course_number.rstrip("Xx"))
        meta = {
            "course_id": course.id,
            "major_code": course.major_code,
            "course_number": course.course_number,
            "course_code": f"{course.major_code} {course.course_number}",
            "course_int": course_int,
        }
        if (result := collection.get([id], limit=1, include=["embeddings", "metadatas"])) and result["ids"]:
            if result["metadatas"][0] != meta:
                print("Updating course %s" % course.id)
                collection.update(
                    documents=course.description,
                    metadatas=meta,
                    ids=id,
                    embeddings=result["embeddings"],
                )
            else:
                print("Skipping course %s" % course.id)
            continue
        
        if course.description == "":
            print("Skipping course %s" % course.id)
            continue

        if time.time() - last_query_time < DEBOUNCE:
            time.sleep(DEBOUNCE - (time.time() - last_query_time))
        last_query_time = time.time()

        print("Adding course %s" % course.id)
        collection.add(
            documents=course.description,
            metadatas=meta,
            ids=id,
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())