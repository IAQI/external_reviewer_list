### This script reads a CSV file of names, normalizes them, removes duplicates,
### and writes them to a LaTeX file for typesetting. It also handles discarded names
### that were duplicates or had issues.

### csv_to_latex_names.py
### vibe-coded by Christian Schaffner on 7 July 2025, with plenty of help from ChatGPT 4.1

### prompts: 
# 1. Create a python script that reads in the tqc-25-users-external-revs.csv file, only keep given_name and family_name, discard double entries. Then create a compilable latex file with a double column list of all names sorted according to family_name.
# 2. output the names that you discard as doubles. Make sure you get rid of duplicates which are only differing in accents.
# 3. there are still some sorting issues. Names like "de Wolf" or "van den Berg" should be sorted according to their last word, ignoring the middle words. Last names starting with an accent character should be sorted according to the character without the accent. And single last names should be capitalized.


import csv
import unicodedata

def normalize_name(name):
    # Remove accents and normalize
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII').strip().lower()

def get_sort_key(family, given):
    # Remove accents for sorting
    def strip_accents(s):
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    # Split family name into words
    words = family.split()
    # Use last word for sorting
    last_word = words[-1] if words else family
    last_word_stripped = strip_accents(last_word).lower()
    # For tie-breaker, use full family name (stripped) and given name (stripped)
    family_stripped = strip_accents(family).lower()
    given_stripped = strip_accents(given).lower()
    return (last_word_stripped, family_stripped, given_stripped)

def capitalize_if_single_word(family):
    words = family.split()
    if len(words) == 1:
        return words[0].capitalize()
    return family

def read_unique_names(csv_path):
    names = set()
    discarded = set()
    seen = set()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            given = row['given_name'].strip()
            family = row['family_name'].strip()
            if not given or not family:
                continue
            norm_given = normalize_name(given)
            norm_family = normalize_name(family)
            norm_pair = (norm_family, norm_given)
            orig_pair = (family, given)
            if norm_pair in seen:
                discarded.add(orig_pair)
            else:
                seen.add(norm_pair)
                names.add(orig_pair)
    # Sort using custom key
    names_sorted = sorted(
        [(capitalize_if_single_word(family), given) for (family, given) in names],
        key=lambda x: get_sort_key(x[0], x[1])
    )
    discarded_sorted = sorted(discarded, key=lambda x: get_sort_key(x[0], x[1]))
    return names_sorted, discarded_sorted

def write_latex(names, tex_path):
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

def write_discarded(discarded, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        for family, given in discarded:
            f.write(f"{given},{family}\n")

if __name__ == "__main__":
    csv_path = "data/tqc25-users-external-revs.csv"
    tex_path = "data/tqc25-users-external-revs-names.tex"
    discarded_path = "data/tqc25-users-external-revs-discarded.csv"
    names, discarded = read_unique_names(csv_path)
    write_latex(names, tex_path)
    write_discarded(discarded, discarded_path)
    print(f"Wrote {len(names)} unique names to {tex_path}")
    print(f"Wrote {len(discarded)} discarded names to {discarded_path}")
