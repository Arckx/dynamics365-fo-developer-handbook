import re
import os

map_file = "D:/memory/dynamics365-fo-developer-handbook/scripts/renumber_map.txt"
input_file = "D:/memory/dynamics365-fo-developer-handbook/d365-learning-guide.md"
output_file = "D:/memory/dynamics365-fo-developer-handbook/d365-learning-guide-new.md"

# Load the map
mapping = []
with open(map_file, 'r') as f:
    for line in f:
        line = line.strip()
        if ' -> ' in line:
            old, new = line.split(' -> ')
            mapping.append((old, new))

# Sort mapping by length of old version descending to avoid partial matches
# (e.g., replacing 10.1 before 1.1 might cause issues, though usually \b handles it)
# More importantly, replacing "2.1" with "5.1" and then "1.2" with "2.1" would be bad if done sequentially on the same string.
# We should do it in one pass or use placeholders.

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# To avoid "double replacement" issues, we use a regex that matches any of our old numbers
# and then use a function to return the replacement.

# Create a regex pattern that matches any of the old versions as a whole word
# Order matters: longer ones first to match 10.1 before 10
pattern_parts = [re.escape(old) for old, new in sorted(mapping, key=lambda x: len(x[0]), reverse=True)]
pattern = r'\b(' + '|'.join(pattern_parts) + r')\b'

# Map for lookup
map_dict = dict(mapping)

def replace_func(match):
    old_val = match.group(1)
    return map_dict.get(old_val, old_val)

# Perform replacement for sections (e.g., 1.1, 2.1)
new_content = re.sub(pattern, replace_func, content)

# Now handle Chapter headings: "# Chapter 1" -> "# Chapter 1"
# The request says:
# - Chapter 1: Platform Architecture & AOT (1.1-1.2)
# ...
# The current file has "# Chapter 1 — The D365 F&O Developmental Landscape"
# We need to replace these main chapter headings too.

chapter_headings = {
    "Chapter 1": "Chapter 1: Platform Architecture & AOT",
    "Chapter 2": "Chapter 5: X++ Data Types & Variables", # This is tricky, they are shifting
    # Wait, the user wants new chapters.
}

# Actually, the user proposal RESTRUCTURES chapters.
# Chapter 1 (current) -> becomes Chapters 1, 2, 3, 4.
# Chapter 2 (current) -> becomes Chapters 5, 6, 7, 8.
# etc.

# Let's see how many "# Chapter X" we have.
lines = new_content.split('\n')
final_lines = []

# New Chapter Titles based on Proposal
new_chapters = {
    1: "Chapter 1: Platform Architecture & AOT",
    2: "Chapter 2: Models, Layers, Packages",
    3: "Chapter 3: Visual Studio Setup & Language Mindset",
    4: "Chapter 4: LCS & Dev Lifecycle",
    5: "Chapter 5: X++ Data Types & Variables",
    6: "Chapter 6: Control Flow & CRUD",
    7: "Chapter 7: Methods, Exceptions, Classes",
    8: "Chapter 8: VS Development & Activity",
    9: "Chapter 9: Table Design & EDTs",
    10: "Chapter 10: Form Architecture & CoC",
    11: "Chapter 11: Views & Lookups",
    12: "Chapter 12: Class Fundamentals & RunBase",
    13: "Chapter 13: Event Handlers & Command Pattern",
    14: "Chapter 14: Extensibility Deep Dive",
    15: "Chapter 15: Security Model",
    16: "Chapter 16: Data Entities",
    17: "Chapter 17: SSRS & Electronic Reporting",
    18: "Chapter 18: Batch Processing",
    19: "Chapter 19: SysTest Framework",
    20: "Chapter 20: LCS Deep Dive & CI/CD",
    21: "Chapter 21: Performance & SQL Tuning",
    22: "Chapter 22: Capstone Projects",
    23: "Chapter 23: Advanced X++ Patterns",
    24: "Chapter 24: Production Debugging",
    25: "Chapter 25: Power Platform & Copilot",
    26: "Chapter 26: Module Specialization",
    27: "Chapter 27: Advanced DevOps",
    28: "Chapter 28: Compliance & ISV",
    29: "Chapter 29: Workflow Architecture",
    30: "Chapter 30: Number Sequences",
    31: "Chapter 31: Form Patterns",
    32: "Chapter 32: LEM Patterns",
    33: "Chapter 33: Advanced Batch",
    34: "Chapter 34: Localization & Best Practices",
    35: "Chapter 35: Service Patterns"
}

# We need to insert these # Chapter X headings at the right places.
# 1.1 -> Chapter 1
# 1.3 -> Chapter 2
# 1.4 -> Chapter 3
# 1.6 -> Chapter 4
# 2.1 -> Chapter 5
# 2.3 -> Chapter 6
# 2.5 -> Chapter 7
# 2.8 -> Chapter 8
# 3.1 -> Chapter 9
# 4.1 -> Chapter 10
# 5.1 -> Chapter 11
# 6.1 -> Chapter 12
# 6.5 -> Chapter 13
# 7.1 -> Chapter 14
# 8.1 -> Chapter 15
# 9.1 -> Chapter 16
# 10.1 -> Chapter 17
# 11.1 -> Chapter 18
# 12.1 -> Chapter 19
# 13.1 -> Chapter 20
# 14.1 -> Chapter 21
# 15.1 -> Chapter 22
# 16.1 -> Chapter 23
# 18.1 -> Chapter 24
# 19.1 -> Chapter 25
# 20.1 -> Chapter 26
# 21.1 -> Chapter 27
# 22.1 -> Chapter 28
# 23.1 -> Chapter 29
# 24.1 -> Chapter 30
# 26.1 -> Chapter 31
# 27.1 -> Chapter 32
# 28.1 -> Chapter 33
# 29.1 -> Chapter 34
# 30.1 -> Chapter 35

chapter_starts = {
    "1.1": 1, "2.1": 2, "3.1": 3, "4.1": 4, # These are NEW section numbers
    "5.1": 5, "6.1": 6, "7.1": 7, "8.1": 8,
    "9.1": 9, "10.1": 10, "11.1": 11, "12.1": 12,
    "13.1": 13, "14.1": 14, "15.1": 15, "16.1": 16,
    "17.1": 17, "18.1": 18, "19.1": 19, "20.1": 20,
    "21.1": 21, "22.1": 22, "23.1": 23, "24.1": 24,
    "25.1": 25, "26.1": 26, "27.1": 27, "28.1": 28,
    "29.1": 29, "30.1": 30, "31.1": 31, "32.1": 32,
    "33.1": 33, "34.1": 34, "35.1": 35
}

# Remove existing # Chapter X lines
lines = [l for l in new_content.split('\n') if not re.match(r'^# Chapter \d+', l)]

final_lines = []
for line in lines:
    match = re.match(r'^## (\d+\.\d+)', line)
    if match:
        sec_num = match.group(1)
        if sec_num in chapter_starts:
            chap_num = chapter_starts[sec_num]
            final_lines.append(f"# {new_chapters[chap_num]}")
            final_lines.append("")
    final_lines.append(line)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(final_lines))
