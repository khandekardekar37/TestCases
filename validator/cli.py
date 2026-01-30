import json
from json.tool import main
from pathlib import Path
from validator.validator import validate_testcases
from config import MODE
import sys
from config import (
    MODE,
    SEMANTIC_THRESHOLD,
    NLI_THRESHOLD,
    COMPLETENESS_THRESHOLD,
    ACCURACY_THRESHOLD,
    PROCESSED_SSD_FILE
)

from data_processing.raw_extraction import extract_docx_sections
from data_processing.data_classification import aggregate_important_requirements
from validator.validator import validate_testcases
from generator.generator import run_generator


# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.resolve()))


def run_cli():
    print("Standalone Validator CLI")

    print("Extracting SSD document...")
    ssd_docx_path = Path(input("Enter path of your SSD : ").strip())
    raw_ssd_data = extract_docx_sections(ssd_docx_path)


    # 2) Classify SSD data

    print("Classifying important requirements...")
    classified_data = aggregate_important_requirements(raw_ssd_data)

    PROCESSED_SSD_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PROCESSED_SSD_FILE.open("w", encoding="utf-8") as f:
        json.dump(classified_data, f, indent=2, ensure_ascii=False)

    print(f"SSD processed and saved to {PROCESSED_SSD_FILE}")

    tc_path = Path(input("Enter path to testcases TXT file: ").strip())

    if not PROCESSED_SSD_FILE.exists() or not tc_path.exists():
        print("Invalid file paths provided.")
        return

    # Standalone: feedback loop OFF
    coverage, missing, completeness, accuracy = validate_testcases(
        requirement_file=PROCESSED_SSD_FILE,
        testcase_file=tc_path
    )

    print("\nValidation completed in Standalone mode.")
    # print(f"Completeness: {completeness}%")
    # print(f"Accuracy: {accuracy}%")
    # print(f"Missing Requirements: {len(missing)}")

