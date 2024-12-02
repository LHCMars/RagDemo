from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
embeddings = OpenAIEmbeddings()
DB_PATH = "./chroma_db"
COLLECTION_NAME = "chat_data"


def get_chroma_db():
    return Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )
