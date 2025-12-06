# ChromaDB
chroma_client = chromadb.PersistentClient(path="data/chromadb")

course_descriptions_collection = chroma_client.get_or_create_collection(
    name="course_descriptions",
    embedding_function=chromadb.utils.embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key_env_var="GEMINI_API_KEY",
        model_name="gemini-embedding-001",
        task_type="RETRIEVAL_DOCUMENT"
    )
)