import chromadb
from billiken_blueprint.ai.genai_client import genai_client
from google.genai import types
from billiken_blueprint.ai.get_course_suggestions import user_input_to_keywords


def get_courses_from_user_query(
    user_query: str,
    chroma_collection: chromadb.Collection,
    excluded_course_ids: list[int] = [],
) -> dict:
    MODEL = "gemini-embedding-001"

    client = genai_client

    keywords = user_input_to_keywords(user_query)

    result = client.models.embed_content(
        model=MODEL,
        contents=user_query + " " + " ".join(keywords),
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )

    query_embedding = result.embeddings[0].values

    n_results = 20
    max_results = 100

    while n_results <= max_results:
        results = chroma_collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["metadatas", "distances", "documents"],
            where={"course_int": {"$lt": 5000}},
        )

        if not results["ids"] or not results["ids"][0]:
            break

        # Filter results
        filtered_ids = []
        filtered_metadatas = []
        filtered_distances = []
        filtered_documents = []

        # We assume single query, so list index 0
        original_ids = results["ids"][0]
        original_metadatas = results["metadatas"][0]
        original_distances = results["distances"][0]
        original_documents = results["documents"][0]

        for i in range(len(original_ids)):
            course_id = original_metadatas[i]["course_id"]
            if course_id not in excluded_course_ids:
                filtered_ids.append(original_ids[i])
                filtered_metadatas.append(original_metadatas[i])
                filtered_distances.append(original_distances[i])
                filtered_documents.append(original_documents[i])

                if len(filtered_ids) == 5:
                    break

        if len(filtered_ids) == 5 or n_results == max_results:
            return {
                "ids": [filtered_ids],
                "metadatas": [filtered_metadatas],
                "distances": [filtered_distances],
                "documents": [filtered_documents],
            }

        n_results += 20

    return results
