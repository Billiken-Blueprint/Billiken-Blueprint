import chromadb
from billiken_blueprint.ai.genai_client import genai_client
from google.genai import types
from billiken_blueprint.ai.get_course_suggestions import user_input_to_keywords

def get_courses_from_user_query(user_query: str, chroma_collection: chromadb.Collection) -> list[str]:
    MODEL = "gemini-embedding-001"

    client = genai_client


    keywords = user_input_to_keywords(user_query)

    result = client.models.embed_content(
        model=MODEL,
        contents=user_query+" "+" ".join(keywords),
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        ),
    )

    query_embedding = result.embeddings[0].values
    
    results = chroma_collection.query(
        query_embeddings=query_embedding,
        n_results=5,
        include=["metadatas", "distances", "documents"],
        where={
            "course_int": {
                "$lt": 5000
            }
        }
    )

    return results


    