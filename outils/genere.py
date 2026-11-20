#!/usr/bin/env python3
"""Tirage Santa secret : un seul grand cycle (personne ne se tire soi-même, pas de duo A<->B).
Exceptions dans config.json : [["Giver","Receveur interdit"], ...] (sens unique).
Sorties : ../site/data.json (chiffré, public) et liens_et_tirage.md (PRIVÉ, pour Driss)."""
import json, secrets, base64, os, sys, random
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

rng = random.SystemRandom()
cycle = None
for _ in range(200000):
    order = names[:]
    rng.shuffle(order)
    if all((order[i], order[(i + 1) % n]) not in forb for i in range(n)):
        cycle = order
        break
if cycle is None:
    sys.exit("Aucun tirage possible avec ces exceptions.")
dest = {cycle[i]: cycle[(i + 1) % n] for i in range(n)}

b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
data = {"v": 1, "p": {}}
rows = []
base = sys.argv[1] if len(sys.argv) > 1 else "https://ara-maker-hub.github.io/santa-secret/"
for i, nom in enumerate(names, 1):
    pid = f"p{i:02d}"
    key = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    clair = json.dumps({"de": nom, "pour": dest[nom], "date": cfg["date_revelation"]}, ensure_ascii=False).encode()
    ct = AESGCM(key).encrypt(iv, clair, None)
    data["p"][pid] = b64(iv + ct)
    rows.append((nom, dest[nom], f"{base}#{pid}.{b64(key)}"))
json.dump(data, open(os.path.join(here, "..", "data.json"), "w"), indent=1)

with open(os.path.join(here, "liens_et_tirage.md"), "w", encoding="utf-8") as f:
    f.write("# Santa secret : tirage et liens (PRIVÉ, ne pas publier)\n\n")
    f.write("| Participant | Offre à | Lien personnel à envoyer |\n|---|---|---|\n")
    for a, b, l in rows:
        f.write(f"| {a} | {b} | {l} |\n")
    f.write("\nExceptions appliquées (giver -> receveur interdit) : " + (", ".join(f"{a} -> {b}" for a, b in sorted(forb)) or "aucune") + "\n")
print("OK :", n, "participants, tirage en un cycle.")
