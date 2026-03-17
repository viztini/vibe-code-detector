import os
import re
import sys
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Finding:
    category: str
    description: str
    weight: int

class AIDetector:
    def __init__(self):
        # Category weights
        self.weights = {
            'conversational': 25,
            'structural': 30,
            'stylistic': 20,
            'documentation': 25
        }
        
        # Keyword/Regex markers
        self.markers = [
            Finding('conversational', 'Presence of em dashes (—)', 15),
            Finding('stylistic', 'Presence of emojis (✨, 🚀, etc.)', 10),
            Finding('conversational', 'Polite/Conversational phrasing (Sure, Certainly, etc.)', 25),
            Finding('structural', 'Markdown code fence artifacts', 30),
            Finding('structural', 'Instructional boilerplate (Step 1, Step 2, etc.)', 20),
            Finding('structural', 'Standard Google/Sphinx docstring sections', 25),
            Finding('stylistic', '"Too Perfect" formatting (zero trailing whitespace/inconsistencies)', 15)
        ]

        self.re_em_dash = re.compile(r'—')
        self.re_emoji = re.compile(r'[\U00010000-\U0010ffff]')
        self.re_polite = re.compile(r'(?i)(sure|hope this helps|i have|the provided code|here is|certainly|let me know|you can use|feel free)')
        self.re_markdown = re.compile(r'```[a-z]*')
        self.re_steps = re.compile(r'(?i)(step\s*\d+|part\s*\d+|methodology|approach)')
        
        # Structural patterns for docstrings
        self.docstring_sections = [
            re.compile(r'(?i)args\s*:'),
            re.compile(r'(?i)returns\s*:'),
            re.compile(r'(?i)raises\s*:'),
            re.compile(r'(?i)attributes\s*:'),
            re.compile(r'(?i)parameters\s*:'),
            re.compile(r'(?i)yields\s*:')
        ]

    def analyze_file(self, file_path: str) -> Optional[Dict]:
        if not os.path.isfile(file_path):
            return None

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            return {'file': file_path, 'error': str(e)}

        context_findings = []
        score = 0

        # 1. Simple Regex Checks
        if self.re_em_dash.search(content):
            score += 15
            context_findings.append(self.markers[0])
            
        if self.re_emoji.search(content):
            score += 10
            context_findings.append(self.markers[1])

        polite_matches = self.re_polite.findall(content)
        if len(polite_matches) > 1:
            score += 25
            context_findings.append(self.markers[2])

        if self.re_markdown.search(content):
            score += 30
            context_findings.append(self.markers[3])

        step_matches = self.re_steps.findall(content)
        if len(step_matches) > 1:
            score += 20
            context_findings.append(self.markers[4])

        # 2. Advanced Structural Analysis
        doc_section_count = 0
        for section in self.docstring_sections:
            if section.search(content):
                doc_section_count += 1
        
        if doc_section_count >= 2:
            score += 25
            context_findings.append(self.markers[5])

        # 3. Documentation Density & Formatting
        comment_lines = 0
        code_lines = 0
        trailing_whitespace_count = 0
        in_docstring = False

        for line in lines:
            if line.endswith(' '):
                trailing_whitespace_count += 1
                
            stripped = line.strip()
            if not stripped:
                continue
            
            if stripped.startswith('#') or stripped.startswith('//'):
                comment_lines += 1
            elif stripped.startswith('"""') or stripped.startswith("'''") or stripped.startswith('/*'):
                comment_lines += 1
                if stripped.count('"""') == 1 or stripped.count("'''") == 1 or (stripped.startswith('/*') and not stripped.endswith('*/')):
                    in_docstring = not in_docstring
            elif in_docstring:
                comment_lines += 1
                if '"""' in stripped or "'''" in stripped or '*/' in stripped:
                    in_docstring = False
            else:
                code_lines += 1

        total_lines = comment_lines + code_lines
        if total_lines > 5:
            if trailing_whitespace_count == 0:
                score += 15
                context_findings.append(self.markers[6])

            ratio = comment_lines / total_lines
            if ratio > 0.45:
                score += 20
                context_findings.append(Finding('documentation', f'Extremely high doc-to-code ratio ({ratio:.1%})', 20))

        return {
            'file': file_path,
            'score': min(score, 100),
            'findings': context_findings
        }

def main():
    parser = argparse.ArgumentParser(description="Advanced AI Code Detector")
    parser.add_argument("path", help="Path to file or directory to scan")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed categorizations")
    args = parser.parse_args()

    detector = AIDetector()
    
    IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.vscode', '.idea', 'dist', 'build'}
    SUPPORTED_EXTENSIONS = {
        '.py', '.sh', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', 
        '.c', '.cpp', '.h', '.hpp', '.java', '.go', '.rs', '.rb', 
        '.php', '.cs', '.lua', '.md', '.txt'
    }

    paths = []
    if os.path.isfile(args.path):
        paths.append(args.path)
    elif os.path.isdir(args.path):
        for root, dirs, files in os.walk(args.path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                if any(file.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                    paths.append(os.path.join(root, file))
    
    paths.sort()

    print(f"\n{'FILE NAME':<45} | {'SCORE':<5} | {'CONFIDENCE'}")
    print("=" * 75)

    stats = {
        'total': 0,
        'flagged': 0,
        'sum_score': 0
    }

    for path in paths:
        result = detector.analyze_file(path)
        if not result or 'error' in result:
            continue
            
        stats['total'] += 1
        stats['sum_score'] += result['score']
        if result['score'] >= 50:
            stats['flagged'] += 1

        score = result['score']
        if score >= 70:
            confidence = "HIGH (Likely AI)"
        elif score >= 50:
            confidence = "MEDIUM (Suspected AI)"
        elif score >= 30:
            confidence = "LOW (Likely Human)"
        else:
            confidence = "MINIMAL (Human)"

        # Use relative path for cleaner output if scanning a directory
        display_path = os.path.relpath(path, args.path) if os.path.isdir(args.path) else os.path.basename(path)
        if len(display_path) > 42:
            display_path = "..." + display_path[-39:]

        print(f"{display_path:<45} | {score:<5} | {confidence}")
        
        if args.verbose and result['findings']:
            by_cat = {}
            for f in result['findings']:
                if f.category not in by_cat: by_cat[f.category] = []
                by_cat[f.category].append(f.description)
            
            for cat, desc_list in by_cat.items():
                print(f"  [{cat.upper()}]")
                for d in desc_list:
                    print(f"    - {d}")
            print("-" * 75)

    if stats['total'] > 0:
        avg_score = stats['sum_score'] / stats['total']
        print("\n" + "=" * 75)
        print("SCAN SUMMARY")
        print(f"Total Files Scanned: {stats['total']}")
        print(f"Flagged (Likely AI): {stats['flagged']}")
        print(f"Average AI Score:    {avg_score:.1f}")
        print("=" * 75)
    else:
        print("\nNo supported files found to scan.")

if __name__ == "__main__":
    main()
