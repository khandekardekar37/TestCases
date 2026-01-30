
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
from scipy.special import softmax

from config import (
    MODE,
    SEMANTIC_THRESHOLD,
    NLI_THRESHOLD,
    COMPLETENESS_THRESHOLD,
    ACCURACY_THRESHOLD,
)

# Generator is imported lazily to avoid circular issues
# (only used in integrated feedback loop)


# -----------------------------
# Models (loaded once)
# -----------------------------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L12-v2"
NLI_MODEL = "cross-encoder/nli-deberta-v3-small"

embedder = SentenceTransformer(EMBEDDING_MODEL)
nli_model = CrossEncoder(NLI_MODEL)


# ================================
# Load JSON requirements
# ================================
def load_requirements(json_path: Path):
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    requirements = []
    for section, items in data.items():
        for item in items:
            text = item.strip()
            if len(text) < 10:
                continue
            requirements.append({
                "text": text,
                "category": section
            })
    return requirements


# ================================
# Load test cases (TXT)
# ================================
def load_testcases(txt_path: Path):
    with txt_path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# ================================
# Core Validator (PUBLIC API)
# ================================
def validate_testcases(
    requirement_file: Path,
    testcase_file: Path,
):
    print("Loading requirements...")
    requirements = load_requirements(requirement_file)
    req_texts = [r["text"] for r in requirements]

    print("Loading test cases...")
    testcases = load_testcases(testcase_file)

    if not requirements or not testcases:
        raise ValueError("Empty requirements or test cases provided.")

    print("Generating embeddings...")
    req_emb = embedder.encode(
        req_texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    tc_emb = embedder.encode(
        testcases,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    sim_matrix = cosine_similarity(req_emb, tc_emb)

    coverage = {}
    missing = []
    accuracy_scores = []

    print("Validating coverage...")
    for i, req in enumerate(requirements):
        semantic_candidates = []

        # -------- Semantic filtering --------
        for j, tc in enumerate(testcases):
            if sim_matrix[i][j] >= SEMANTIC_THRESHOLD:
                semantic_candidates.append(tc)

        matches = []

        # -------- NLI validation --------
        for tc in semantic_candidates:
            logits = nli_model.predict([(tc, req["text"])])[0]
            probs = softmax(logits)

            entailment_score = float(probs[2])  # entailment
            if entailment_score >= NLI_THRESHOLD:
                matches.append({
                    "testcase": tc,
                    "entailment_score": round(entailment_score, 3)
                })
                accuracy_scores.append(entailment_score)

        if matches:
            coverage[req["text"]] = {
                "category": req["category"],
                "matches": matches
            }
        else:
            missing.append({
                "requirement": req["text"],
                "category": req["category"]
            })

    total = len(requirements)
    covered = len(coverage)

    completeness = (covered / total) * 100 if total else 0
    accuracy = (np.mean(accuracy_scores) * 100) if accuracy_scores else 0

    print("\n========== VALIDATION RESULT ==========")
    print(f"Total Requirements: {total}")
    print(f"Covered Requirements: {covered}")
    print(f"Missing Requirements: {len(missing)}")
    print(f"Completeness Percentage: {round(completeness, 2)}%")
    print(f"Accuracy Percentage: {round(accuracy, 2)}%")

    if missing:
        print("\nMissing Requirements:")
        for req in missing:
            print(f"- {req['requirement']} (Category: {req['category']})")

    # FEEDBACK LOOP (ONLY IN INTEGRATED MODE)
    # if (
    #     MODE == "INTEGRATED"
    #     and completeness < COMPLETENESS_THRESHOLD
    #     and accuracy >= ACCURACY_THRESHOLD
    #     and missing
    # ):
    #     print("\nCompleteness below threshold → triggering generator...")

    #     from generator.generator import run_generator  

    #     missing_dict = {}
    #     for m in missing:
    #         missing_dict.setdefault(m["category"], []).append(m["requirement"])

    #     missing_file = requirement_file.parent / "missing_requirements.json"
    #     with missing_file.open("w", encoding="utf-8") as f:
    #         json.dump(missing_dict, f, indent=2, ensure_ascii=False)

    #     run_generator(
    #         master_requirement_file=requirement_file,
    #         new_requirement_file=missing_file,
    #         output_testcase_file=testcase_file,
    #         hash_file=requirement_file.parent / "requirement_hash.txt"
    #     )

    #     print("Feedback loop completed: missing test cases generated.")

    # return {
    #     "coverage": coverage,
    #     "missing": missing,
    #     "completeness": round(completeness, 2),
    #     "accuracy": round(accuracy, 2),
    # }
    return coverage, missing, completeness, accuracy 




