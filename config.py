
from pathlib import Path

# 1) MODE

# Options: "STANDALONE" | "INTEGRATED"
MODE = "INTEGRATED"  


# VALIDATOR THRESHOLDS

SEMANTIC_THRESHOLD = 0.55
NLI_THRESHOLD = 0.6

# Final decision thresholds (%)
COMPLETENESS_THRESHOLD = 80.0
ACCURACY_THRESHOLD = 75.0


# FEEDBACK LOOP

MAX_FEEDBACK_RETRIES = 2

# GENERATOR FLAGS

FORCE_REGENERATE = False

# 4) Data / Output Paths

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"


PROCESSED_SSD_FILE = OUTPUT_DIR / "json_data/classified_file.json"          
REQUIREMENT_STORE_FILE = OUTPUT_DIR / "json_data/classified_file.json"   
NEW_REQUIREMENT_FILE = OUTPUT_DIR / "json_data/new_requirement.json"       
HASH_FILE = OUTPUT_DIR / "testcases/requirement_hash.txt"
GENERATED_TESTCASES_FILE = OUTPUT_DIR / "testcases/testcases.txt"
VALIDATION_REPORT_FILE = OUTPUT_DIR / "json_data/validation_report.json"
