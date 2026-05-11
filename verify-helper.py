# ── AUTH HELPER ───────────────────────────────────────────────────────────────
def verify_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms=['HS256']   # explicit algorithm list — prevents alg:none attack
        )
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
