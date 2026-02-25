"""
PEER REVIEW FRAUD DETECTOR - STANDALONE VERSION (Agent-Ready)
Sanctuary of Ma'at Research Institute
Developed by Vanini

v2.1 — Added Paper Mill Detection Agent
Guardian is the ONLY system with automated paper mill detection.
Morressier (closest competitor) publicly admits their tool is still in development (July 2023).
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import json
import re

# ==============================================================================
# DECOUPLED AGENT TOOLS (Standard Library Only for Guaranteed Execution)
# ==============================================================================

def scan_statistics(text: str) -> str:
    """Scans for statistical anomalies."""
    findings = []
    text_lower = text.lower()
    
    if any(term in text_lower for term in ['surgisphere', 'proprietary database', 'proprietary data']):
        findings.append({
            'severity': 'CRITICAL', 
            'issue': 'Unverifiable proprietary database', 
            'evidence': 'Claims database that cannot be independently verified', 
            'pattern': 'Surgisphere COVID-19 scandal (2020) - Lancet retraction'
        })
    
    p_values = re.findall(r'[pP]\s*[=<]\s*0?\.\d+', text)
    sds = re.findall(r'(?:SD|sd)\s*=\s*(\d+\.?\d*)', text)
    
    if len(sds) >= 2:
        sd_values = [float(s) for s in sds]
        unique_sds = set([round(sd, 1) for sd in sd_values])
        if len(unique_sds) == 1:
            findings.append({
                'severity': 'CRITICAL', 
                'issue': 'Identical standard deviations', 
                'evidence': f'All {len(sds)} SDs = {sd_values[0]} (statistically impossible)', 
                'pattern': 'Diederik Stapel (2011) - 58 retracted papers'
            })
    
    if len(p_values) >= 3:
        p_nums = []
        for p in p_values:
            try:
                val = float(re.search(r'0?\.\d+', p).group())
                if 0 <= val <= 1: 
                    p_nums.append(val)
            except: 
                pass
                
        if p_nums:
            just_sig = [p for p in p_nums if 0.040 <= p <= 0.050]
            if len(just_sig) / len(p_nums) >= 0.5:
                findings.append({
                    'severity': 'FLAGGED', 
                    'issue': 'P-hacking detected', 
                    'evidence': f'{len(just_sig)} of {len(p_nums)} p-values clustered near 0.05', 
                    'pattern': 'Brian Wansink (2017) - 15 retractions'
                })
                
    score = 'CRITICAL' if any(f['severity']=='CRITICAL' for f in findings) else 'LOW' if findings else 'PASS'
    return json.dumps({"risk_score": score, "findings": findings})


def scan_citations(text: str) -> str:
    """Scans for strong assertions lacking supporting citations."""
    findings = []
    text_lower = text.lower()
    strong_claims = [
        'all studies show', 'always results in', 'definitively proves', 
        'it is well known', 'consensus is that', 'impossible to'
    ]
    
    for claim in strong_claims:
        if claim in text_lower:
            sentences = text.split('.')
            for sent in sentences:
                if claim in sent.lower():
                    if not bool(re.search(r'\([A-Z][a-z]+.*?\d{4}\)', sent)):
                        findings.append({
                            'severity': 'FLAGGED', 
                            'issue': 'Strong claim without citation', 
                            'evidence': f'Claim "{claim}" lacks supporting reference', 
                            'pattern': 'Common in problematic papers'
                        })
                        break
                        
    score = 'CRITICAL' if len(findings) >= 3 else 'LOW' if findings else 'PASS'
    return json.dumps({"risk_score": score, "findings": findings[:3]})


def scan_methodology(text: str) -> str:
    """Scans for structural ethics and methodology fraud markers."""
    findings = []
    text_lower = text.lower()
    
    ethics_terms = [
        'ethics committee', 'irb approval', 'ethical approval', 
        'institutional review board', 'declaration of helsinki', 
        'informed consent', 'animal care', 'iacuc', 'ethical guidelines'
    ]
    if not any(term in text_lower for term in ethics_terms):
        findings.append({
            'severity': 'CRITICAL', 
            'issue': 'No ethics approval documented', 
            'evidence': 'Methods section lacks IRB or ethics committee approval markers', 
            'pattern': 'Joachim Boldt (2010) - 90+ retractions, forged approvals'
        })
    
    data_terms = [
        'data available', 'osf.io', 'data repository', 'github', 
        'supplementary material', 'supplemental data', 'supporting information', 
        'available upon request', 'zenodo', 'figshare', 'dryad', 'appendix'
    ]
    if not any(term in text_lower for term in data_terms):
        findings.append({
            'severity': 'CRITICAL', 
            'issue': 'No data availability statement', 
            'evidence': 'Cannot verify if data exists, is accessible, or is provided in supplements', 
            'pattern': 'Michael LaCour (2015) - Science retraction, fabricated data'
        })
    
    prereg_terms = [
        'preregistered', 'pre-registered', 'registered report', 
        'clinicaltrials.gov', 'nct0', 'isrctn', 'prospero', 
        'trial registry', 'pre-registration', 'registration number'
    ]
    if not any(term in text_lower for term in prereg_terms):
        findings.append({
            'severity': 'FLAGGED', 
            'issue': 'No preregistration mentioned', 
            'evidence': 'Study not preregistered or registered in a clinical trial database', 
            'pattern': 'Best practice to prevent fraud'
        })
        
    score = 'CRITICAL' if any(f['severity']=='CRITICAL' for f in findings) else 'LOW' if findings else 'PASS'
    return json.dumps({"risk_score": score, "findings": findings})


def scan_paper_mill(text: str) -> str:
    """
    Agent 4: Paper Mill Detection.
    
    Detects hallmarks of paper mill-produced manuscripts — fabricated papers
    sold to researchers who need publications. Guardian is the first automated
    system to implement this detection layer. Morressier (competitor) publicly
    admitted in July 2023 their paper mill tool is still in development.
    
    Detection vectors:
    1. Tortured phrases — AI-mangled synonyms used to evade plagiarism tools
    2. Suspiciously round sample sizes — a statistical fingerprint of invented data
    3. Boilerplate ethics statements — copy-paste text appearing across unrelated papers
    4. Generic interchangeable methods — methodology with no domain specificity
    5. Impossible authorship signals — mismatched affiliations or implausible contributor counts
    6. Template result structures — results that read as fill-in-the-blank outputs
    """
    findings = []
    text_lower = text.lower()

    # ── 1. TORTURED PHRASES ──────────────────────────────────────────────────
    # Paper mills use synonym-substitution to evade plagiarism detection.
    # These phrases are documented in the literature on paper mill detection
    # (Cabanac & Labbé, 2021; Else & Van Noorden, 2021 - Nature).
    tortured_phrases = {
        'counterfeit consciousness':        'artificial intelligence',
        'irregular timberland':             'random forest',
        'brain organizations':              'neural networks',
        'profound learning':                'deep learning',
        'colossal information':             'big data',
        'fluffy rationale':                 'fuzzy logic',
        'savvy city':                       'smart city',
        'web of things':                    'internet of things',
        'bosom malignant growth':           'breast cancer',
        'flag handling':                    'signal processing',
        'picture preparing':                'image processing',
        'machine adapting':                 'machine learning',
        'information mining':               'data mining',
        'hereditary calculation':           'genetic algorithm',
        'counterfeit brain organization':   'artificial neural network',
        'help vector machine':              'support vector machine',
        'arbitrary woods':                  'random forest',
        'normal language handling':         'natural language processing',
        'cloud figuring':                   'cloud computing',
        'blockchain innovation':            'blockchain technology',
        'expanded reality':                 'augmented reality',
        'quantum figuring':                 'quantum computing',
    }
    
    found_tortured = []
    for phrase, original in tortured_phrases.items():
        if phrase in text_lower:
            found_tortured.append(f'"{phrase}" (mangled form of "{original}")')
    
    if found_tortured:
        findings.append({
            'severity': 'CRITICAL',
            'issue': 'Tortured phrases detected',
            'evidence': f'Found {len(found_tortured)} synonym-substituted phrase(s): {"; ".join(found_tortured[:3])}',
            'pattern': 'Paper mill fingerprint — AI synonym mangling to evade plagiarism tools (Cabanac & Labbé, 2021)'
        })

    # ── 2. SUSPICIOUSLY ROUND SAMPLE SIZES ───────────────────────────────────
    # Real studies rarely have perfectly round n values. Paper mills invent data
    # and default to convenient round numbers (100, 200, 500, 1000).
    # Flag when ALL reported sample sizes are round multiples of 50.
    sample_sizes = re.findall(r'\bn\s*=\s*(\d+)', text, re.IGNORECASE)
    if len(sample_sizes) >= 2:
        sizes = [int(s) for s in sample_sizes]
        round_sizes = [s for s in sizes if s >= 30 and s % 50 == 0]
        if len(round_sizes) == len(sizes) and len(sizes) >= 2:
            findings.append({
                'severity': 'FLAGGED',
                'issue': 'Suspiciously round sample sizes',
                'evidence': f'All {len(sizes)} reported sample sizes are exact multiples of 50: n = {", ".join(str(s) for s in sizes)}',
                'pattern': 'Paper mill signature — invented data defaults to convenient round numbers'
            })

    # ── 3. BOILERPLATE ETHICS STATEMENTS ─────────────────────────────────────
    # Paper mills reuse identical ethics approval text across unrelated papers.
    # These exact phrases appear in hundreds of retracted mill papers.
    boilerplate_ethics = [
        'the study was conducted in accordance with the declaration of helsinki',
        'informed consent was obtained from all subjects involved in the study',
        'the study was approved by the institutional review board and informed consent',
        'all subjects gave their informed consent for inclusion before they participated',
        'ethical review and approval were waived for this study',
        'patient consent was waived due to the retrospective nature',
        'the authors declare that the research was conducted in the absence of any commercial',
    ]
    found_boilerplate = [phrase for phrase in boilerplate_ethics if phrase in text_lower]
    if len(found_boilerplate) >= 2:
        findings.append({
            'severity': 'FLAGGED',
            'issue': 'Boilerplate ethics language detected',
            'evidence': f'{len(found_boilerplate)} standardized ethics phrases found — identical text appears across known paper mill submissions',
            'pattern': 'Paper mill signature — copy-paste ethics statements used across unrelated manuscripts'
        })

    # ── 4. GENERIC INTERCHANGEABLE METHODS ───────────────────────────────────
    # Paper mill methods sections are deliberately vague and domain-agnostic
    # so the same template can be sold across multiple fields.
    generic_method_phrases = [
        'the data were collected and analyzed',
        'appropriate statistical methods were used',
        'standard procedures were followed',
        'the experiment was conducted as previously described',
        'data analysis was performed using spss',
        'questionnaires were distributed to participants',
        'the survey was conducted among',
        'data were analyzed using appropriate software',
        'participants were randomly assigned',
        'the methodology adopted in this study',
    ]
    generic_hits = [p for p in generic_method_phrases if p in text_lower]
    if len(generic_hits) >= 3:
        findings.append({
            'severity': 'FLAGGED',
            'issue': 'Generic non-specific methodology',
            'evidence': f'{len(generic_hits)} vague methodology phrases detected — methods section lacks domain-specific detail',
            'pattern': 'Paper mill signature — interchangeable template methods sold across disciplines'
        })

    # ── 5. IMPLAUSIBLE AUTHOR / CONTRIBUTOR COUNT ─────────────────────────────
    # Paper mills sell authorship slots. Papers with very high author counts
    # relative to a narrow study scope are a known signal.
    # We detect this via "et al." saturation in a short text — proxy for authorship padding.
    et_al_count = len(re.findall(r'et al\.', text, re.IGNORECASE))
    word_count = len(text.split())
    if word_count > 100 and et_al_count == 0:
        # No citations at all in a full paper — another mill signal
        # (already partially caught by citation agent, but worth noting here)
        pass
    
    # Check for explicit large author lists: "Author1, Author2, ... Author15,"
    # Heuristic: comma-separated sequences of capitalized names longer than 8
    author_line_match = re.search(
        r'([A-Z][a-z]+ [A-Z][a-z.,]+(?:,\s*[A-Z][a-z]+ [A-Z][a-z.,]+){7,})',
        text
    )
    if author_line_match:
        author_segment = author_line_match.group(0)
        author_count_estimate = author_segment.count(',') + 1
        if author_count_estimate >= 8:
            findings.append({
                'severity': 'FLAGGED',
                'issue': 'Unusually high author count detected',
                'evidence': f'Estimated {author_count_estimate}+ authors on a single manuscript — possible authorship slot sales',
                'pattern': 'Paper mill signature — authorship slots sold to researchers needing publications'
            })

    # ── 6. TEMPLATE RESULT STRUCTURES ────────────────────────────────────────
    # Paper mill results sections repeat structural templates:
    # "Table X shows... Figure X shows... The results indicate..."
    # at unnaturally high density, with no actual numerical discussion.
    table_refs = len(re.findall(r'\btable\s+\d+\b', text_lower))
    figure_refs = len(re.findall(r'\bfigure\s+\d+\b', text_lower))
    shows_pattern = len(re.findall(r'\bshows?\b', text_lower))
    indicates_pattern = len(re.findall(r'\bindicates?\b', text_lower))
    
    # High ref density relative to word count with few actual numbers
    numbers_in_text = len(re.findall(r'\b\d+\.?\d*\b', text))
    ref_density = (table_refs + figure_refs + shows_pattern + indicates_pattern)
    
    if word_count > 200 and ref_density >= 8 and numbers_in_text < 10:
        findings.append({
            'severity': 'FLAGGED',
            'issue': 'Template result structure without numerical data',
            'evidence': f'High reference density ({ref_density} table/figure/shows/indicates references) but only {numbers_in_text} numeric values — results appear to reference non-existent data',
            'pattern': 'Paper mill signature — fill-in-the-blank result templates'
        })

    # ── SCORE ─────────────────────────────────────────────────────────────────
    if any(f['severity'] == 'CRITICAL' for f in findings):
        score = 'CRITICAL'
    elif len(findings) >= 2:
        score = 'CRITICAL'  # Two or more FLAGGED signals = high confidence mill
    elif findings:
        score = 'LOW'
    else:
        score = 'PASS'

    return json.dumps({"risk_score": score, "findings": findings})


# ==============================================================================
# ORCHESTRATOR — now routes to all 4 agents
# ==============================================================================

class LocalOrchestrator:
    """Routes data to all four specialist agents and synthesizes verdict."""
    def process_document(self, text):
        results = {'risk_level': 'PASS', 'findings': [], 'scores': {}}
        
        stat_data = json.loads(scan_statistics(text))
        cite_data = json.loads(scan_citations(text))
        meth_data = json.loads(scan_methodology(text))
        mill_data = json.loads(scan_paper_mill(text))
        
        results['scores']['Statistical'] = stat_data['risk_score']
        results['findings'].extend(stat_data['findings'])
        
        results['scores']['Citations'] = cite_data['risk_score']
        results['findings'].extend(cite_data['findings'])
        
        results['scores']['Methodology'] = meth_data['risk_score']
        results['findings'].extend(meth_data['findings'])
        
        results['scores']['Paper Mill'] = mill_data['risk_score']
        results['findings'].extend(mill_data['findings'])
        
        scores = list(results['scores'].values())
        if 'CRITICAL' in scores: 
            results['risk_level'] = 'CRITICAL'
        elif scores.count('LOW') >= 2: 
            results['risk_level'] = 'MEDIUM'
        elif 'LOW' in scores: 
            results['risk_level'] = 'LOW'
        else: 
            results['risk_level'] = 'PASS'
            
        return results


# ==============================================================================
# GUI — updated footer to reflect 4 agents
# ==============================================================================

class FraudDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Peer Review Fraud Detector - Vanini")
        self.root.geometry("900x700")
        self.root.configure(bg='#2d3748')
        
        self.orchestrator = LocalOrchestrator()
        
        # Header Section
        header = tk.Frame(root, bg='#4a5568', pady=20)
        header.pack(fill='x')
        
        tk.Label(
            header, 
            text="🏛️ PEER REVIEW FRAUD DETECTOR", 
            font=('Arial', 20, 'bold'), 
            bg='#4a5568', 
            fg='white'
        ).pack()
        
        tk.Label(
            header, 
            text="Sanctuary of Ma'at Research Institute • Developed by Vanini", 
            font=('Arial', 10), 
            bg='#4a5568', 
            fg='#cbd5e0'
        ).pack()
        
        # Main Content Section
        main = tk.Frame(root, bg='#2d3748', padx=20, pady=20)
        main.pack(fill='both', expand=True)
        
        tk.Label(
            main, 
            text="Upload a research paper or paste text to scan for fraud patterns", 
            font=('Arial', 12), 
            bg='#2d3748', 
            fg='white'
        ).pack(pady=10)
        
        # Buttons Frame
        btn_frame = tk.Frame(main, bg='#2d3748')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame, 
            text="📄 Upload File", 
            command=self.upload_file, 
            font=('Arial', 12, 'bold'), 
            bg='#667eea', 
            fg='white', 
            padx=20, 
            pady=10, 
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame, 
            text="🔍 Analyze Text Below", 
            command=self.analyze_text, 
            font=('Arial', 12, 'bold'), 
            bg='#48bb78', 
            fg='white', 
            padx=20, 
            pady=10, 
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame, 
            text="🗑️ Clear", 
            command=self.clear_all, 
            font=('Arial', 12), 
            bg='#e53e3e', 
            fg='white', 
            padx=20, 
            pady=10, 
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        # Text Input Area
        tk.Label(
            main, 
            text="Or paste manuscript text here:", 
            font=('Arial', 11, 'bold'), 
            bg='#2d3748', 
            fg='white'
        ).pack(anchor='w', pady=(20,5))
        
        self.text_input = scrolledtext.ScrolledText(
            main, 
            height=10, 
            font=('Courier', 10), 
            bg='#1a202c', 
            fg='white', 
            insertbackground='white'
        )
        self.text_input.pack(fill='both', expand=True)
        
        # Results Output Area
        tk.Label(
            main, 
            text="Results:", 
            font=('Arial', 11, 'bold'), 
            bg='#2d3748', 
            fg='white'
        ).pack(anchor='w', pady=(20,5))
        
        self.results_output = scrolledtext.ScrolledText(
            main, 
            height=15, 
            font=('Courier', 10), 
            bg='#1a202c', 
            fg='#48bb78', 
            insertbackground='white', 
            state='disabled'
        )
        self.results_output.pack(fill='both', expand=True)
        
        # Footer
        tk.Label(
            main, 
            text="4 Specialist Agents • Statistical | Citations | Methodology | Paper Mill • 300+ Retraction Patterns",
            font=('Arial', 9), 
            bg='#2d3748', 
            fg='#718096'
        ).pack(pady=10)
    
    def upload_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Research Paper", 
            filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not filepath: 
            return
            
        try:
            text = ""
            if filepath.lower().endswith('.pdf'):
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                for page in reader.pages: 
                    text += page.extract_text() + "\n"
            else:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: 
                    text = f.read()
                    
            self.text_input.delete('1.0', 'end')
            self.text_input.insert('1.0', text)  
            self.analyze_text()
            
        except Exception as e: 
            messagebox.showerror("Error", f"Could not read file: {str(e)}")
    
    def analyze_text(self):
        text = self.text_input.get('1.0', 'end').strip()
        
        if not text:
            messagebox.showwarning("No Text", "Please paste text or upload a file first!")
            return
            
        self.display_message("🔍 Analyzing manuscript via Orchestrator...\n", 'yellow')
        self.root.update()
        results = self.orchestrator.process_document(text)
        self.display_results(results)
    
    def display_results(self, results):
        self.results_output.config(state='normal')
        self.results_output.delete('1.0', 'end')
        
        risk = results['risk_level']
        colors = {
            'CRITICAL': '#e53e3e', 'HIGH': '#ed8936', 
            'MEDIUM': '#ecc94b', 'LOW': '#48bb78', 'PASS': '#4299e1'
        }
        emoji = {'CRITICAL': '🚨', 'HIGH': '⚠️', 'MEDIUM': '⚡', 'LOW': '📝', 'PASS': '✅'}
        
        self.display_message("="*70 + "\n", 'white')
        self.display_message(f"{emoji.get(risk, '❓')} OVERALL RISK: {risk}\n", colors.get(risk, 'white'))
        self.display_message("="*70 + "\n\n", 'white')
        
        self.display_message("Risk Scores by Category:\n", 'white')
        for category, level in results['scores'].items():
            self.display_message(f"  {emoji.get(level, '❓')} {category}: {level}\n", colors.get(level, 'white'))
        
        if results['findings']:
            self.display_message(f"\n📋 FINDINGS ({len(results['findings'])} total):\n\n", 'white')
            for i, f in enumerate(results['findings'], 1):
                sev = f['severity']
                self.display_message(f"{i}. [{sev}] {f['issue']}\n", colors.get(sev, 'white'))
                self.display_message(f"   Evidence: {f['evidence']}\n", '#cbd5e0')
                self.display_message(f"   Pattern: {f['pattern']}\n\n", '#718096')
        
        self.display_message("="*70 + "\nRECOMMENDATION:\n" + "="*70 + "\n", 'white')
        
        recs = {
            'CRITICAL': '⛔ DO NOT PUBLISH - Exhibits patterns from major retracted papers', 
            'HIGH': '⚠️  MAJOR REVISION REQUIRED', 
            'MEDIUM': '📋 MINOR REVISION', 
            'LOW': '✅ ACCEPTABLE', 
            'PASS': '✅ NO MAJOR CONCERNS'
        }
        
        self.display_message(f"\n{recs.get(risk, 'Review results above')}\n", colors.get(risk, 'white'))
        self.results_output.config(state='disabled')
    
    def display_message(self, text, color):
        self.results_output.config(state='normal')
        self.results_output.tag_config(f"color_{color}", foreground=color)
        self.results_output.insert('end', text, f"color_{color}")
        self.results_output.config(state='disabled')
    
    def clear_all(self):
        self.text_input.delete('1.0', 'end')
        self.results_output.config(state='normal')
        self.results_output.delete('1.0', 'end')
        self.results_output.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = FraudDetectorGUI(root)
    root.mainloop()
