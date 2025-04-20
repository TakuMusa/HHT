# Supplementary Data & Code for "The Semantic and Narrative Functions of Arabic Vocabulary in Hikayat Hang Tuah"

## Project Overview

This repository provides supplementary materials for the article analyzing the functional roles and systemic interactions of 60 core Arabic loanwords (ALs) within the classical Malay epic, *Hikayat Hang Tuah* (HHT). The analysis is based on the Kassim Ahmad (1997) romanized edition (~172,000 tokens).

**Author:** [Talaibek Musaev]
**Contact:** [musaev at um.edu.my]
**Article Link/DOI:** [Link to be added upon publication/DOI]

## Contents

This repository contains the following key supplementary files:

1.  **`Appendix B_all_collocations_ORI.csv`**:
    *   **Description:** The **full dataset** of statistically significant collocates (Log-Likelihood LL ≥ 10.83, p < 0.001) for the 60 core ALs analyzed in the article. This file provides the raw data supporting the summarized Appendix B and the analysis in Section 5.
    *   **Format:** CSV (Comma-Separated Values), UTF-8 encoded.
    *   **Columns:** `Root Word`, `Collocate`, `Direction` (Left/Right), `LL Score`, `p-value`, `Example KWIC` (illustrative context).
    *   **Method:** Calculated using [Mention Tool: e.g., Custom Python script / AntConc] with a ±20 word window. However, in the analisys the +/-5 was used.

2.  **`Appendix C_combined_kwic_results_ORI.txt`**:
    *   **Description:** The **complete Key Word In Context (KWIC)** concordance data for all occurrences of the 60 core ALs within the HHT corpus. This file was used for the detailed qualitative contextual analysis presented in the article.
    *   **Format:** Plain text (.txt), UTF-8 encoded.
    *   **Structure:** Includes initial summary statistics followed by detailed KWIC listings for each keyword.
    *   **Context Window:** ±20 words.

3.  **`MalayStemmer.py`**:
    *   **Description:** The **Python 3 script** used for lemmatizing the Malay text of HHT. It implements rule-based stemming according to standard Malay morphology, incorporating morphophonological rules (incl. nasalization) and a dictionary of 73 exceptions (defined within the script) to enhance accuracy for core terms and irregular forms.
    *   **Usage:** Refer to comments within the script for detailed logic.
    *   **Dependencies:** Developed and tested using **Python 3.12.3 (conda-forge distribution, 64-bit)**. The script uses standard Python libraries (`re`, `os`, `collections`, `argparse`, `datetime`) and `pandas` (for saving to Excel in the main execution block). Ensure `pandas` is installed (`pip install pandas`). The core `MalayStemmer` class itself has minimal external dependencies beyond standard Python 3.

## Methodology Note

The core methodology, including AL validation, selection criteria, lemmatization details, and statistical thresholds, is described in Section 3 of the main article. The lemmatization accuracy for the 60 core ALs exceeds 95%.

## License

*   Data files (`.csv`, `.txt`) are provided under the [e.g., Creative Commons Attribution 4.0 International (CC BY 4.0)] license.
*   Code file (`.py`) is provided under the [e.g., MIT License].

## Citation

Please cite the main article if using these materials. You may also cite this dataset/code repository directly:

[Musaev, Talaaibek]. [2025]. *Supplementary Data and Code for 'The Semantic and Narrative Functions of Arabic Vocabulary in Hikayat Hang Tuah'*. GitHub Repository. [URL of your repository] *(Optionally add DOI if obtained via Zenodo)*.
