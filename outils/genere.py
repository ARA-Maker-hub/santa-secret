#!/usr/bin/env python3
"""Tirage Santa secret : un seul grand cycle (personne ne se tire soi-même, pas de duo A<->B).
Exceptions dans config.json : [["Giver","Receveur interdit"], ...] (sens unique).
Imposés dans config.json : "imposes": [["Giver","Receveur"], ...] (ce couple doit exister dans le tirage).
Option --apercu : affiche un tirage sans rien écrire.
Sorties : ../site/data.json (chiffré, public) et liens_et_tirage.md (PRIVÉ, pour Driss)."""
import json, secrets, base64, os, sys, random, hashlib, shutil
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

here = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(here, "config.json"), encoding="utf-8"))
names = cfg["participants"]
n = len(names)
if n < 3:
    sys.exit("Il faut au moins 3 participants.")
forb = {(a, b) for a, b in cfg.get("exceptions", [])}
for a, b in forb:
    if a not in names or b not in names:
        sys.exit(f"Exception inconnue : {a} -> {b}")

imp = [tuple(x) for x in cfg.get("imposes", [])]
for a, b in imp:
    if a not in names or b not in names:
        sys.exit(f"Imposé inconnu : {a} -> {b}")
APERCU = "--apercu" in sys.argv
sys.argv = [a for a in sys.argv if a != "--apercu"]

rng = random.SystemRandom()
cycle = None
if len(imp) == n:  # tirage entièrement imposé (verrouillé) : on le rejoue tel quel
    d = dict(imp)
    if len(d) != n or len(set(d.values())) != n or any(a == b for a, b in imp):
        sys.exit("Tirage imposé invalide.")
    cur, seq = names[0], []
    for _ in range(n):
        seq.append(cur); cur = d[cur]
    if cur != names[0] or len(set(seq)) != n:
        sys.exit("Le tirage imposé n'est pas un seul grand cycle.")
    cycle = seq
for _ in range(0 if cycle else 200000):
    order = names[:]
    rng.shuffle(order)
    suite = {order[i]: order[(i + 1) % n] for i in range(n)}
    if all((a, suite[a]) not in forb for a in names) and all(suite[a] == b for a, b in imp):
        cycle = order
        break
if cycle is None:
    sys.exit("Aucun tirage possible avec ces exceptions.")
dest = {cycle[i]: cycle[(i + 1) % n] for i in range(n)}
if APERCU:
    for a in cycle:
        print(a, "->", dest[a])
    sys.exit(0)

b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
data = {"v": 1, "p": {}}
vdir = cfg.get("voix_dir")
vout = os.path.join(here, "..", "voix")
if vdir:
    os.makedirs(vout, exist_ok=True)
    shutil.copyfile(os.path.join(vdir, "intro.mp3"), os.path.join(vout, "intro.mp3"))
rows = []
base = sys.argv[1] if len(sys.argv) > 1 else "https://ara-maker-hub.github.io/santa-secret/"
for i, nom in enumerate(names, 1):
    pid = f"p{i:02d}"
    key = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    clair = json.dumps({"de": nom, "pour": dest[nom], "date": cfg["date_revelation"]}, ensure_ascii=False).encode()
    ct = AESGCM(key).encrypt(iv, clair, None)
    data["p"][pid] = b64(iv + ct)
    if vdir:
        # nom du fichier voix = début du SHA-256 de la clé : introuvable sans le lien personnel
        shutil.copyfile(os.path.join(vdir, pid + ".mp3"), os.path.join(vout, hashlib.sha256(key).hexdigest()[:16] + ".mp3"))
    rows.append((nom, dest[nom], f"{base}#{pid}.{b64(key)}"))
json.dump(data, open(os.path.join(here, "..", "data.json"), "w"), indent=1)

with open(os.path.join(here, "liens_et_tirage.md"), "w", encoding="utf-8") as f:
    f.write("# Santa secret : tirage et liens (PRIVÉ, ne pas publier)\n\n")
    f.write("| Participant | Offre à | Lien personnel à envoyer |\n|---|---|---|\n")
    for a, b, l in rows:
        f.write(f"| {a} | {b} | {l} |\n")
    f.write("\nExceptions appliquées (giver -> receveur interdit) : " + (", ".join(f"{a} -> {b}" for a, b in sorted(forb)) or "aucune") + "\n")
print("OK :", n, "participants, tirage en un cycle.")
