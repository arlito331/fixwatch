#!/usr/bin/env python3
"""One-time migration: encrypt FixWatch data so the public repo holds only ciphertext.

- data/fixes.json           -> data/fixes.enc            (AES-256-GCM, iv||ct)
- photos/**/*.jpg           -> same path + '.enc'        (AES-256-GCM, iv||ct)
- data/keys.json            <- master key wrapped under each account password
                               (PBKDF2-SHA256, shared salt, per-entry AES-GCM)

Passwords live OUTSIDE the repo (../KEYS/fixwatch-passwords.json), master key
backup too. Run from the repo root:  python3 tools/encrypt_data.py apply
Without 'apply' it is a dry run. Idempotent: skips already-encrypted files.
"""
import json, os, secrets, sys, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS_DIR = os.path.join(os.path.dirname(REPO), 'KEYS')
PW_FILE = os.path.join(KEYS_DIR, 'fixwatch-passwords.json')
MK_FILE = os.path.join(KEYS_DIR, 'fixwatch-master-key.txt')
ITER = 600_000

def b64(b): import base64; return base64.b64encode(b).decode()

def enc_file(aes, src, dst):
    iv = secrets.token_bytes(12)
    with open(src, 'rb') as f: pt = f.read()
    with open(dst, 'wb') as f: f.write(iv + aes.encrypt(iv, pt, None))

def main():
    apply = len(sys.argv) > 1 and sys.argv[1] == 'apply'
    accounts = json.load(open(PW_FILE))          # [{user,pass,role,country}]

    if os.path.exists(MK_FILE):
        import base64; mk = base64.b64decode(open(MK_FILE).read().strip())
    else:
        mk = secrets.token_bytes(32)
        if apply:
            open(MK_FILE, 'w').write(b64(mk))
            os.chmod(MK_FILE, 0o600)
    aes = AESGCM(mk)

    # wrap table
    salt = secrets.token_bytes(16)
    entries = []
    for a in accounts:
        kek = hashlib.pbkdf2_hmac('sha256', a['pass'].encode(), salt, ITER)
        payload = json.dumps({'user': a['user'], 'role': a['role'],
                              'country': a.get('country'), 'k': b64(mk)}).encode()
        iv = secrets.token_bytes(12)
        entries.append({'iv': b64(iv), 'ct': b64(AESGCM(kek).encrypt(iv, payload, None))})
    keys = {'v': 1, 'kdf': {'name': 'PBKDF2-SHA256', 'iter': ITER, 'salt': b64(salt)},
            'entries': entries}

    fixes_src = os.path.join(REPO, 'data', 'fixes.json')
    todo_photos = []
    for root, _, files in os.walk(os.path.join(REPO, 'photos')):
        for fn in files:
            p = os.path.join(root, fn)
            if fn.endswith('.enc') or fn.startswith('.'): continue
            if not os.path.exists(p + '.enc'): todo_photos.append(p)

    print(f"accounts: {len(accounts)} | photos to encrypt: {len(todo_photos)} | "
          f"fixes.json: {'yes' if os.path.exists(fixes_src) else 'MISSING'}")
    if not apply:
        print("dry run — pass 'apply' to write"); return

    json.dump(keys, open(os.path.join(REPO, 'data', 'keys.json'), 'w'), indent=1)
    if os.path.exists(fixes_src):
        enc_file(aes, fixes_src, os.path.join(REPO, 'data', 'fixes.enc'))
        # plaintext backup outside the repo, then remove from worktree
        import shutil; shutil.copy2(fixes_src, os.path.join(KEYS_DIR, 'fixes.json.pre-encryption'))
        os.remove(fixes_src)
    for p in todo_photos:
        enc_file(aes, p, p + '.enc'); os.remove(p)
    print("done: keys.json, fixes.enc, %d photos" % len(todo_photos))

if __name__ == '__main__':
    main()
