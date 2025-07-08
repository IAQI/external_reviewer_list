### This script reads a CSV file of names, normalizes them, removes duplicates,
### and writes them to a LaTeX file for typesetting. It also handles discarded names
### that were duplicates or had issues.

### csv_to_latex_names.py
### vibe-coded by Christian Schaffner on 7 July 2025, with plenty of help from ChatGPT 4.1

### prompts: 
# 1. Create a python script that reads in the tqc-25-users-external-revs.csv file,
#    only keep given_name and family_name, discard double entries.
#    Then create a compilable latex file with a double column list of all names
#    sorted according to family_name.
#
# 2. Output the names that you discard as doubles.
#    Make sure you get rid of duplicates which are only differing in accents.
#
# 3. There are still some sorting issues.
#    Names like "de Wolf" or "van den Berg" should be sorted according to their last word,
#    ignoring the middle words.
#    Last names starting with an accent character should be sorted according to the character without the accent.
#    And single last names should be capitalized.
#
# 4. For the name you skip, don't write them in a separate file, but output them on the console.
#    Output both the name you keep, and the one you remove.
#    When one has accents, keep the one with the accents.
#
# 5. Now properly comment the code you wrote, so that it's easy to follow the code when inspecting it.
#
# 6. now use proper typing



# Standard library imports
import csv
import unicodedata
from typing import List, Tuple

def normalize_name(name: str) -> str:
    """
    Normalize a name by removing accents, converting to ASCII, stripping whitespace, and lowering case.
    Used for duplicate detection regardless of accents/case.
    """
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII').strip().lower()

def get_sort_key(family: str, given: str) -> Tuple[str, str, str]:
    """
    Return a tuple used for sorting names:
    - Sorts by the last word of the family name (ignoring accents and case)
    - Tie-breakers: full family name (no accents, lower), then given name (no accents, lower)
    This ensures correct alphabetical order for names like 'de Wolf' or 'van den Berg'.
    """
    def strip_accents(s):
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    words = family.split()
    last_word = words[-1] if words else family
    last_word_stripped = strip_accents(last_word).lower()
    family_stripped = strip_accents(family).lower()
    given_stripped = strip_accents(given).lower()
    return (last_word_stripped, family_stripped, given_stripped)

def capitalize_if_single_word(family: str) -> str:
    """
    Capitalize the family name if it is a single word (e.g., 'smith' -> 'Smith').
    Multi-word family names are left unchanged.
    """
    words = family.split()
    if len(words) == 1:
        return words[0].capitalize()
    return family

def read_unique_names(csv_path: str) -> List[Tuple[str, str]]:
    """
    Read the CSV file and return a sorted list of unique (family, given) name pairs.
    - Only keeps the version with accents if duplicates differ only by accents.
    - Prints to the console which name is kept and which is removed for each duplicate.
    - Sorting is done according to the custom sort key.
    """
    names_dict: dict[Tuple[str, str], Tuple[str, str]] = {}  # Maps normalized (family, given) to the original (family, given)
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            given = row['given_name'].strip()
            family = row['family_name'].strip()
            if not given or not family:
                continue  # Skip incomplete rows
            # Normalize for duplicate detection
            norm_given = normalize_name(given)
            norm_family = normalize_name(family)
            norm_pair = (norm_family, norm_given)
            orig_pair = (family, given)
            if norm_pair in names_dict:
                # If duplicate, decide which to keep: prefer the one with more accents
                prev_family, prev_given = names_dict[norm_pair]
                def count_accents(s):
                    # Count characters with a Unicode decomposition (i.e., accented)
                    return sum(1 for c in s if unicodedata.decomposition(c))
                prev_accents = count_accents(prev_family) + count_accents(prev_given)
                curr_accents = count_accents(family) + count_accents(given)
                if curr_accents > prev_accents:
                    print(f"Duplicate found: Keeping accented '{given} {family}', Removing '{prev_given} {prev_family}'")
                    names_dict[norm_pair] = (family, given)
                else:
                    print(f"Duplicate found: Keeping '{prev_given} {prev_family}', Removing '{given} {family}'")
            else:
                # First occurrence of this normalized name
                names_dict[norm_pair] = (family, given)
    # Prepare and sort the final list of names
    names_sorted = sorted(
        [(capitalize_if_single_word(family), given) for (family, given) in names_dict.values()],
        key=lambda x: get_sort_key(x[0], x[1])
    )
    return names_sorted

def write_latex(names: List[Tuple[str, str]], tex_path: str) -> None:
    """
    Write the sorted list of names to a LaTeX file, formatted as a double-column itemized list.
    Escapes LaTeX special characters in names to avoid compilation errors.
    """
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(r"""
\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{multicol}
\usepackage[left=2cm,right=2cm,top=2cm,bottom=2cm]{geometry}
\pagestyle{empty}
\begin{document}
\begin{center}
\section*{List of Names}
\end{center}
\begin{multicols}{2}
\begin{itemize}
""")
        for family, given in names:
            # Escape LaTeX special characters in names
            def latex_escape(s):
                return s.replace('\\', r'\textbackslash{}') \
                        .replace('&', r'\&') \
                        .replace('%', r'\%') \
                        .replace('$', r'\$') \
                        .replace('#', r'\#') \
                        .replace('_', r'\_') \
                        .replace('{', r'\{') \
                        .replace('}', r'\}') \
                        .replace('~', r'\textasciitilde{}') \
                        .replace('^', r'\textasciicircum{}')
            f.write(f"  \\item {latex_escape(given)} {latex_escape(family)}\n")
        f.write(r"""
\end{itemize}
\end{multicols}
\end{document}
""")

def write_discarded(discarded, out_path) -> None:
    # No longer needed; output handled in console
    pass

if __name__ == "__main__":
    # File paths for input and output
    csv_path = "data/tqc25-users-external-revs.csv"
    tex_path = "data/tqc25-users-external-revs-names.tex"
    # discarded_path is unused; kept for reference
    names = read_unique_names(csv_path)
    write_latex(names, tex_path)
    print(f"Wrote {len(names)} unique names to {tex_path}")
