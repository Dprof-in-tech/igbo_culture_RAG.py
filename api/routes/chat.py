import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, OpenAI
from astrapy import DataAPIClient

load_dotenv()

# Load environment variables
ASTRA_DB_APPLICATION_TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
ASTRA_DB_API_ENDPOINT = os.environ["ASTRA_DB_API_ENDPOINT"]
ASTRA_DB_KEYSPACE = os.environ["ASTRA_DB_KEYSPACE_NAME"]
ASTRA_DB_API_KEY_NAME = os.environ.get("ASTRA_DB_API_KEY_NAME") or None
ASTRA_DB_COLLECTION_NAME = os.environ.get("ASTRA_DB_COLLECTION_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
   api_key=OPENAI_API_KEY
)

embedding_model = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small"
)

astra_db_client = DataAPIClient()
database = astra_db_client.get_database(
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    token=ASTRA_DB_APPLICATION_TOKEN,
    keyspace=ASTRA_DB_KEYSPACE
)

collection = database.get_collection(ASTRA_DB_COLLECTION_NAME)

def get_similar_docs (query, number):
    embedding = embedding_model.embed_query(query)[:1024]
    cursor = collection.find(
        {},
        sort={"$vector": embedding},
        limit=number
    )
    documents = list(cursor)
    docs_map = [doc.get("text", "") for doc in documents]
    return docs_map



def build_full_prompt(query):
    relevant_docs = get_similar_docs(query, 10)
    docs_single_string = "\n".join(relevant_docs)

    prompt_context = (
        """
        You are Achalugo, a warm and wise Igbo woman who knows everything about Igbo culture, language, proverbs, idioms, and traditions. Use the context to enrich your answers, but speak from your own deep knowledge when needed.

        Always translate Igbo words or proverbs to English carefully—make sure the meaning and explanation match. If not, correct it. Speak clearly, truthfully, and with gentle confidence. Only explain the usage of a proverb if you're asked.

        Use polite, simple language, and format your answers with clean Markdown. No images, just words from the heart.

        You are to only answer questions pertaining to igbo culture or language. If the question is not related to igbo culture or language, you will respond with the following: "This question is out of scope of my context."

        """
        )
    user_query_boilerplate = "USER QUERY: "
    document_context_boilerplate = "CONTEXT: "
    final_answer_boilerplate = "Final Answer: "

    nl = "\n"
    filled_prompt_template = (
        prompt_context
        + nl
        + user_query_boilerplate
        + query
        + nl
        + document_context_boilerplate
        + docs_single_string
        + nl
        + final_answer_boilerplate
    )
    return filled_prompt_template

def send_to_openai(full_prompt):
    return client.invoke(full_prompt)
