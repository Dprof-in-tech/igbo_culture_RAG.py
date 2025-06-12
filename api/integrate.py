import os
import time
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urlparse
from typing import List, Dict, Any, Tuple

from astrapy.info import VectorServiceOptions
from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

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

class IgboProverbExtractor:
    def __init__(self):
        # Igbo proverb indicators and patterns
        self.igbo_keywords = [
            'ilu', 'proverb', 'saying', 'wisdom', 'means', 'meaning', 'translation',
            'omenala', 'ndi igbo', 'igbo culture', 'traditional', 'ancestor'
        ]
        
        # Common Igbo words that appear in proverbs
        self.igbo_words = [
            'nwa', 'nne', 'nna', 'eze', 'obi', 'aka', 'anya', 'chi', 'mmadu', 'ndi',
            'umu', 'onye', 'ihe', 'oge', 'uku', 'ike', 'uche', 'ogu', 'aha', 'ala',
            'anwu', 'osisi', 'okwu', 'ego', 'uzo', 'ulo', 'agha', 'oga', 'kwu',
            'na-', 'ma', 'ka', 'ga-', 'ghi', 'kwa', 'rue', 'si', 'bu', 'di'
        ]
        
        # Proverb patterns
        self.proverb_patterns = [
            r'^[A-Z][^.]*\.$',  # Starts with capital, ends with period
            r'.*\bmeans?\b.*',   # Contains "means" or "mean"
            r'.*\btranslation\b.*',  # Contains "translation"
            r'.*\bsaying\b.*',   # Contains "saying"
            r'^\d+\.\s*',        # Numbered lists
            r'.*:\s*',           # Colon separated (proverb: meaning)
        ]
        
        # Words to exclude (navigation, headers, etc.)
        self.exclude_words = [
            'cookie', 'privacy', 'menu', 'search', 'login', 'register', 'home',
            'about', 'contact', 'copyright', 'terms', 'service', 'policy',
            'navigation', 'sidebar', 'footer', 'header', 'advertisement',
            'subscribe', 'newsletter', 'email', 'facebook', 'twitter', 'share'
        ]

    def is_likely_igbo_content(self, text: str) -> bool:
        """Check if text contains Igbo language or proverb indicators"""
        text_lower = text.lower()
        
        # Check for Igbo words
        igbo_word_count = sum(1 for word in self.igbo_words if word in text_lower)
        
        # Check for proverb indicators
        proverb_indicators = sum(1 for keyword in self.igbo_keywords if keyword in text_lower)
        
        # Check if it looks like a proverb structure
        has_meaning_structure = any(pattern in text_lower for pattern in ['means', 'meaning:', 'translation:', ':', '–', '—'])
        
        return igbo_word_count >= 2 or proverb_indicators >= 1 or has_meaning_structure

    def extract_proverb_pairs(self, text: str) -> List[Dict[str, str]]:
        """Extract Igbo proverb and English meaning pairs"""
        proverb_pairs = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 10:
                continue
                
            # Skip lines with exclude words
            if any(exclude_word in line.lower() for exclude_word in self.exclude_words):
                continue
            
            # Pattern 1: "Igbo proverb" - English meaning
            if ' - ' in line and self.is_likely_igbo_content(line):
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    proverb_pairs.append({
                        'igbo': parts[0].strip(),
                        'english': parts[1].strip(),
                        'type': 'proverb_pair'
                    })
                    continue
            
            # Pattern 2: "Igbo proverb" : English meaning
            if ':' in line and self.is_likely_igbo_content(line):
                parts = line.split(':', 1)
                if len(parts) == 2 and len(parts[0]) > 10:
                    proverb_pairs.append({
                        'igbo': parts[0].strip(),
                        'english': parts[1].strip(),
                        'type': 'proverb_pair'
                    })
                    continue
            
            # Pattern 3: Lines with "means" or "meaning"
            if re.search(r'\bmeans?\b|\bmeaning\b', line.lower()) and len(line) > 20:
                # Try to split on "means" or "meaning"
                for separator in [' means ', ' meaning ', ' means:', ' meaning:']:
                    if separator in line.lower():
                        idx = line.lower().find(separator)
                        igbo_part = line[:idx].strip()
                        english_part = line[idx + len(separator):].strip()
                        
                        if len(igbo_part) > 5 and len(english_part) > 5:
                            proverb_pairs.append({
                                'igbo': igbo_part,
                                'english': english_part,
                                'type': 'explained_proverb'
                            })
                            break
                continue
            
            # Pattern 4: Numbered lists
            numbered_match = re.match(r'^\d+\.\s*(.+)', line)
            if numbered_match and self.is_likely_igbo_content(line):
                content = numbered_match.group(1)
                if len(content) > 15:
                    # Check if next line might be translation
                    english_translation = ""
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line[0].isdigit() and len(next_line) > 10:
                            english_translation = next_line
                    
                    proverb_pairs.append({
                        'igbo': content,
                        'english': english_translation,
                        'type': 'numbered_proverb'
                    })
                continue
            
            # Pattern 5: Standalone Igbo text (if it contains multiple Igbo words)
            if self.is_likely_igbo_content(line) and len(line) > 15:
                igbo_word_count = sum(1 for word in self.igbo_words if word in line.lower())
                if igbo_word_count >= 3:
                    proverb_pairs.append({
                        'igbo': line,
                        'english': '',
                        'type': 'igbo_text'
                    })
        
        return proverb_pairs

    def categorize_content(self, content: str) -> List[str]:
        """Categorize the type of Igbo content"""
        content_lower = content.lower()
        categories = []
        
        if any(word in content_lower for word in ['wisdom', 'wise', 'elder', 'ancestor']):
            categories.append('wisdom')
        
        if any(word in content_lower for word in ['family', 'community', 'relationship', 'marriage']):
            categories.append('social')
        
        if any(word in content_lower for word in ['work', 'effort', 'success', 'achievement']):
            categories.append('work_ethics')
        
        if any(word in content_lower for word in ['god', 'chi', 'spirit', 'divine', 'prayer']):
            categories.append('spiritual')
        
        if any(word in content_lower for word in ['nature', 'earth', 'tree', 'river', 'animal']):
            categories.append('nature')
        
        if any(word in content_lower for word in ['truth', 'honest', 'lie', 'justice', 'right']):
            categories.append('morality')
        
        if any(word in content_lower for word in ['time', 'patience', 'wait', 'season']):
            categories.append('time_patience')
        
        return categories if categories else ['general']

