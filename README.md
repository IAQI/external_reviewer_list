# external_reviewer_list

This repository provides tools to generate a front matter with an alphabetically sorted list of external reviewers, based on a HotCRP user export.

## Main Script: `csv_to_latex_names.py`

This script processes a CSV file of reviewer names and produces a LaTeX file with a double-column, alphabetically sorted list of unique names. It also outputs a CSV file of discarded (duplicate) names.

### Features
- **Reads** the CSV file, extracting only `given_name` and `family_name` fields.
- **Normalizes** names by removing accents and converting to lowercase, ensuring duplicates (even those differing only by accents) are detected.
- **Removes duplicates** and keeps track of discarded (duplicate) names.
- **Sorts** names alphabetically by the last word of the family name (ignoring middle words and accents), and capitalizes single-word family names.
- **Outputs**:
  - A LaTeX file with the sorted list of unique names, formatted for typesetting.
  - A CSV file listing the discarded (duplicate) names.
- **Prints** a summary of how many unique and discarded names were processed.

### Usage

Run the script from the repository root:

```bash
python csv_to_latex_names.py
```

By default, it expects the input CSV at `data/tqc25-users-external-revs.csv` and writes output files to the `data/` directory.

