# generator/generator.py

import json
import os
import hashlib
from pathlib import Path
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from config import FORCE_REGENERATE


# LLM (UNCHANGED)

print("Loading model...")
llm = ChatOllama(model="mistral", temperature=0.2, streaming=False)

# Utility Functions (UNCHANGED)
def load_json(path: Path):
    if path.exists():
        try:
            data = path.read_text(encoding="utf-8").strip()
            if not data:
                return {}
            return json.loads(data)
        except json.JSONDecodeError:
            print(f"Warning: {path} contains invalid JSON. Using empty dict instead.")
            return {}
    return {}

def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def compute_hash(data):
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

def load_hash(path: Path):
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return None

def save_hash(path: Path, hash_value):
    path.write_text(hash_value, encoding="utf-8")

def hepler(text):
    sections = {"Positive": [], "Negative": [], "Boundary": []}
    current = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Positive"):
            current = "Positive"
        elif line.startswith("Negative"):
            current = "Negative"
        elif line.startswith("Boundary"):
            current = "Boundary"
        elif current and line:
            sections[current].append(line)
    return sections

# Graph State (UNCHANGED)
class State(dict):
    section: str
    text: str
    testcases: dict

# Generation Node (UNCHANGED)
def generate_testcases_node(state: State):
    print(f"Generating test cases for section: {state['section']}")
    prompt = ChatPromptTemplate.from_template("""
You are a Quality Assurance Engineer. Your task is to generate **comprehensive test cases** for the given requirements.

    Guidelines:

    1. Cover **positive**, **negative**, and **boundary/edge cases** wherever applicable.
    2. Keep sentences concise and self-contained.
    3. Do not skip unrelated generic test cases that may be required for security, risk, or permission checks.
    4. Do NOT include sections like "Test Steps", "Preconditions", or "Expected Result".
    5. Output must be ONLY a numbered list (1., 2., 3., ...).
    6. Group test cases ONLY under the following three sections and in this exact order:
     - Positive
     - Negative
     - Boundary
    
    7. Do Not create sections such as :
     - Functional Test Cases
     - Business Test Cases
     - Technical Test Cases
     - Non-Functional Test Cases
     - Data Test Cases

    8. Requirement type (Functional, business, technocal, security, data, non-functional) MUST NOT be used for grouping. All Testcases must be classified ONLY as positive, negative or boundary.                                  
                    

    for example :                                          
     Requirements: 
     Additional Driver Age Validation
     Restrictions in the NBL Application
        
    would generate below testcases:
    
    Positive
       1. Verify that the system allows creation of an additional driver when the entered age is 18 or above.
       2. Verify that clicking the Reset button allows the user to re-enter valid data.

    Negative
       1. Verify that the system blocks additional driver creation when the entered age is below 18.
       2. Verify that the system displays the error message "Applicant Age not in Range" when the entered age is below 18.

    Boundary
        1. Verify that the system allows additional driver creation when the entered age is exactly 18.
        2. Verify that the system blocks additional driver creation when the entered age is exactly 17.
    
    
    Requirement:
    {input_text}
""")
    chain = prompt | llm
    result = chain.invoke({"input_text": state["text"]})
    print("Testcases++++++++++++++++",result)
    state["testcases"][state["section"]] = result.content
    return state

# LangGraph (UNCHANGED)
graph = StateGraph(State)
graph.add_node("generate", generate_testcases_node)
graph.set_entry_point("generate")
graph.add_edge("generate", END)
app = graph.compile()

# PUBLIC ENTRY FUNCTION (NEW)
def run_generator(
    master_requirement_file: Path,
    new_requirement_file: Path | None,
    output_testcase_file: Path,
    hash_file: Path
):
    """
    Called by app.py or CLI
    """

    stored_requirements = load_json(master_requirement_file)
    new_requirements = load_json(new_requirement_file) if new_requirement_file else {}

    generate_master = not output_testcase_file.exists() or FORCE_REGENERATE
    generate_new = bool(new_requirements)

    if not generate_master and not generate_new:
        print("Nothing new to generate.")
        return

    all_testcases = {}

    # --- Master ---
    if generate_master:
        for section, requirements in stored_requirements.items():
            combined_text = "\n".join(requirements)
            result = app.invoke({
                "section": section,
                "text": combined_text,
                "testcases": all_testcases
            })
            all_testcases.update(result["testcases"])

    # --- Missing only ---
    if generate_new:
        for section, requirements in new_requirements.items():
            combined_text = "\n".join(requirements)
            result = app.invoke({
                "section": section,
                "text": combined_text,
                "testcases": all_testcases
            })
            all_testcases.update(result["testcases"])

            stored_requirements.setdefault(section, [])
            for req in requirements:
                if req not in stored_requirements[section]:
                    stored_requirements[section].append(req)

    merged = {"Positive": [], "Negative": [], "Boundary": []}
    for section_output in all_testcases.values():
        split = hepler(section_output)
        for k in merged:
            merged[k].extend(split[k])

    mode = "w" if generate_master else "a"
    with output_testcase_file.open(mode, encoding="utf-8") as f:
        for section in ["Positive", "Negative", "Boundary"]:
            f.write(f"{section}:\n")
            for i, tc in enumerate(merged[section], 1):
                f.write(f"{i}. {tc.lstrip('0123456789. ')}\n")
            f.write("\n")

    save_json(master_requirement_file, stored_requirements)
    save_hash(hash_file, compute_hash(stored_requirements))

    if new_requirement_file:
        save_json(new_requirement_file, {})

    print("Test cases generated successfully.")
