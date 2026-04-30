@app.route('/ratings', methods=['GET'])
def get_ratings():
    data = _read_bin()
    avg, count = _compute_stats(data.get('ratings', []))
    return jsonify({
        'ratings': data.get('ratings', []),
        'average': avg,
        'count': count
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
