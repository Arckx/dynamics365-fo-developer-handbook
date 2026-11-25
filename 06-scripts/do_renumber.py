import re

input_file = "D:/memory/dynamics365-fo-developer-handbook/d365-learning-guide.md"
output_file = "D:/memory/dynamics365-fo-developer-handbook/d365-learning-guide.md"

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Define mapping for section numbers based on user's proposed structure
# Current sections:
# 1.1, 1.2 -> 1.1, 1.2
# 1.3 -> 2.1
# 1.4, 1.5 -> 3.1, 3.2
# 1.6, 1.7 -> 4.1, 4.2
# 1.8 -> 4.3 (Activity)
# 2.1, 2.2 -> 5.1, 5.2
# 2.3, 2.4 -> 6.1, 6.2
# 2.5, 2.6, 2.7 -> 7.1, 7.2, 7.3
# 2.8, 2.9 -> 8.1, 8.2
# 3.1 - 3.8 -> 9.1 - 9.8
# 4.1 - 4.5 -> 10.1 - 10.5
# 5.1 - 5.3 -> 11.1 - 11.3
# 6.1 - 6.4 -> 12.1 - 12.4
# 6.5 - 6.7 -> 13.1 - 13.3
# 7.1 - 7.8 -> 14.1 - 14.8
# 8.1 - 8.11 -> 15.1 - 15.11
# 9.1 - 9.8 -> 16.1 - 16.8
# 10.1 - 10.12 -> 17.1 - 17.12
# 11.1 - 11.9 -> 18.1 - 18.9
# 12.1 - 12.6 -> 19.1 - 19.6 (Wait, 12.4 is duplicated in original, let's map carefully)
# 13.1 - 13.8 -> 20.1 - 20.8
# 14.1 - 14.6 -> 21.1 - 21.6
# 15.1 - 15.5 -> 22.1 - 22.5
# 16.1 - 16.4 -> 23.1 - 23.4
# 17.1 - 17.6 -> 23.5 - 23.10 (Wait, user says Chapter 23 includes 16.1-16.4, 17.1-17.6)
# 18.1 - 18.4 -> 24.1 - 24.4
# 19.1 - 19.4 -> 25.1 - 25.4
# 20.1 - 20.4 -> 26.1 - 26.4
# 21.1 - 21.3 -> 27.1 - 27.3
# 22.1 - 22.5 -> 28.1 - 28.5
# 23.1 - 23.5 -> 29.1 - 29.5
# 24.1 - 24.4 -> 30.1 - 30.4
# 25.1 - 25.4 -> (Wait, 25.x in original? Let's check)
# 26.1 - 26.8 -> 31.1 - 31.8
# 27.1 - 27.6 -> 32.1 - 32.6
# 28.1 - 28.6 -> 33.1 - 33.6
# 29.1 - 29.3 -> 34.1 - 34.3
# 30.1 - 30.5 -> 35.1 - 35.5

