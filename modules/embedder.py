from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

def get_embedder():
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        transport="grpc"
    )
