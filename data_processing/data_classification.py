import json
import re
from collections import defaultdict
from sentence_transformers import SentenceTransformer, util



# Load MiniLM Model
MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)


# Reference Testable Requirements
REFERENCE_REQUIREMENTS = [
    "The system must allow users to perform an action",
    "The system should validate input",
    "The system must display correct data",
    "The system should block the operation",
    "The backend must process the request",
    "The system should generate output",
    "The system must update the database",
    "The system should trigger a warning"
]

REFERENCE_EMBEDDINGS = model.encode(
    REFERENCE_REQUIREMENTS,
    normalize_embeddings=True
)


# POSITIVE SIGNALS

IMPORTANT_KEYWORDS = re.compile(
    r"\b("
    r"must|should|shall|will|allow|ensure|validate|display|update|"
    r"block|trigger|generate|calculate|store|filter|select|recognize|"
    r"apply|accept|reject|map|process|retrieve|save|check|"
    r"complete|define|execute|integrate|monitor|confirm"
    r")\b",
    re.IGNORECASE
)


# NEGATIVE SIGNALS

NON_TESTABLE_PATTERNS = re.compile(
    r"\b("
    r"overview|introduction|diagram|illustrates|appendix|example|"
    r"note|details|concept|theory|summary|context|prototype"
    r")\b",
    re.IGNORECASE
)



