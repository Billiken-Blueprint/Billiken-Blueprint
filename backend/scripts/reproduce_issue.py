import sys
from pathlib import Path
import os

# Add the parent directory to the path so we can import billiken_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent))

from billiken_blueprint.ai.genai_client import genai_client
from google.genai import types

def test_embedding():
    text = "This is a test course description."
    print(f"Testing embedding for text: {text}")
    try:
        result = genai_client.models.embed_content(
            model="text-embedding-004", # Trying a known working model first, or I should stick to gemini-embedding-001 if that's what they use
            contents=[text],
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )
        print("Result object type:", type(result))
        # print("Result object dir:", dir(result))
        
        if hasattr(result, 'embeddings'):
            print(f"Number of embeddings: {len(result.embeddings)}")
            if len(result.embeddings) > 0:
                first_embedding = result.embeddings[0]
                print("First embedding object type:", type(first_embedding))
                # print("First embedding object dir:", dir(first_embedding))
                
                if hasattr(first_embedding, 'values'):
                    print("Values type:", type(first_embedding.values))
                    print("Values length:", len(first_embedding.values) if first_embedding.values else "None")
                    print("First 5 values:", first_embedding.values[:5] if first_embedding.values else "None")
                else:
                    print("First embedding has no 'values' attribute")
        else:
            print("Result has no 'embeddings' attribute")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_embedding()
