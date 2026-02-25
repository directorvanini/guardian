"""
Guardian v2.0 — REST API Server
Sanctuary of Ma'at Research Institute

Exposes fraud detection agents as HTTP endpoints.
Complete.dev agents call these endpoints as tools.

Endpoints:
  POST /analyze          — Full multi-agent analysis (primary)
  POST /agents/stats     — Statistical integrity agent only
  POST /agents/citations — Citation integrity agent only
  POST /agents/methods   — Methodology & ethics agent only
  GET  /health           — Health check + AI status

Run:
  pip install flask flask-cors
  ANTHROPIC_API_KEY=sk-... python guardian_api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import traceback

# Import our backend
sys.path.insert(0, os.path.dirname(__file__))
from guardian_v2 import (
    analyze_paper,
    run_statistical_agent,
    run_citation_agent,
    run_methodology_agent,
    run_paper_mill_agent,
    _AI_ENABLED,
    MODEL
)

app = Flask(__name__)
CORS(app)  # Allow Complete.dev and web clients to call this API

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_text_from_request():
    """Extract paper text from JSON body. Returns (text, error_response)."""
    data = request.get_json(silent=True)
    if not data:
        return None, (jsonify({'error': 'Request body must be JSON'}), 400)
    text = data.get('text', '').strip()
    if not text:
        return None, (jsonify({'error': 'Field "text" is required and cannot be empty'}), 400)
    if len(text) > 200_000:
        return None, (jsonify({'error': 'Text exceeds 200,000 character limit'}), 413)
    return text, None


# ─────────────────────────────────────────────────────────────────────────────
# PRIMARY ENDPOINT — Full Analysis
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Full multi-agent analysis. Primary endpoint for Complete.dev Orchestrator Agent.

    Request:
      { "text": "<full paper text>" }

    Response:
      {
        "overall_risk": "CRITICAL" | "FLAGGED" | "PASS",
        "agent_statuses": { "Statistical Integrity": "...", ... },
        "all_findings": [ { severity, issue, evidence, pattern }, ... ],
        "executive_summary": "...",
        "recommendation": "...",
        "ai_enhanced": bool,
        "total_findings": int
      }
    """
    text, err = get_text_from_request()
    if err:
        return err

    try:
        report = analyze_paper(text)
        return jsonify(report)
    except Exception as e:
        return jsonify({
            'error': 'Analysis failed',
            'detail': str(e),
            'trace': traceback.format_exc()
        }), 500


# ─────────────────────────────────────────────────────────────────────────────
# INDIVIDUAL AGENT ENDPOINTS — for Complete.dev Agent Builder tools
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/agents/stats', methods=['POST'])
def stats_agent():
    """
    Statistical Integrity Agent.
    Detects: data fabrication, p-hacking, impossible statistics, suspicious variance.

    Request:  { "text": "..." }
    Response: { "risk_score": "CRITICAL|FLAGGED|PASS", "findings": [...], "agent": "Statistical" }
    """
    text, err = get_text_from_request()
    if err:
        return err
    try:
        return jsonify(run_statistical_agent(text))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/agents/citations', methods=['POST'])
def citation_agent():
    """
    Citation Integrity Agent.
    Detects: unsupported claims, self-citation loops, cherry-picking.

    Request:  { "text": "..." }
    Response: { "risk_score": "CRITICAL|FLAGGED|PASS", "findings": [...], "agent": "Citation" }
    """
    text, err = get_text_from_request()
    if err:
        return err
    try:
        return jsonify(run_citation_agent(text))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/agents/methods', methods=['POST'])
def methodology_agent():
    """
    Methodology & Ethics Agent.
    Detects: missing IRB approval, no data availability, no preregistration, no COI.

    Request:  { "text": "..." }
    Response: { "risk_score": "CRITICAL|FLAGGED|PASS", "findings": [...], "agent": "Methodology" }
    """
    text, err = get_text_from_request()
    if err:
        return err
    try:
        return jsonify(run_methodology_agent(text))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/agents/papermill', methods=['POST'])
def paper_mill_agent_endpoint():
    """
    Paper Mill Detection Agent.
    Detects: tortured phrases, round sample sizes, boilerplate ethics,
    generic methods, template result structures.
    Guardian is the FIRST automated system with this capability.
    Morressier (competitor) admitted in July 2023 their tool is still in development.

    Request:  { "text": "..." }
    Response: { "risk_score": "CRITICAL|FLAGGED|PASS", "findings": [...], "agent": "Paper Mill" }
    """
    text, err = get_text_from_request()
    if err:
        return err
    try:
        return jsonify(run_paper_mill_agent(text))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'Guardian v2.0 API',
        'ai_enhanced': _AI_ENABLED,
        'model': MODEL if _AI_ENABLED else 'regex-only',
        'endpoints': [
            'POST /analyze',
            'POST /agents/stats',
            'POST /agents/citations',
            'POST /agents/methods',
            'POST /agents/papermill',
            'GET  /health'
        ]
    })


@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'name': 'Guardian v2.0',
        'description': 'Multi-agent research fraud detection API',
        'institute': "Sanctuary of Ma'at Research Institute",
        'docs': 'POST /analyze with {"text": "<paper text>"}'
    })


# ─────────────────────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    print(f"\n{'='*60}")
    print(f"  Guardian v2.0 API Server")
    print(f"  AI Enhanced: {_AI_ENABLED}")
    print(f"  Running on: http://localhost:{port}")
    print(f"{'='*60}\n")
    app.run(host='0.0.0.0', port=port, debug=debug)
