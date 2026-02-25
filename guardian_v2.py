"""
Guardian v2.0 - AI-Powered Backend
Sanctuary of Ma'at Research Institute
Author: Kenneth Vanini

Multi-Agent Architecture:
  - StatisticalAgent    : Detects data fabrication, p-hacking, impossible statistics
  - CitationAgent       : Identifies unsupported claims and citation manipulation
  - MethodologyAgent    : Checks ethics compliance, data availability, preregistration
  - OrchestratorAgent   : Synthesizes all findings into a final risk verdict

Each agent uses a hybrid approach:
  1. Fast regex/keyword pre-screen (always runs, no API needed)
  2. LLM deep analysis via Anthropic Claude (runs when ANTHROPIC_API_KEY is set)

Falls back gracefully to regex-only if no API key is present.
"""

import re
import json
import os
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# ANTHROPIC CLIENT SETUP (optional — degrades gracefully if not available)
# ─────────────────────────────────────────────────────────────────────────────

try:
    import anthropic
    _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    _AI_ENABLED = bool(os.environ.get("ANTHROPIC_API_KEY", ""))
except ImportError:
    _client = None
    _AI_ENABLED = False

MODEL = "claude-opus-4-6"  # Use best model for fraud detection accuracy

# ─────────────────────────────────────────────────────────────────────────────
# SHARED HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _call_agent(system_prompt: str, user_content: str, max_tokens: int = 1024) -> Optional[str]:
    """Call Claude with a system prompt. Returns text or None on failure."""
    if not _AI_ENABLED or _client is None:
        return None
    try:
        response = _client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}]
        )
        return response.content[0].text
    except Exception as e:
        return None  # Fail silently, fall back to regex results


