"""Inject the annotated dataset and statistics into website/template.html -> website/index.html.

Run from the repository root after scripts/analysis.py:  python website/build_site.py
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SHORT = {"Positive": "P", "Neutral": "U", "Negative": "N"}
ASPECT = {"Product Quality": "QUAL", "Performance": "PERF", "Value for Money": "VALUE",
          "Delivery & Packaging": "DELIV", "Service & Installation": "SERV",
          "Size, Fit & Comfort": "SIZE", "Durability": "DUR", "General": "GEN"}
FLAG = {"Mixed": "M", "Sarcasm": "S", "Informal/Code-mixed": "I", "Ambiguous": "A"}

DISPUTES = [
    ("FK127", "U", "P", "U", "R3", "Praise is hedged (\"good good ok ok\") and followed by a complaint about a missing adaptor. No overall verdict."),
    ("FK133", "U", "N", "N", "R2", "\"its okay product\" is a hedge. The concrete defects, noise and humidity, dominate."),
    ("FK141", "P", "U", "P", "R1", "\"basic\" names the product category, not an evaluation. \"very good product\" is explicit."),
    ("FK144", "P", "N", "P", "R7", "\"so complaints\" is a typo for \"no complaints\", read alongside \"good for the price\"."),
    ("FK149", "P", "U", "P", "R4", "The product is praised. Only packaging, a peripheral aspect, is criticised."),
    ("FK155", "N", "U", "N", "R2", "A foot hitting the front wheel is a functional design flaw. \"looks ok\" is secondary."),
    ("FK166", "P", "U", "P", "R1", "Explicit verdict: \"it is good for all kind of grounds\". The scratches are minor."),
    ("FK172", "N", "U", "N", "-", "The complaint is about price, not the product, but the attitude (\"pathetic\") is clearly negative."),
    ("FK173", "U", "P", "P", "R1", "Explicit verdict \"overall very good\". The warranty clause is unclear, so it is flagged Ambiguous."),
]
EXTRA_PRACTICE = [
    ("FK018", "R3", "Sound praised, wall mount called \"very bad\". Five stars, but the text is balanced with no verdict."),
    ("FK029", "R5", "Five stars and the headline \"brilliant\", yet the text says \"third class product\". Label the text."),
    ("FK176", "R6", "\"is it a heater or vacuum cleaner\" mocks overheating. Label the intended meaning."),
]
RULES = {
    "R1": "Explicit overall verdict decides the label",
    "R2": "A concrete defect outweighs a vague hedge",
    "R3": "Balanced contrast without a verdict is Neutral",
    "R4": "Core product praised, peripheral aspect criticised: Positive",
    "R5": "Label the text, never the star rating or headline",
    "R6": "Sarcasm: label the intended meaning",
    "R7": "Typos and Hinglish: label the most plausible meaning",
    "R8": "Questions and purely factual statements are Neutral",
    "R9": "Comparisons: stance towards the reviewed product",
    "R10": "Conditional or future statements: current stance, flag Ambiguous",
}


def main():
    df = pd.read_csv(ROOT / "annotation" / "annotated_dataset.csv")
    stats = json.loads((ROOT / "reports" / "stats.json").read_text())
    recs = []
    for r in df.itertuples():
        name = re.sub(r"\s+", " ", str(r.product_name)).strip()
        recs.append({
            "id": r.ID, "t": r.Summary, "r": int(r.Rate),
            "p": int(r.product_price) if str(r.product_price).isdigit() else None,
            "n": name if len(name) <= 70 else name[:68].rsplit(" ", 1)[0] + "...",
            "h": "" if pd.isna(r.Review) else str(r.Review),
            "s": SHORT[r.Final_Sentiment], "a": ASPECT[r.Aspect],
            "f": "" if pd.isna(r.Flags) else "".join(FLAG[x.strip()] for x in r.Flags.split(",")),
            "d": SHORT[r.Dataset_Label],
            "an": {"Haziq (A)": "A", "Aditya (B)": "B"}.get(r.Annotator, "AB"),
            "w": int(r.Word_Count),
        })
    practice = [{"id": i, "a": a, "b": b, "final": f, "rule": rule, "why": why} for i, a, b, f, rule, why in DISPUTES]
    final = {x["id"]: x["s"] for x in recs}
    practice += [{"id": i, "a": final[i], "b": final[i], "final": final[i], "rule": rule, "why": why}
                 for i, rule, why in EXTRA_PRACTICE]
    payload = {"records": recs, "stats": stats, "practice": practice, "rules": RULES}
    tpl = (ROOT / "website" / "template.html").read_text(encoding="utf8")
    blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    out = tpl.replace("/*__DATA__*/null", blob)
    # artifact.html: body fragment (the artifact host adds the document skeleton at publish time)
    (ROOT / "website" / "artifact.html").write_text(out, encoding="utf8")
    # index.html: full standalone document for localhost / opening from disk
    head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
    page = head + out.replace("</style>", "</style>\n</head>\n<body>", 1) + "\n</body>\n</html>\n"
    (ROOT / "website" / "index.html").write_text(page, encoding="utf8")
    print(f"wrote website/index.html and artifact.html ({len(out) / 1024:.0f} KB, {len(recs)} records)")


if __name__ == "__main__":
    main()