def expand_bullets(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines

# ================================
# Importance Detection
# ================================
def is_important_requirement(text, semantic_threshold=0.4):
    text = text.strip()

    if len(text.split()) < 6:
        return False

    if NON_TESTABLE_PATTERNS.search(text):
        return False

    if IMPORTANT_KEYWORDS.search(text):
        return True

    embedding = model.encode(text, normalize_embeddings=True)
    score = util.cos_sim(
        embedding,
        REFERENCE_EMBEDDINGS
    ).max().item()

    return score >= semantic_threshold


# Classification Logic
def aggregate_important_requirements(structured_ssd: dict) -> dict:
    
    aggregated = defaultdict(list)

    for section in structured_ssd.get("sections", []):
        feature = (section.get("feature") or "").lower()
        sub_section = section.get("sub_section") or "General"

        for text in section.get("content", []):
            if not isinstance(text, str):
                continue

            text = text.strip()
            if not text:
                continue

            if not is_important_requirement(text):
                continue

            cat = sub_section.lower()

            if "functional" in cat:
                aggregated["Functional"].append(text)
            elif "non-functional" in cat:
                aggregated["Non-Functional"].append(text)
            elif "technical" in feature:
                aggregated["Technical"].append(text)
            elif "business" in feature:
                aggregated["Business"].append(text)
            else:
                aggregated["General"].append(text)

    for key in [
        "Functional",
        "Non-Functional",
        "Business",
        "Technical"
        "General"
    ]:
        aggregated.setdefault(key, [])
    
    cleaned_output = {
        category: requirements
        for category, requirements in aggregated.items()
        if requirements  # keep only non-empty
    }

    return cleaned_output

    # return dict(aggregated)


# ---------------- CLI SUPPORT ----------------
if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Please provide structured SSD JSON file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = Path(input_file).stem + "_classified.json"

    with open(input_file, "r", encoding="utf-8") as f:
        structured_ssd = json.load(f)

    classified = aggregate_important_requirements(structured_ssd)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(classified, f, indent=2, ensure_ascii=False)

    print(f"Requirements classified → {output_file}")



















# import json
# import re
# import sys
# from collections import defaultdict
# from sentence_transformers import SentenceTransformer, util
# from nltk.tokenize import sent_tokenize
# from pathlib import Path

# import nltk

# def ensure_nltk():
#     try:
#         nltk.data.find("tokenizers/punkt")
#         nltk.data.find("tokenizers/punkt_tab")
#     except LookupError:
#         print("Downloading required NLTK resources...")
#         nltk.download("punkt")
#         nltk.download("punkt_tab")

# ensure_nltk()

# # --------------------------------
# # NLTK setup
# # --------------------------------
# # nltk.download("punkt", quiet=True)

# # --------------------------------
# # Load MiniLM Model
# # --------------------------------
# MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"
# model = SentenceTransformer(MODEL_NAME)

# # --------------------------------
# # Reference Testable Requirements
# # --------------------------------
# REFERENCE_REQUIREMENTS = [
#     "The system must allow users to perform an action",
#     "The system should validate input",
#     "The system must display correct data",
#     "The system should block the operation",
#     "The backend must process the request",
#     "The system should generate output",
#     "The system must update the database",
#     "The system should trigger a warning"
# ]

# REFERENCE_EMBEDDINGS = model.encode(
#     REFERENCE_REQUIREMENTS,
#     normalize_embeddings=True
# )

# # --------------------------------
# # POSITIVE SIGNALS
# # --------------------------------
# IMPORTANT_KEYWORDS = re.compile(
#     r"\b("
#     r"must|should|shall|will|allow|ensure|validate|display|update|"
#     r"block|trigger|generate|calculate|store|filter|select|recognize|"
#     r"apply|accept|reject|map|process|retrieve|save|check|"
#     r"execute|integrate|monitor|confirm|append|pull"
#     r")\b",
#     re.IGNORECASE
# )

# # --------------------------------
# # NEGATIVE SIGNALS
# # --------------------------------
# NON_TESTABLE_PATTERNS = re.compile(
#     r"\b("
#     r"overview|introduction|diagram|illustrates|appendix|example|"
#     r"note|details|concept|theory|summary|context|prototype|"
#     r"date|status|project id"
#     r")\b",
#     re.IGNORECASE
# )

# # --------------------------------
# # Importance Detection
# # --------------------------------
# def is_important_requirement(text, semantic_threshold=0.2):
#     text = text.strip()

#     if len(text.split()) < 0:
#         return False

#     if NON_TESTABLE_PATTERNS.search(text):
#         return False

#     if IMPORTANT_KEYWORDS.search(text):
#         return True

#     embedding = model.encode(text, normalize_embeddings=True)
#     score = util.cos_sim(embedding, REFERENCE_EMBEDDINGS).max().item()

#     return score >= semantic_threshold


# # --------------------------------
# # Sentence Extraction
# # --------------------------------
# def extract_sentences(text: str):
#     sentences = sent_tokenize(text)
#     return [
#         s.strip() for s in sentences
#         if len(s.split()) >= 20
#     ]


# def expand_bullets(text):
#     """
#     Converts:
#     'check below buttons\nupdate\ndelete\nprint'
#     into:
#     ['check below buttons', 'update', 'delete', 'print']
#     """
#     lines = [l.strip() for l in text.split("\n") if l.strip()]
#     return lines
# # --------------------------------
# # Classification Logic
# # --------------------------------
# def aggregate_important_requirements(structured_ssd: dict) -> dict:
#     aggregated = defaultdict(list)

#     for section in structured_ssd.get("sections", []):
#         feature = (section.get("feature") or "").lower()
#         sub_section = (section.get("sub_section") or "").lower()

#         for block in section.get("content", []):
#             if not isinstance(block, str):
#                 continue

#             sentences = extract_sentences(block)

#             for sentence in sentences:
#                 if not is_important_requirement(sentence):
#                     continue

#                 # -------- CATEGORY DECISION --------
#                 if "functional" in sub_section:
#                     aggregated["Functional"].append(sentence)

#                 elif "non-functional" in sub_section:
#                     aggregated["Non-Functional"].append(sentence)

#                 elif (
#                     "backend" in sentence.lower()
#                     or "frontend" in sentence.lower()
#                     or "database" in sentence.lower()
#                     or "etl" in sentence.lower()
#                 ):
#                     aggregated["Technical"].append(sentence)

#                 elif "business" in feature:
#                     aggregated["Business"].append(sentence)

#                 else:
#                     aggregated["General"].append(sentence)

#     # Ensure keys always exist
#     for key in [
#         "Functional",
#         "Non-Functional",
#         "Business",
#         "Technical",
#         "General"
#     ]:
#         aggregated.setdefault(key, [])

#     cleaned_output = {
#         category: requirements
#         for category, requirements in aggregated.items()
#         if requirements  # keep only non-empty
#     }

#     return cleaned_output

#     # return dict(aggregated)


# # --------------------------------
# # MAIN RUNNER (NO HARDCODED FILES)
# # --------------------------------
# if __name__ == "__main__":

#     if len(sys.argv) < 2:
#         print("❌ Please provide SSD JSON file path")
#         print("Usage: python classification.py <ssd_json_file>")
#         sys.exit(1)

#     INPUT_FILE = sys.argv[1]
#     OUTPUT_FILE = Path(INPUT_FILE).stem + "_classified.json"

#     with open(INPUT_FILE, "r", encoding="utf-8") as f:
#         structured_ssd = json.load(f)

#     classified = aggregate_important_requirements(structured_ssd)

#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(classified, f, indent=2, ensure_ascii=False)

#     print(f"✅ Requirements classified successfully → {OUTPUT_FILE}")
