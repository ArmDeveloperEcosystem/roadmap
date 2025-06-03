#!/usr/bin/env python3
"""
Script to count and list all Learning Paths with the "Hugging Face" tag in the tools_software_languages section of _index.md.
Clones the main branch of the arm-learning-paths repository, scans all _index.md files, and outputs a markdown table with the Learning Path title and category.
"""

import os
import sys
import re
import yaml
import tempfile
import shutil
import subprocess
from collections import namedtuple

REPO_URL = "https://github.com/ArmDeveloperEcosystem/arm-learning-paths.git"
REPO_DIR = "arm-learning-paths"
OUTPUT_MD = "huggingface_learning_paths.md"

LearningPath = namedtuple('LearningPath', ['title', 'category', 'path'])

def extract_front_matter(file_path):
    """Extract YAML front matter from a markdown file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if match:
                front_matter_text = match.group(1)
                try:
                    return yaml.safe_load(front_matter_text)
                except Exception as e:
                    print(f"Error parsing YAML in {file_path}: {e}", file=sys.stderr)
            return {}
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return {}

def find_huggingface_learning_paths(repo_dir):
    """Find all Learning Paths with the 'Hugging Face' tag in tools_software_languages."""
    lp_dir = os.path.join(repo_dir, "content", "learning-paths")
    results = []
    if not os.path.exists(lp_dir):
        print(f"Learning Paths directory not found: {lp_dir}", file=sys.stderr)
        return results
    for category in os.listdir(lp_dir):
        category_path = os.path.join(lp_dir, category)
        if not os.path.isdir(category_path):
            continue
        for lp in os.listdir(category_path):
            lp_path = os.path.join(category_path, lp)
            index_md = os.path.join(lp_path, "_index.md")
            if os.path.isdir(lp_path) and os.path.isfile(index_md):
                fm = extract_front_matter(index_md)
                # DEBUG: print the tools_software_languages field for inspection
                print(f"DEBUG: {category}/{lp} tools_software_languages: {fm.get('tools_software_languages')}")
                tools_tags = fm.get('tools_software_languages', [])
                tags = []
                if isinstance(tools_tags, str):
                    tags = [t.strip() for t in tools_tags.split(',')]
                elif isinstance(tools_tags, list):
                    tags = [str(t).strip() for t in tools_tags]
                # DEBUG: print the parsed tags
                print(f"DEBUG: {category}/{lp} parsed tags: {tags}")
                if any(tag.lower() == "hugging face" for tag in tags):
                    title = fm.get('title', lp)
                    print(f"FOUND: {title} in {category}")
                    results.append(LearningPath(title=title, category=category, path=f"{category}/{lp}"))
    return results

def write_markdown_table(learning_paths, output_file):
    with open(output_file, 'w') as f:
        f.write("# Hugging Face Learning Paths\n\n")
        f.write("| Title | Category |\n")
        f.write("|-------|----------|\n")
        for lp in learning_paths:
            url = f"https://learn.arm.com/learning-paths/{lp.path}"
            f.write(f"| [{lp.title}]({url}) | {lp.category} |\n")
    print(f"Markdown report written to {output_file}")

def main():
    # Clone or update the repo in a temp dir
    temp_dir = tempfile.mkdtemp()
    repo_path = os.path.join(temp_dir, REPO_DIR)
    try:
        print(f"Cloning {REPO_URL}...")
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, repo_path], check=True)
        print("Scanning for Learning Paths with 'Hugging Face' tag...")
        huggingface_lps = find_huggingface_learning_paths(repo_path)
        print(f"DEBUG: Found {len(huggingface_lps)} learning paths with 'Hugging Face' tag.")
        for lp in huggingface_lps:
            print(f"DEBUG: Adding to table: {lp.title} | {lp.category} | {lp.path}")
        # Write to the correct output location
        output_dir = os.path.join(os.getcwd(), "reports", "hugging-face")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "huggingface-learning-paths.md")
        write_markdown_table(huggingface_lps, output_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