mapping = {
    # Ch 1
    "1.1": "1.1", "1.2": "1.2",
    # Ch 2
    "1.3": "2.1",
    # Ch 3
    "1.4": "3.1", "1.5": "3.2",
    # Ch 4
    "1.6": "4.1", "1.7": "4.2", "1.8": "4.3",
    # Ch 5
    "2.1": "5.1", "2.2": "5.2",
    # Ch 6
    "2.3": "6.1", "2.4": "6.2",
    # Ch 7
    "2.5": "7.1", "2.6": "7.2", "2.7": "7.3",
    # Ch 8
    "2.8": "8.1", "2.9": "8.2",
    # Ch 9
    "3.1": "9.1", "3.2": "9.2", "3.3": "9.3", "3.4": "9.4", "3.5": "9.5", "3.6": "9.6", "3.7": "9.7", "3.8": "9.8",
    # Ch 10
    "4.1": "10.1", "4.2": "10.2", "4.3": "10.3", "4.4": "10.4", "4.5": "10.5",
    # Ch 11
    "5.1": "11.1", "5.2": "11.2", "5.3": "11.3",
    # Ch 12
    "6.1": "12.1", "6.2": "12.2", "6.3": "12.3", "6.4": "12.4",
    # Ch 13
    "6.5": "13.1", "6.6": "13.2", "6.7": "13.3",
    # Ch 14
    "7.1": "14.1", "7.2": "14.2", "7.3": "14.3", "7.4": "14.4", "7.5": "14.5", "7.6": "14.6", "7.7": "14.7", "7.8": "14.8",
    # Ch 15
    "8.1": "15.1", "8.2": "15.2", "8.3": "15.3", "8.4": "15.4", "8.5": "15.5", "8.6": "15.6", "8.7": "15.7", "8.8": "15.8", "8.9": "15.9", "8.10": "15.10", "8.11": "15.11",
    # Ch 16
    "9.1": "16.1", "9.2": "16.2", "9.3": "16.3", "9.4": "16.4", "9.5": "16.5", "9.6": "16.6", "9.7": "16.7", "9.8": "16.8",
    # Ch 17
    "10.1": "17.1", "10.2": "17.2", "10.3": "17.3", "10.4": "17.4", "10.5": "17.5", "10.6": "17.6", "10.7": "17.7", "10.8": "17.8", "10.9": "17.9", "10.10": "17.10", "10.11": "17.11", "10.12": "17.12",
    # Ch 18
    "11.1": "18.1", "11.2": "18.2", "11.3": "18.3", "11.4": "18.4", "11.5": "18.5", "11.6": "18.6", "11.7": "18.7", "11.8": "18.8", "11.9": "18.9",
    # Ch 19
    "12.1": "19.1", "12.2": "19.2", "12.3": "19.3", "12.4": "19.4", "12.5": "19.5", "12.6": "19.6",
    # Ch 20
    "13.1": "20.1", "13.2": "20.2", "13.3": "20.3", "13.4": "20.4", "13.5": "20.5", "13.6": "20.6", "13.7": "20.7", "13.8": "20.8",
    # Ch 21
    "14.1": "21.1", "14.2": "21.2", "14.3": "21.3", "14.4": "21.4", "14.5": "21.5", "14.6": "21.6",
    # Ch 22
    "15.1": "22.1", "15.2": "22.2", "15.3": "22.3", "15.4": "22.4", "15.5": "22.5",
    # Ch 23
    "16.1": "23.1", "16.2": "23.2", "16.3": "23.3", "16.4": "23.4",
    "17.1": "23.5", "17.2": "23.6", "17.3": "23.7", "17.4": "23.8", "17.5": "23.9", "17.6": "23.10",
    # Ch 24
    "18.1": "24.1", "18.2": "24.2", "18.3": "24.3", "18.4": "24.4",
    # Ch 25
    "19.1": "25.1", "19.2": "25.2", "19.3": "25.3", "19.4": "25.4",
    # Ch 26
    "20.1": "26.1", "20.2": "26.2", "20.3": "26.3", "20.4": "26.4",
    # Ch 27
    "21.1": "27.1", "21.2": "27.2", "21.3": "27.3",
    # Ch 28
    "22.1": "28.1", "22.2": "28.2", "22.3": "28.3", "22.4": "28.4", "22.5": "28.5",
    # Ch 29
    "23.1": "29.1", "23.2": "29.2", "23.3": "29.3", "23.4": "29.4", "23.5": "29.5",
    # Ch 30
    "24.1": "30.1", "24.2": "30.2", "24.3": "30.3", "24.4": "30.4",
    # Ch 31
    "26.1": "31.1", "26.2": "31.2", "26.3": "31.3", "26.4": "31.4", "26.5": "31.5", "26.6": "31.6", "26.7": "31.7", "26.8": "31.8",
    # Ch 32
    "27.1": "32.1", "27.2": "32.2", "27.3": "32.3", "27.4": "32.4", "27.5": "32.5", "27.6": "32.6",
    # Ch 33
    "28.1": "33.1", "28.2": "33.2", "28.3": "33.3", "28.4": "33.4", "28.5": "33.5", "28.6": "33.6",
    # Ch 34
    "29.1": "34.1", "29.2": "34.2", "29.3": "34.3",
    # Ch 35
    "30.1": "35.1", "30.2": "35.2", "30.3": "35.3", "30.4": "35.4", "30.5": "35.5"
}

# New Chapter titles
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

chapter_starts = {
    "1.1": 1, "2.1": 2, "3.1": 3, "4.1": 4,
    "5.1": 5, "6.1": 6, "7.1": 7, "8.1": 8,
    "9.1": 9, "10.1": 10, "11.1": 11, "12.1": 12,
    "13.1": 13, "14.1": 14, "15.1": 15, "16.1": 16,
    "17.1": 17, "18.1": 18, "19.1": 19, "20.1": 20,
    "21.1": 21, "22.1": 22, "23.1": 23, "24.1": 24,
    "25.1": 25, "26.1": 26, "27.1": 27, "28.1": 28,
    "29.1": 29, "30.1": 30, "31.1": 31, "32.1": 32,
    "33.1": 33, "34.1": 34, "35.1": 35
}

# Step 1: Replace all section references in text (e.g. "Chapter 2.1" -> "Chapter 5.1", or just "2.1" -> "5.1", etc.)
# Sort keys by length descending to replace longer strings first
sorted_keys = sorted(mapping.keys(), key=len, reverse=True)

# We want to replace section numbers in references like "Chapter X.Y", "Section X.Y", "X.Y", etc.
# To be safe and precise, let's do replacements using regex word boundaries.
# But wait! If we replace "1.3" with "2.1", we must ensure we don't mess up other things.
# Let's create a regex pattern for all mapped keys.
pattern = r'\b(' + '|'.join(re.escape(k) for k in sorted_keys) + r')\b'

def replace_section(match):
    k = match.group(1)
    return mapping[k]

content_updated = re.sub(pattern, replace_section, content)

# Step 2: Remove old Chapter headers (`# Chapter ...`)
lines = [l for l in content_updated.split('\n') if not re.match(r'^# Chapter \d+', l)]

# Step 3: Insert new Chapter headers before their starting sections (`## X.Y`)
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

print("Renumbering complete!")
