from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests as req

app = Flask(__name__)
CORS(app)

# ── ENV VARS (set these on Render) ────────────────────────────────────────────
JSONBIN_BIN  = os.environ.get('JSONBIN_BIN_ID', '')
JSONBIN_KEY  = os.environ.get('JSONBIN_API_KEY', '')
JSONBIN_BASE = f'https://api.jsonbin.io/v3/b/{JSONBIN_BIN}'
JSONBIN_HDR  = {'X-Master-Key': JSONBIN_KEY, 'Content-Type': 'application/json'}


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _read_bin():
    """Read current ratings from JSONBin."""
    try:
        r = req.get(f'{JSONBIN_BASE}/latest', headers=JSONBIN_HDR, timeout=5)
        return r.json().get('record', {'ratings': []})
    except Exception:
        return {'ratings': []}


def _write_bin(data):
    """Overwrite the bin with updated data."""
    try:
        req.put(JSONBIN_BASE, json=data, headers=JSONBIN_HDR, timeout=5)
    except Exception:
        pass


def _compute_stats(ratings):
    if not ratings:
        return 0.0, 0
    avg = round(sum(r['stars'] for r in ratings) / len(ratings), 1)
    return avg, len(ratings)


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return jsonify({'status': 'Ledja backend running'})


@app.route('/ratings', methods=['GET'])
def get_ratings():
    data = _read_bin()
    avg, count = _compute_stats(data.get('ratings', []))
    return jsonify({
        'ratings': data.get('ratings', []),
        'average': avg,
        'count':   count
    })


@app.route('/rate', methods=['POST'])
def post_rating():
    body = request.get_json(silent=True) or {}
    stars = int(body.get('stars', 0))
    if stars < 1 or stars > 5:
        return jsonify({'error': 'Invalid rating'}), 400

    entry = {
        'stars':   stars,
        'name':    str(body.get('name', 'Anonymous'))[:40],
        'comment': str(body.get('comment', ''))[:200],
        'date':    str(body.get('date', ''))[:20],
    }

    data = _read_bin()
    ratings = data.get('ratings', [])
    ratings.append(entry)
    _write_bin({'ratings': ratings})

    avg, count = _compute_stats(ratings)
    return jsonify({
        'ratings': ratings,
        'average': avg,
        'count':   count
    })


# ── M-PESA / SMS ROUTES (add here when Safaricom Paybill is approved) ────────
# @app.route('/c2b/validation', methods=['POST'])
# @app.route('/c2b/confirmation', methods=['POST'])
# @app.route('/validate', methods=['POST'])
# @app.route('/register-urls', methods=['POST'])


if __name__ == '__main__':
    app.run()
