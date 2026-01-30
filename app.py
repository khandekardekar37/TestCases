from pathlib import Path
import json

from config import (
    MODE,
    PROCESSED_SSD_FILE,
    REQUIREMENT_STORE_FILE,
    GENERATED_TESTCASES_FILE,
    VALIDATION_REPORT_FILE,
    MAX_FEEDBACK_RETRIES,
    COMPLETENESS_THRESHOLD
)

from data_processing.raw_extraction import extract_docx_sections
from data_processing.data_classification import aggregate_important_requirements
from validator.validator import validate_testcases
from generator.generator import run_generator


def main():
    print("Starting Integrated AI Testcase System Orchestrator...")

  
    #  Extract SSD from DOCX
    if not PROCESSED_SSD_FILE.exists() or PROCESSED_SSD_FILE.stat().st_size == 0:
        print("Extracting SSD document...")
        # ssd_docx_path = PROCESSED_SSD_FILE
        ssd_docx_path = Path("data/input/ssd.docx")
        raw_ssd_data = extract_docx_sections(ssd_docx_path)

        print("Classifying important requirements...")
        classified_data = aggregate_important_requirements(raw_ssd_data)

        PROCESSED_SSD_FILE.parent.mkdir(parents=True, exist_ok=True)
        with PROCESSED_SSD_FILE.open("w", encoding="utf-8") as f:
            json.dump(classified_data, f, indent=2, ensure_ascii=False)

        print(f"SSD processed and saved to {PROCESSED_SSD_FILE}")

 
    # print("Extracting SSD document...")
    # ssd_docx_path = Path("data/input/ssd.docx")
    # raw_ssd_data = extract_docx_sections(ssd_docx_path)


    # # 2) Classify SSD data

    # print("Classifying important requirements...")
    # classified_data = aggregate_important_requirements(raw_ssd_data)

    # PROCESSED_SSD_FILE.parent.mkdir(parents=True, exist_ok=True)
    # with PROCESSED_SSD_FILE.open("w", encoding="utf-8") as f:
    #     json.dump(classified_data, f, indent=2, ensure_ascii=False)

    # print(f"SSD processed and saved to {PROCESSED_SSD_FILE}")

 
    # 3) Initial Testcase Generation (ONLY ONCE)
  
    GENERATED_TESTCASES_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not GENERATED_TESTCASES_FILE.exists() or GENERATED_TESTCASES_FILE.stat().st_size == 0:
        print("No existing testcases found. Generating initial testcases...")

        run_generator(
            master_requirement_file=PROCESSED_SSD_FILE,
            new_requirement_file=None,  
            output_testcase_file=GENERATED_TESTCASES_FILE,
            hash_file=Path("data/output/requirements.hash"),
        )


    # 4) Validation + Feedback Loop

    feedback_attempt = 0
    completeness = 0
    accuracy = 0
    coverage = {}
    missing = []

    while feedback_attempt <= MAX_FEEDBACK_RETRIES:
        print(f"\nValidation attempt #{feedback_attempt + 1}")

        coverage, missing, completeness, accuracy = validate_testcases(
            requirement_file=PROCESSED_SSD_FILE,
            testcase_file=GENERATED_TESTCASES_FILE,
        )

        if completeness >= 95 or not missing:
            print(f"\nValidation passed with completeness {completeness}%")
            break

        feedback_attempt += 1
        if feedback_attempt > MAX_FEEDBACK_RETRIES:
            print("Max feedback attempts reached. Some requirements may still be missing.")
            break

        # Prepare missing requirements for generator

        print("Preparing missing requirements for regeneration...")

        missing_file = Path("data/output/new_requirements.json")
        missing_file.parent.mkdir(parents=True, exist_ok=True)

        grouped_missing = {}
        for item in missing:
            grouped_missing.setdefault(item["category"], []).append(item["requirement"])

        with missing_file.open("w", encoding="utf-8") as f:
            json.dump(grouped_missing, f, indent=2, ensure_ascii=False)

        # Generate testcases for missing only
        run_generator(
            master_requirement_file=PROCESSED_SSD_FILE,
            new_requirement_file=missing_file,
            output_testcase_file=GENERATED_TESTCASES_FILE,
            hash_file=Path("data/output/requirements.hash"),
        )

    # 5) Save Validation Report

    report = {
        "completeness": completeness,
        "accuracy": accuracy,
        "total_requirements": len(coverage) + len(missing),
        "covered": len(coverage),
        "missing": missing,
    }

    VALIDATION_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with VALIDATION_REPORT_FILE.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nValidation report saved to {VALIDATION_REPORT_FILE}")
    print(f"Final testcases file: {GENERATED_TESTCASES_FILE}")
    print("Orchestration complete!")


# if __name__ == "__main__":
#     if MODE != "INTEGRATED":
#         print("app.py should run only in INTEGRATED mode. Switch MODE in config.py")
#     else:
#         main()


if __name__ == "__main__":

    if MODE == "INTEGRATED":
        main()

    elif MODE == "STANDALONE":
        print("Running Validator in STANDALONE mode...\n")

        # Import here to avoid circular imports
        from validator.cli import run_cli
        run_cli()

    else:
        raise ValueError(
            "Invalid MODE in config.py. Use 'INTEGRATED' or 'STANDALONE'"
        )
