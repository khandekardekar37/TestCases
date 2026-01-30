1. Project Title : Test Case Generator + Validator
An end-to-end application that extracts requirements from SSD documents, generates test cases, validates them against the SSD using semantic similarity, and continuously improves through a feedback loop.

2. Problem Statement
why this project is needed?.
 -Manual test case creation is time-consuming and error-prone
 -SSDs vary in structure and language
 -Existing tools lack semantic validation and feedback learning

3. Solution Overview
 -Extracts requirements from SSD (.docx)
 -Generates structured test cases
 -Validates test cases semantically against SSD
 -Calculates coverage and accuracy
 -Improves output using feedback loop

4. End-to-End Flow
  1) SSD upload
    -Text extraction 
    -Requirement classification & filtering
    -Requirement JSON generation

  2) Test case generation
    -taking input as SSD
    -Test Case Generation
    -testcases Storing

  3) Test Case Validation
    -Semantic validation
    -Coverage scoring
    -Feedback-based refinement

5. Project Structure
how the code is organized.

project-root/
│
├── data_processing/
│   └── row_extraction.py
|   |__ data_classification.py
|
├── generator/
│   └── generator.py
|
├── validator/
│   └── validator.py
|   |__ cli.py
|
├── data/
│   ├── Input/
|   |      |__SSD.docx
|   |
│   |
|   └── output
|           |__json_data
|           |        |__classified_data.json
|           |        |__new_requirements.json
|           |        |__validation_report.json
|           |__testcases
|                    |__testcases.txt
|                    |__requirements.hash
|                 
|
├── requirements.txt
└── README.md


6. Technologies/Framework Used
Python 3.x
NLP: Transformers, Sentence-Transformers
Testcase Generation: langchain, langgraph

7. Installation Steps
cd project-root
pip install -r requirements.txt

8. How to Run the Project
set the mode from config.py file 
mode = "INTEGRATED" or "STANDALONE"
python -m app

if mode is STANDALONE
Inputs
-SSD file (.docx)
-testcases.txt 

if the mode is INTEGRATED
Input 
-SSD.docx
Output
-data\output\testcases\testcases.txt

9. Validation Logic
-taking SSD and test cases 
-Semantic similarity is calculated
-Thresholds decide pass / partial / fail
-Coverage percentage is generated

10. Feedback Loop
-Validation gaps are fed back to generator
-Low-quality test cases are regenerated
-System improves iteratively

11. Use Cases
-Banking & Loan Systems
-Insurance Platforms

12. Limitations & Future Enhancements
-Depends on SSD quality
-cant understand the SSD

-Session Management
-Prioritize Testcases
-Dynamic Output Format
-ML Model Reinforcement

13. Author / Contact
Author: Divya Khandekar
Contact: d.khandekar@tcs.com