# Enhanced list of Igbo proverb URLs
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
    "https://www.britannica.com/topic/Igbo",
    "https://www.nairaland.com/1555321/igbo-proverbs-meanings",
    "https://www.pulse.ng/lifestyle/food-travel-arts/igbo-proverbs-and-their-meanings/3zg8t1g"
]

# Initialize the extractor
extractor = IgboProverbExtractor()

# Scrape and clean text with enhanced extraction
raw_texts = []

print("🌍 Starting Igbo proverbs and wisdom extraction...")

for url in urls:
    try:
        # Add headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove unwanted elements more comprehensively
            for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "iframe", "form", "button"]):
                tag.decompose()
            
            # Extract title and metadata
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Unknown Title"
            
            # Try to get main content area
            main_content = None
            content_selectors = ['article', '.post-content', '.article-content', '.entry-content', '.content', 'main', '.post-body']
            
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    main_content = content_element
                    break
            
            # Fallback to body if no main content found
            if not main_content:
                main_content = soup.find('body')
            
            if main_content:
                text = main_content.get_text(separator="\n")
                lines = [line.strip() for line in text.splitlines()]
                clean_text = "\n".join([line for line in lines if line and len(line.strip()) > 10])
                
                if len(clean_text) > 300:  # Minimum content length
                    raw_texts.append({
                        "url": url,
                        "title": title_text,
                        "text": clean_text,
                        "domain": urlparse(url).netloc
                    })
                    print(f"✅ Successfully scraped: {title_text[:60]}...")
                else:
                    print(f"⚠️  Insufficient content from: {url}")
            else:
                print(f"❌ No content found: {url}")
        else:
            print(f"❌ Failed to fetch: {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
    
    # Be respectful - add delay between requests
    time.sleep(2)

print(f"\n📊 Successfully scraped {len(raw_texts)} sources")

# Enhanced proverb extraction
all_proverbs = []
for entry in raw_texts:
    print(f"🔍 Extracting from: {entry['title'][:50]}...")
    
    proverb_pairs = extractor.extract_proverb_pairs(entry["text"])
    
    for proverb in proverb_pairs:
        # Categorize the proverb
        full_text = f"{proverb['igbo']} {proverb['english']}"
        categories = extractor.categorize_content(full_text)
        
        # Create enhanced metadata
        enhanced_proverb = {
            'igbo_text': proverb['igbo'],
            'english_meaning': proverb['english'],
            'source_url': entry['url'],
            'source_title': entry['title'],
            'source_domain': entry['domain'],
            'extraction_type': proverb['type'],
            'categories': categories,
            'has_translation': bool(proverb['english'].strip()),
            'word_count': len(proverb['igbo'].split())
        }
        
        all_proverbs.append(enhanced_proverb)

print(f"📝 Extracted {len(all_proverbs)} Igbo proverbs and wisdom texts")

# Prepare enhanced documents for insertion
documents_to_insert = []

for idx, proverb in enumerate(all_proverbs):
    # Create comprehensive content for embedding
    if proverb['has_translation']:
        page_content = f"Igbo: {proverb['igbo_text']}\nEnglish: {proverb['english_meaning']}"
    else:
        page_content = proverb['igbo_text']
    
    # Only include substantial content
    if len(page_content.strip()) < 15:
        continue
    
    # Enhanced metadata
    metadata = {
        "igbo_text": proverb['igbo_text'],
        "english_meaning": proverb['english_meaning'],
        "source": proverb['source_url'],
        "source_title": proverb['source_title'],
        "domain": proverb['source_domain'],
        "categories": proverb['categories'],
        "extraction_type": proverb['extraction_type'],
        "has_translation": proverb['has_translation'],
        "word_count": proverb['word_count'],
        "content_type": "igbo_wisdom",
        "index": idx
    }
    
    doc = Document(
        page_content=page_content,
        metadata=metadata
    )
    documents_to_insert.append(doc)

print(f"📦 Prepared {len(documents_to_insert)} documents for vector store")

# Show samples
if documents_to_insert:
    print(f"\n📄 Sample proverbs:")
    for i, doc in enumerate(documents_to_insert[:5]):
        print(f"{i+1}. {doc.page_content[:100]}...")
        print(f"   Categories: {doc.metadata['categories']}")
        print(f"   Type: {doc.metadata['extraction_type']}")
        print()

# Insert into Astra vector DB with error handling
try:
    if documents_to_insert:
        inserted_ids = vector_store.add_documents(documents_to_insert)
        print(f"✅ Successfully inserted {len(inserted_ids)} Igbo wisdom documents")
    else:
        print("❌ No documents to insert!")
        exit(1)
except Exception as e:
    print(f"❌ Error inserting documents: {e}")
    exit(1)

# Enhanced testing with Igbo-relevant queries
test_queries = [
    "wisdom from elders",
    "family and community values",
    "hard work and success", 
    "patience and time",
    "truth and honesty",
    "Igbo traditional wisdom",
    "nwa (child) teachings",
    "chi and spirituality"
]

print(f"\n🔍 Testing search functionality with {len(test_queries)} Igbo-relevant queries:")

for query in test_queries:
    try:
        results = vector_store.similarity_search(query, k=3)
        print(f"\n🔎 Query: '{query}' → {len(results)} results")
        
        for i, res in enumerate(results, 1):
            igbo_text = res.metadata.get('igbo_text', '')
            english_meaning = res.metadata.get('english_meaning', '')
            categories = res.metadata.get('categories', ['unknown'])
            
            print(f"   {i}. Igbo: {igbo_text[:80]}...")
            if english_meaning:
                print(f"      English: {english_meaning[:80]}...")
            print(f"      Categories: {', '.join(categories)}")
            print(f"      Source: {res.metadata.get('domain', 'unknown')}")
            
    except Exception as e:
        print(f"❌ Error testing query '{query}': {e}")

# Summary statistics
print(f"\n📊 EXTRACTION SUMMARY:")
print(f"🌐 Sources scraped: {len(raw_texts)}")
print(f"📝 Proverbs extracted: {len(all_proverbs)}")
print(f"💾 Documents stored: {len(inserted_ids)}")
print(f"🔤 With translations: {sum(1 for p in all_proverbs if p['has_translation'])}")

# Category breakdown
category_counts = {}
for proverb in all_proverbs:
    for category in proverb['categories']:
        category_counts[category] = category_counts.get(category, 0) + 1

print(f"\n🏷️  CATEGORY BREAKDOWN:")
for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {category}: {count}")

print(f"\n🎉 Igbo wisdom extraction completed successfully!")
print(f"💡 The vector store now contains rich Igbo proverbs with English translations and cultural context.")