def _parse_ai_findings(raw: str) -> list:
    """
    Parse AI agent output. Expects JSON array of finding objects.
    Each finding: {severity, issue, evidence, pattern}
    """
    if not raw:
        return []
    try:
        # Strip markdown code fences if present
        clean = re.sub(r'```(?:json)?', '', raw).strip().rstrip('`').strip()
        # Find JSON array in the response
        match = re.search(r'\[.*\]', clean, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return []


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1 — STATISTICAL INTEGRITY AGENT
# ─────────────────────────────────────────────────────────────────────────────

_STAT_SYSTEM = """You are the Statistical Integrity Agent for Guardian, a research fraud detection system.

Your job is to analyze research paper text for statistical red flags associated with data fabrication, 
p-hacking, and reporting anomalies. You are an expert statistician who has studied every major 
retraction case including Diederik Stapel, Brian Wansink, Hwang Woo-suk, and the Surgisphere scandal.

Look for:
- Identical or suspiciously similar standard deviations across independent groups
- P-values clustered just below 0.05 (p-hacking signature)
- Impossible effect sizes for the sample size reported
- Round numbers throughout (e.g., all means end in .0 or .5)
- Missing variance data entirely
- Claims of unverifiable proprietary databases
- Results that are "too clean" — no failed experiments, no outliers
- Baseline characteristics that are statistically too similar across groups (CONSORT table manipulation)

Respond ONLY with a valid JSON array of findings. Each finding must have exactly these fields:
  severity: "CRITICAL" or "FLAGGED"
  issue: short title of the problem (max 80 chars)
  evidence: specific text excerpt or pattern found (max 200 chars)
  pattern: reference to a known retraction case this resembles (max 100 chars)

If no issues found, return an empty array: []

Example format:
[
  {
    "severity": "CRITICAL",
    "issue": "Identical standard deviations across 4 independent groups",
    "evidence": "SD = 2.3 reported for groups A, B, C, D despite different sample sizes and treatments",
    "pattern": "Diederik Stapel (2011) - fabricated data across 58 papers"
  }
]"""


def run_statistical_agent(text: str) -> dict:
    """
    Run statistical integrity checks.
    Returns: {risk_score: str, findings: list, agent: 'Statistical'}
    """
    findings = []

    # ── FAST PRE-SCREEN ──────────────────────────────────────────────────────

    text_lower = text.lower()

    # Check for unverifiable proprietary databases
    if any(t in text_lower for t in ['surgisphere', 'proprietary database', 'proprietary data']):
        findings.append({
            'severity': 'CRITICAL',
            'issue': 'Unverifiable proprietary database referenced',
            'evidence': 'Paper claims a proprietary database that cannot be independently verified',
            'pattern': 'Surgisphere COVID-19 scandal (2020) — Lancet/NEJM retraction'
        })

    # Check for identical standard deviations
    sds = re.findall(r'(?:SD|sd|S\.D\.)\s*[=:]\s*(\d+\.?\d*)', text)
    if len(sds) >= 2:
        sd_values = [float(s) for s in sds]
        unique_sds = set(round(v, 1) for v in sd_values)
        if len(unique_sds) == 1:
            findings.append({
                'severity': 'CRITICAL',
                'issue': 'Identical standard deviations across all groups',
                'evidence': f'All {len(sds)} reported SDs = {sd_values[0]} (statistically near-impossible)',
                'pattern': 'Diederik Stapel (2011) — 58 retracted papers, fabricated data'
            })
        elif len(unique_sds) <= max(2, len(sds) // 3):
            findings.append({
                'severity': 'FLAGGED',
                'issue': 'Suspiciously low variance in standard deviations',
                'evidence': f'Only {len(unique_sds)} unique SD values across {len(sds)} reported groups',
                'pattern': 'Common pattern in fabricated datasets'
            })

    # P-hacking detection
    p_values = re.findall(r'[pP]\s*[=<]\s*(0?\.\d+)', text)
    if len(p_values) >= 3:
        p_nums = []
        for p in p_values:
            try:
                val = float(p)
                if 0 < val <= 1:
                    p_nums.append(val)
            except ValueError:
                pass
        if p_nums:
            just_sig = [p for p in p_nums if 0.040 <= p <= 0.050]
            ratio = len(just_sig) / len(p_nums)
            if ratio >= 0.5:
                findings.append({
                    'severity': 'FLAGGED',
                    'issue': 'P-hacking signature detected',
                    'evidence': f'{len(just_sig)} of {len(p_nums)} p-values ({ratio:.0%}) clustered in 0.040–0.050 range',
                    'pattern': 'Brian Wansink (2017) — 15 retractions, confirmed p-hacking'
                })

    # Suspiciously round numbers
    means = re.findall(r'(?:mean|M)\s*[=:]\s*(\d+\.\d+)', text, re.IGNORECASE)
    if means and len(means) >= 4:
        round_count = sum(1 for m in means if float(m) == round(float(m), 1) and float(m) % 0.5 == 0)
        if round_count / len(means) >= 0.8:
            findings.append({
                'severity': 'FLAGGED',
                'issue': 'Suspiciously round mean values',
                'evidence': f'{round_count} of {len(means)} reported means are round numbers (multiples of 0.5)',
                'pattern': 'Common indicator of manually entered/fabricated data'
            })

    # ── AI DEEP ANALYSIS ─────────────────────────────────────────────────────

    if _AI_ENABLED:
        # Send a focused excerpt to the AI (first 3000 chars covers abstract + methods + results)
        excerpt = text[:4000]
        ai_prompt = f"""Analyze this research paper excerpt for statistical fraud indicators.
        
PAPER TEXT:
{excerpt}

Return ONLY a JSON array of findings as specified. Focus on issues NOT already covered by these 
already-detected patterns: {[f['issue'] for f in findings]}"""

        raw = _call_agent(_STAT_SYSTEM, ai_prompt, max_tokens=1500)
        ai_findings = _parse_ai_findings(raw)

        # Deduplicate against pre-screen findings
        existing_issues = {f['issue'].lower()[:30] for f in findings}
        for af in ai_findings:
            if af.get('issue', '').lower()[:30] not in existing_issues:
                findings.append(af)

    # ── SCORE ─────────────────────────────────────────────────────────────────

    if any(f['severity'] == 'CRITICAL' for f in findings):
        score = 'CRITICAL'
    elif findings:
        score = 'FLAGGED'
    else:
        score = 'PASS'

    return {'risk_score': score, 'findings': findings, 'agent': 'Statistical'}


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2 — CITATION INTEGRITY AGENT
# ─────────────────────────────────────────────────────────────────────────────

_CITE_SYSTEM = """You are the Citation Integrity Agent for Guardian, a research fraud detection system.

Your job is to analyze research paper text for citation manipulation and unsupported claims.
You have deep knowledge of how fraudulent papers misrepresent the literature.

Look for:
- Strong universal claims ("all studies show", "it is well known", "always results in") without citations
- Self-citation loops (author citing only their own prior work)
- Fabricated or impossible citations (e.g., citing papers that don't exist, wrong years)
- Citation of retracted papers as supporting evidence
- Selectively citing only confirming studies (cherry-picking)
- Claims that overstate what the cited source actually shows
- Missing citations for key statistical claims or effect sizes

Respond ONLY with a valid JSON array of findings. Each finding must have exactly these fields:
  severity: "CRITICAL" or "FLAGGED"
  issue: short title of the problem (max 80 chars)
  evidence: specific text excerpt or pattern found (max 200 chars)
  pattern: reference to a known problematic citation practice (max 100 chars)

If no issues found, return: []"""


def run_citation_agent(text: str) -> dict:
    """
    Run citation integrity checks.
    Returns: {risk_score: str, findings: list, agent: 'Citation'}
    """
    findings = []
    text_lower = text.lower()

    # ── FAST PRE-SCREEN ──────────────────────────────────────────────────────

    strong_claims = [
        ('all studies show', 'Absolute claim: "all studies show"'),
        ('always results in', 'Absolute claim: "always results in"'),
        ('definitively proves', 'Overreach: "definitively proves"'),
        ('it is well known', 'Unsubstantiated consensus: "it is well known"'),
        ('consensus is that', 'Unsubstantiated consensus: "consensus is that"'),
        ('impossible to', 'Absolute negation: "impossible to"'),
        ('universally accepted', 'Overreach: "universally accepted"'),
        ('undeniably', 'Absolute: "undeniably"'),
        ('without exception', 'Absolute: "without exception"'),
    ]

    sentences = re.split(r'(?<=[.!?])\s+', text)
    for phrase, label in strong_claims:
        if phrase in text_lower:
            for sent in sentences:
                if phrase in sent.lower():
                    # Check if sentence has a citation (Author, Year) or [N] style
                    has_citation = bool(
                        re.search(r'\([A-Z][a-z]+.*?\d{4}\)', sent) or
                        re.search(r'\[\d+\]', sent) or
                        re.search(r'\d{4}\)', sent)
                    )
                    if not has_citation:
                        findings.append({
                            'severity': 'FLAGGED',
                            'issue': f'Strong claim without supporting citation',
                            'evidence': f'{label} — sentence lacks any citation',
                            'pattern': 'Hallmark of unsupported extrapolation in problematic papers'
                        })
                    break  # One finding per phrase type

    # Check for excessive self-citation (heuristic: same author name appears in >60% of citations)
    citations = re.findall(r'\(([A-Z][a-z]+)(?:\s+et\s+al\.?)?,?\s+\d{4}\)', text)
    if len(citations) >= 5:
        from collections import Counter
        citation_counts = Counter(citations)
        top_author, top_count = citation_counts.most_common(1)[0]
        if top_count / len(citations) >= 0.5:
            findings.append({
                'severity': 'FLAGGED',
                'issue': 'Potential self-citation loop',
                'evidence': f'Author "{top_author}" appears in {top_count}/{len(citations)} citations ({top_count/len(citations):.0%})',
                'pattern': 'Citation manipulation to inflate impact — common in compromised reviews'
            })

    # ── AI DEEP ANALYSIS ─────────────────────────────────────────────────────

    if _AI_ENABLED:
        # Focus AI on the introduction and discussion where citation issues cluster
        intro_disc = text[:2000] + "\n...\n" + text[-2000:] if len(text) > 4000 else text
        ai_prompt = f"""Analyze this research paper for citation integrity issues.

PAPER TEXT (intro + discussion):
{intro_disc}

Focus especially on: unsupported claims, impossible citations, cherry-picking language.
Already detected: {[f['issue'] for f in findings]}

Return ONLY a JSON array of findings."""

        raw = _call_agent(_CITE_SYSTEM, ai_prompt, max_tokens=1200)
        ai_findings = _parse_ai_findings(raw)
        existing = {f['issue'].lower()[:30] for f in findings}
        for af in ai_findings:
            if af.get('issue', '').lower()[:30] not in existing:
                findings.append(af)

    # ── SCORE ─────────────────────────────────────────────────────────────────

    if len(findings) >= 3:
        score = 'CRITICAL'
    elif findings:
        score = 'FLAGGED'
    else:
        score = 'PASS'

    return {'risk_score': score, 'findings': findings[:5], 'agent': 'Citation'}


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3 — METHODOLOGY & ETHICS AGENT
# ─────────────────────────────────────────────────────────────────────────────

_METH_SYSTEM = """You are the Methodology and Ethics Compliance Agent for Guardian, a research fraud detection system.

Your job is to identify structural integrity failures in research papers — missing ethics approvals,
absent data availability statements, lack of preregistration, and methodological red flags that
enabled major retractions.

Look for:
- Missing IRB / ethics committee approval (required for human subjects research)
- Missing data availability statement (data should be available or archived)
- No preregistration for clinical trials or psychology studies
- Vague or incomplete methods that cannot be replicated
- Impossibly short study timelines for the scope of work described
- Sample size with no power calculation or justification
- Missing conflict of interest declaration
- Post-hoc outcome switching (outcomes described as "secondary" that appear primary)
- Duplicate publication indicators (same data, different framing)

Respond ONLY with a valid JSON array of findings. Each finding must have exactly these fields:
  severity: "CRITICAL" or "FLAGGED"  
  issue: short title of the problem (max 80 chars)
  evidence: specific text excerpt or pattern found (max 200 chars)
  pattern: reference to a known retraction case this resembles (max 100 chars)

If no issues found, return: []"""


def run_methodology_agent(text: str) -> dict:
    """
    Run methodology and ethics compliance checks.
    Returns: {risk_score: str, findings: list, agent: 'Methodology'}
    """
    findings = []
    text_lower = text.lower()

    # ── FAST PRE-SCREEN ──────────────────────────────────────────────────────

    # Ethics approval check
    ethics_terms = [
        'ethics committee', 'irb approval', 'ethical approval',
        'institutional review board', 'declaration of helsinki',
        'informed consent', 'animal care', 'iacuc', 'ethical guidelines',
        'ethics board', 'research ethics', 'protocol approval', 'irb #', 'irb no'
    ]
    if not any(t in text_lower for t in ethics_terms):
        findings.append({
            'severity': 'CRITICAL',
            'issue': 'No ethics approval documented in manuscript',
            'evidence': 'Methods section contains no IRB, ethics committee, or equivalent approval statement',
            'pattern': 'Joachim Boldt (2010) — 90+ retractions for forged ethics approvals'
        })

    # Data availability check
    data_terms = [
        'data available', 'data availability', 'osf.io', 'data repository',
        'github.com', 'supplementary material', 'supplemental data',
        'supporting information', 'available upon request', 'zenodo',
        'figshare', 'dryad', 'appendix', 'raw data', 'open data',
        'data sharing', 'dataset available', 'mendeley data'
    ]
    if not any(t in text_lower for t in data_terms):
        findings.append({
            'severity': 'CRITICAL',
            'issue': 'No data availability statement found',
            'evidence': 'No mention of data repository, supplementary files, or availability policy',
            'pattern': 'Michael LaCour (2015) — Science retraction, data was entirely fabricated'
        })

    # Preregistration check
    prereg_terms = [
        'preregistered', 'pre-registered', 'registered report',
        'clinicaltrials.gov', 'nct0', 'isrctn', 'prospero',
        'trial registry', 'pre-registration', 'registration number',
        'open science framework', 'aspredicted'
    ]
    if not any(t in text_lower for t in prereg_terms):
        findings.append({
            'severity': 'FLAGGED',
            'issue': 'No study preregistration mentioned',
            'evidence': 'No reference to preregistration, trial registration, or registered report',
            'pattern': 'Best practice for preventing outcome switching and HARKing'
        })

    # Conflict of interest check
    coi_terms = [
        'conflict of interest', 'competing interest', 'declaration of interest',
        'financial disclosure', 'no conflict', 'coi statement', 'the authors declare'
    ]
    if not any(t in text_lower for t in coi_terms):
        findings.append({
            'severity': 'FLAGGED',
            'issue': 'No conflict of interest declaration',
            'evidence': 'No COI statement found — required by most journals and funding bodies',
            'pattern': 'Undisclosed industry funding linked to multiple bias-inflated retractions'
        })

    # Power calculation check
    power_terms = [
        'power calculation', 'sample size calculation', 'power analysis',
        'statistical power', 'adequately powered', 'a priori power'
    ]
    if not any(t in text_lower for t in power_terms):
        findings.append({
            'severity': 'FLAGGED',
            'issue': 'No power calculation or sample size justification',
            'evidence': 'Methods lack any mention of how sample size was determined',
            'pattern': 'Underpowered studies susceptible to false positives and selective reporting'
        })

    # ── AI DEEP ANALYSIS ─────────────────────────────────────────────────────

    if _AI_ENABLED:
        # Focus on methods section specifically
        methods_excerpt = text[1000:5000] if len(text) > 5000 else text
        ai_prompt = f"""Analyze this research paper's methods/ethics section for compliance failures.

PAPER TEXT (methods region):
{methods_excerpt}

Already flagged issues: {[f['issue'] for f in findings]}

Focus on: replication feasibility, timeline plausibility, outcome definitions, any signs of
post-hoc analysis presented as pre-planned.

Return ONLY a JSON array of findings."""

        raw = _call_agent(_METH_SYSTEM, ai_prompt, max_tokens=1400)
        ai_findings = _parse_ai_findings(raw)
        existing = {f['issue'].lower()[:30] for f in findings}
        for af in ai_findings:
            if af.get('issue', '').lower()[:30] not in existing:
                findings.append(af)

    # ── SCORE ─────────────────────────────────────────────────────────────────

    if any(f['severity'] == 'CRITICAL' for f in findings):
        score = 'CRITICAL'
    elif findings:
        score = 'FLAGGED'
    else:
        score = 'PASS'

    return {'risk_score': score, 'findings': findings, 'agent': 'Methodology'}


# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATOR — SYNTHESIZES ALL AGENT OUTPUTS
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 4 — PAPER MILL DETECTION
# ─────────────────────────────────────────────────────────────────────────────

_MILL_SYSTEM = """You are the Paper Mill Detection Agent for Guardian, a research fraud detection
system at the Sanctuary of Ma'at Research Institute.

Guardian is the FIRST automated system to implement paper mill detection.
Morressier (nearest competitor) publicly admitted in July 2023 their tool is still in development.

You analyze manuscripts for paper mill signatures:
- Tortured phrases (AI synonym-mangling to evade plagiarism tools)
- Suspiciously round sample sizes (invented data defaults to n=100, 200, 500)
- Boilerplate ethics statements (copy-paste text across unrelated papers)
- Generic interchangeable methodology (template sold across disciplines)
- Template result structures (high table/figure density, no actual numbers)

Return ONLY a JSON array of finding objects with fields: severity, issue, evidence, pattern.
CRITICAL = tortured phrases (definitive mill fingerprint)
FLAGGED = other signals (each individually probabilistic, combined = high confidence)"""


def run_paper_mill_agent(text: str) -> dict:
    """
    Run paper mill detection checks.
    Returns: {risk_score: str, findings: list, agent: 'Paper Mill'}
    """
    findings = []
    text_lower = text.lower()

    # ── TORTURED PHRASES ─────────────────────────────────────────────────────
    tortured = {
        'counterfeit consciousness':       'artificial intelligence',
        'profound learning':               'deep learning',
        'irregular timberland':            'random forest',
        'brain organizations':             'neural networks',
        'colossal information':            'big data',
        'fluffy rationale':                'fuzzy logic',
        'machine adapting':                'machine learning',
        'information mining':              'data mining',
        'natural language handling':       'natural language processing',
        'picture preparing':               'image processing',
        'flag handling':                   'signal processing',
        'hereditary calculation':          'genetic algorithm',
        'counterfeit brain organization':  'artificial neural network',
        'help vector machine':             'support vector machine',
        'arbitrary woods':                 'random forest',
        'cloud figuring':                  'cloud computing',
        'savvy city':                      'smart city',
        'web of things':                   'internet of things',
        'bosom malignant growth':          'breast cancer',
    }
    found_tortured = [(k, v) for k, v in tortured.items() if k in text_lower]
    if found_tortured:
        findings.append({
            'severity': 'CRITICAL',
            'issue': 'Tortured phrases detected',
            'evidence': f'{len(found_tortured)} synonym-substituted phrase(s): ' +
                        '; '.join(f'"{k}" → "{v}"' for k, v in found_tortured[:3]),
            'pattern': 'Paper mill fingerprint — AI synonym mangling to evade plagiarism detection (Cabanac & Labbé, 2021)'
        })

    # ── ROUND SAMPLE SIZES ────────────────────────────────────────────────────
    import re as _re
    sizes = [int(m.group(1)) for m in _re.finditer(r'\bn\s*=\s*(\d+)', text, _re.IGNORECASE)]
    if len(sizes) >= 2 and all(s >= 30 and s % 50 == 0 for s in sizes):
        findings.append({
            'severity': 'FLAGGED',
            'issue': 'Suspiciously round sample sizes',
            'evidence': f'All {len(sizes)} reported sample sizes are exact multiples of 50: n = {", ".join(str(s) for s in sizes)}',
            'pattern': 'Paper mill signature — invented data defaults to convenient round numbers'
        })

    # ── BOILERPLATE ETHICS ────────────────────────────────────────────────────
    boilerplate = [
        'the study was conducted in accordance with the declaration of helsinki',
        'informed consent was obtained from all subjects involved in the study',
        'all subjects gave their informed consent for inclusion before they participated',
        'ethical review and approval were waived for this study',
        'patient consent was waived due to the retrospective nature',
        'the authors declare that the research was conducted in the absence of any commercial',
    ]
    found_boiler = [p for p in boilerplate if p in text_lower]
    if len(found_boiler) >= 2:
        findings.append({
            'severity': 'FLAGGED',
            'issue': 'Boilerplate ethics language detected',
            'evidence': f'{len(found_boiler)} standardized ethics phrases found — identical text appears across known paper mill submissions',
            'pattern': 'Paper mill signature — copy-paste ethics statements reused across unrelated manuscripts'
        })

    # ── GENERIC METHODS ───────────────────────────────────────────────────────
    generic = [
        'the data were collected and analyzed',
        'appropriate statistical methods were used',
        'standard procedures were followed',
        'the experiment was conducted as previously described',
        'data analysis was performed using spss',
        'questionnaires were distributed to participants',
        'data were analyzed using appropriate software',
        'participants were randomly assigned',
        'the methodology adopted in this study',
        'the survey was conducted among',
    ]
    generic_hits = [p for p in generic if p in text_lower]
    if len(generic_hits) >= 3:
        findings.append({
            'severity': 'FLAGGED',
            'issue': 'Generic non-specific methodology',
            'evidence': f'{len(generic_hits)} vague methodology phrases detected — methods section lacks domain-specific detail',
            'pattern': 'Paper mill signature — interchangeable template methods sold across disciplines'
        })

    # ── TEMPLATE RESULT STRUCTURE ─────────────────────────────────────────────
    word_count = len(text.split())
    if word_count > 200:
        table_refs  = len(_re.findall(r'\btable\s+\d+\b', text_lower))
        figure_refs = len(_re.findall(r'\bfigure\s+\d+\b', text_lower))
        shows_n     = len(_re.findall(r'\bshows?\b', text_lower))
        indicates_n = len(_re.findall(r'\bindicates?\b', text_lower))
        ref_density = table_refs + figure_refs + shows_n + indicates_n
        data_numbers = len(_re.findall(r'\b\d+\.\d+\b|\b[1-9]\d+\b', text))
        if ref_density >= 8 and data_numbers < 10:
            findings.append({
                'severity': 'FLAGGED',
                'issue': 'Template result structure without numerical data',
                'evidence': f'High reference density ({ref_density} table/figure/shows/indicates references) but only {data_numbers} numeric values',
                'pattern': 'Paper mill signature — fill-in-the-blank result templates referencing non-existent data'
            })

    # ── AI DEEP ANALYSIS ──────────────────────────────────────────────────────
    if _AI_ENABLED:
        excerpt = text[:5000]
        ai_prompt = f"""Analyze this manuscript for paper mill characteristics.

PAPER TEXT:
{excerpt}

Already flagged: {[f['issue'] for f in findings]}

Look for: unnatural phrasing, implausible timelines, domain mismatch between authors
and topic, suspiciously generic language, near-identical sentence structures repeated.

Return ONLY a JSON array of findings."""
        raw = _call_agent(_MILL_SYSTEM, ai_prompt, max_tokens=1000)
        ai_findings = _parse_ai_findings(raw)
        existing = {f['issue'].lower()[:30] for f in findings}
        for af in ai_findings:
            if af.get('issue', '').lower()[:30] not in existing:
                findings.append(af)

    # ── SCORE ─────────────────────────────────────────────────────────────────
    if any(f['severity'] == 'CRITICAL' for f in findings):
        score = 'CRITICAL'
    elif len(findings) >= 2:
        score = 'CRITICAL'  # 2+ FLAGGED signals = high-confidence mill
    elif findings:
        score = 'FLAGGED'
    else:
        score = 'PASS'

    return {'risk_score': score, 'findings': findings, 'agent': 'Paper Mill'}


# ─────────────────────────────────────────────────────────────────────────────

_ORCH_SYSTEM = """You are the Chief Orchestrator for Guardian, a research fraud detection system at the 
Sanctuary of Ma'at Research Institute.

You receive structured findings from four specialist agents (Statistical, Citation, Methodology, Paper Mill) and 
must synthesize them into a final risk verdict and executive summary.

Your output must be a JSON object with exactly these fields:
  overall_risk: "CRITICAL", "FLAGGED", or "PASS"
  executive_summary: 2-3 sentence plain-language verdict explaining the risk level and key concerns
  key_concerns: array of the 3 most critical issues (strings), or empty array if none
  recommendation: one of:
    "DO NOT PUBLISH — exhibits patterns from major retracted papers"
    "REQUIRES MAJOR REVISION — significant concerns must be addressed before review"
    "REQUIRES MINOR REVISION — some concerns flagged, verify before publication"  
    "APPEARS COMPLIANT — no major fraud indicators detected"

Be conservative: when in doubt about borderline cases, escalate the risk level."""


def _orchestrate(stat_result: dict, cite_result: dict, meth_result: dict, text: str, mill_result: dict = None) -> dict:
    """
    Combine agent results into a final verdict.
    Returns the complete report dict expected by Guardian_gui.py
    """
    if mill_result is None:
        mill_result = {'risk_score': 'PASS', 'findings': [], 'agent': 'Paper Mill'}

    all_findings = (
        stat_result['findings'] +
        cite_result['findings'] +
        meth_result['findings'] +
        mill_result['findings']
    )

    agent_statuses = {
        'Statistical Integrity': stat_result['risk_score'],
        'Citation Integrity':    cite_result['risk_score'],
        'Methodology & Ethics':  meth_result['risk_score'],
        'Paper Mill':            mill_result['risk_score'],
    }

    scores = list(agent_statuses.values())

    # ── RULE-BASED OVERALL RISK ───────────────────────────────────────────────

    if 'CRITICAL' in scores:
        rule_risk = 'CRITICAL'
    elif scores.count('FLAGGED') >= 2:
        rule_risk = 'FLAGGED'
    elif 'FLAGGED' in scores:
        rule_risk = 'FLAGGED'
    else:
        rule_risk = 'PASS'

    # ── AI SYNTHESIS (if available) ───────────────────────────────────────────

    executive_summary = ""
    key_concerns = []
    recommendation = ""

    if _AI_ENABLED:
        findings_summary = json.dumps(all_findings[:10], indent=2)  # Top 10 findings
        orch_prompt = f"""Synthesize these fraud detection findings into a final verdict.

AGENT SCORES:
{json.dumps(agent_statuses, indent=2)}

FINDINGS ({len(all_findings)} total, showing top 10):
{findings_summary}

Return ONLY the JSON object as specified."""

        raw = _call_agent(_ORCH_SYSTEM, orch_prompt, max_tokens=600)
        if raw:
            try:
                clean = re.sub(r'```(?:json)?', '', raw).strip().rstrip('`').strip()
                match = re.search(r'\{.*\}', clean, re.DOTALL)
                if match:
                    orch_data = json.loads(match.group())
                    rule_risk = orch_data.get('overall_risk', rule_risk)
                    executive_summary = orch_data.get('executive_summary', '')
                    key_concerns = orch_data.get('key_concerns', [])
                    recommendation = orch_data.get('recommendation', '')
            except Exception:
                pass  # Fall back to rule-based verdict

    # ── BUILD FINAL REPORT ────────────────────────────────────────────────────

    # Default recommendation if AI didn't provide one
    if not recommendation:
        rec_map = {
            'CRITICAL': 'DO NOT PUBLISH — exhibits patterns from major retracted papers',
            'FLAGGED': 'REQUIRES MAJOR REVISION — significant concerns must be addressed before review',
            'PASS': 'APPEARS COMPLIANT — no major fraud indicators detected'
        }
        recommendation = rec_map.get(rule_risk, 'Review findings above')

    if not executive_summary:
        critical_count = sum(1 for f in all_findings if f.get('severity') == 'CRITICAL')
        flagged_count = sum(1 for f in all_findings if f.get('severity') == 'FLAGGED')
        executive_summary = (
            f"Guardian identified {len(all_findings)} total concern(s): "
            f"{critical_count} CRITICAL and {flagged_count} FLAGGED. "
            f"Risk classification: {rule_risk}."
        )

    return {
        'overall_risk': rule_risk,
        'agent_statuses': agent_statuses,
        'all_findings': all_findings,
        'executive_summary': executive_summary,
        'key_concerns': key_concerns,
        'recommendation': recommendation,
        'ai_enhanced': _AI_ENABLED,
        'total_findings': len(all_findings),
    }


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API — called by Guardian_gui.py
# ─────────────────────────────────────────────────────────────────────────────

def analyze_paper(text: str) -> dict:
    """
    Main entry point. Runs all three agents and returns a unified report.

    Args:
        text: Full text of the research paper

    Returns:
        {
          overall_risk:      "CRITICAL" | "FLAGGED" | "PASS"
          agent_statuses:    {agent_name: risk_score, ...}
          all_findings:      [{severity, issue, evidence, pattern}, ...]
          executive_summary: str
          key_concerns:      [str, ...]
          recommendation:    str
          ai_enhanced:       bool
          total_findings:    int
        }
    """
    if not text or not text.strip():
        return {
            'overall_risk': 'PASS',
            'agent_statuses': {
                'Statistical Integrity': 'PASS',
                'Citation Integrity':    'PASS',
                'Methodology & Ethics':  'PASS',
                'Paper Mill':            'PASS',
            },
            'all_findings': [],
            'executive_summary': 'No text provided for analysis.',
            'key_concerns': [],
            'recommendation': 'Please provide paper text for analysis.',
            'ai_enhanced': False,
            'total_findings': 0,
        }

    # Run agents (could be parallelized with threading for speed)
    stat_result = run_statistical_agent(text)
    cite_result = run_citation_agent(text)
    meth_result = run_methodology_agent(text)
    mill_result = run_paper_mill_agent(text)

    # Orchestrate into final report
    return _orchestrate(stat_result, cite_result, meth_result, text, mill_result)


# ─────────────────────────────────────────────────────────────────────────────
# CLI TEST MODE — run directly to test without GUI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("Guardian v2.0 Backend — Test Mode")
    print(f"AI Enhanced: {_AI_ENABLED}")
    print("=" * 70)

    # Use a sample fraudulent paper if no file provided
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
            sample = f.read()
    else:
        sample = """
        Abstract: This study definitively proves that our novel treatment always results in 
        significant improvement. It is well known that current therapies are inadequate. 
        All studies show poor outcomes with standard care. Consensus is that new approaches 
        are needed.
        
        Methods: Participants (N=120) were randomly assigned to treatment or control groups.
        Data was collected using our proprietary database system. 
        Group A: mean=4.5, SD=1.2. Group B: mean=6.5, SD=1.2. Group C: mean=8.5, SD=1.2.
        
        Results: Treatment showed significant improvement (p=0.048). Secondary outcome also 
        improved (p=0.043). Additional measures showed benefit (p=0.047). Quality of life 
        improved (p=0.042).
        
        Discussion: These results confirm our hypothesis. Further research is needed.
        """

    print("\nAnalyzing paper...\n")
    report = analyze_paper(sample)

    print(f"OVERALL RISK: {report['overall_risk']}")
    print(f"AI Enhanced: {report['ai_enhanced']}")
    print(f"\nAgent Statuses:")
    for agent, status in report['agent_statuses'].items():
        print(f"  {agent}: {status}")

    print(f"\nFindings ({report['total_findings']} total):")
    for i, f in enumerate(report['all_findings'], 1):
        print(f"  {i}. [{f['severity']}] {f['issue']}")
        print(f"     Evidence: {f['evidence']}")

    print(f"\nExecutive Summary: {report['executive_summary']}")
    print(f"\nRecommendation: {report['recommendation']}")
