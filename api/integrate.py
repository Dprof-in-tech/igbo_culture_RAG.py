import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from astrapy.info import VectorServiceOptions
from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Load environment variables
ASTRA_DB_APPLICATION_TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
ASTRA_DB_API_ENDPOINT = os.environ["ASTRA_DB_API_ENDPOINT"]
ASTRA_DB_KEYSPACE = os.environ["ASTRA_DB_KEYSPACE_NAME"]
ASTRA_DB_API_KEY_NAME = os.environ.get("ASTRA_DB_API_KEY_NAME") or None
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Vector store setup
vectorize_options = VectorServiceOptions(
    provider="openai",
    model_name="text-embedding-3-small",
)

vector_store = AstraDBVectorStore(
    collection_name="igbo_proverbs",
    token=ASTRA_DB_APPLICATION_TOKEN,
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    namespace=ASTRA_DB_KEYSPACE,
    collection_vector_service_options=vectorize_options,
)

# List of URLs to scrape
urls = [
    "https://steemit.com/nigeria/@leopantro/50-igbo-proverbs-and-idioms",
    "https://www.zikoko.com/life/15-igbo-proverbs-and-their-meanings/",
    "https://www.igboguide.org/guests/igbo-proverbs.htm",
    "https://www.igbounionofwashington.com/post/igbo-proverbs-and-their-meanings",
    "https://oiroegbu.com/learn-africa/the-igbo-and-their-proverbs/",
    "https://sloaneangelou.blog/journal/100-igbo-proverbs",
    "https://www.teachyourselfigbo.com/igbo-proverbs-and-their-meanings.php",
    "https://ig.wikipedia.org/wiki/Ilu_igbo",
    "https://en.wikipedia.org/wiki/Igbo_culture",
    "https://en.wikipedia.org/wiki/Igbo_people",
    "https://en.wikipedia.org/wiki/Odinala",
    "https://en.wikipedia.org/wiki/Igbo_art",
    "https://www.britannica.com/topic/Igbo"
]

# Scrape and clean text
raw_texts = []

for url in urls:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines()]
            clean_text = "\n".join([line for line in lines if line])
            raw_texts.append({"url": url, "text": clean_text})
        else:
            print(f"Failed to fetch: {url}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# Basic heuristic to extract proverbs (can be improved)
proverb_candidates = []
for entry in raw_texts:
    lines = entry["text"].splitlines()
    for line in lines:
        if len(line.split()) > 4 and any(c in line for c in [".", "!", "—", "–"]):  # crude filtering
            proverb_candidates.append({
                "quote": line.strip(),
                "source": entry["url"]
            })

# Prepare documents for insertion
documents_to_insert = []

for idx, item in enumerate(proverb_candidates):
    doc = Document(
        page_content=item["quote"],
        metadata={"source": item["source"], "index": idx}
    )
    documents_to_insert.append(doc)

print(f"Prepared {len(documents_to_insert)} documents for vector store.")
print("Sample:", documents_to_insert[0].page_content[:150])

# Insert into Astra vector DB
inserted_ids = vector_store.add_documents(documents_to_insert)

print(f"Inserted {len(inserted_ids)} documents.")

# Sample similarity search
results = vector_store.similarity_search("Wisdom from elders", k=3)

for res in results:
    print(f"\n📜 {res.page_content}\n🔎 Source: {res.metadata['source']}")
