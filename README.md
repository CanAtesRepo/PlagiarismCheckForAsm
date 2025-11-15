# MSP430 Assembly Plagiarism Checker

A small Python tool to detect plagiarism between MSP430 `.asm` student submissions.

This project:
- Normalizes MSP430 assembly code (ignores labels, registers, immediates, etc.)
- Computes **logic-based similarity** using opcode n-gram Jaccard similarity
- Computes an additional **“anomaly-aware” score** based on raw text similarity
- Generates:
  - A **text report** with both logic & anomaly scores
  - An interactive **HTML report** where you can select a student and visually compare code & diffs

> 🧑‍🏫 Originally built for MSP430G2553 lab assignments, but can be adapted to other MSP430 setups.

---

## Features

- 🚫 **Label- and register-agnostic normalization**

  - Labels (`inner:`, `loop:`, `end_inner:`) are collapsed into `#BLOCK_START`
  - Registers (`R0`–`R15`) are normalized to `R`
  - Immediates and numeric literals are replaced by `IMM`

- 🧠 **Logic similarity**

  - Extracts opcode sequences from the normalized main loop
  - Uses opcode **n-gram Jaccard similarity** (default `k = 3`)
  - Threshold-based detection (e.g., report only pairs above 80%)

- 🕵️ **Anomaly-aware similarity (raw text)**

  - Compares **raw main loop code** (comments & whitespace trimmed)
  - Computes:
    - `logic_similarity` – opcode-level similarity (%)
    - `raw_similarity` – raw main-loop text similarity (%)
    - `anomaly_extra` – `raw_similarity - logic_similarity` (%)
  - `anomaly_extra` > 0 indicates “extra copying” in formatting, comments, spacing, etc.

- 📄 **Text report**

  - Shows how many matches each student has above the logic threshold
  - For each suspicious pair: both logic and anomaly scores

- 🌐 **HTML report**

  - Dropdown to select a student
  - See all their matches and similarity percentages
  - View:
    - Student’s own main-loop code
    - Matched student’s main-loop code
    - Side-by-side **HTML diff** (normalized) with color highlighting

---

## Folder Structure

Suggested layout:

```text
.
├─ asm_processing.py        # Extracts and normalizes main loop region
├─ plagiarism_core.py       # Logic similarity (opcodes, n-grams, Jaccard)
├─ anomaly_core.py          # Raw / anomaly-aware similarity
├─ student_io.py            # Loading student folders, pairwise similarity, text report
├─ html_report.py           # Interactive HTML report generator
├─ run_plagiarism_check.py  # Main entry point
├─ submissions/             # Student submissions (each folder = one student)
│   ├─ 202211013/
│   │   └─ main.asm
│   ├─ 202211014/
│   │   └─ main.asm
│   └─ ...
└─ results/
    ├─ plagiarism_results.txt
    └─ report.html
