"""CCE-2 NLP: merge annotations, measure agreement, and generate insight statistics + figures.

Run from the repository root:  python scripts/analysis.py
Outputs: annotation/annotated_dataset.csv/.xlsx, reports/stats.json, figures/*.png
"""
import json
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SENT = {"P": "Positive", "N": "Negative", "U": "Neutral"}
ASPECT = {"QUAL": "Product Quality", "PERF": "Performance", "VALUE": "Value for Money",
          "DELIV": "Delivery & Packaging", "SERV": "Service & Installation",
          "SIZE": "Size, Fit & Comfort", "DUR": "Durability", "GEN": "General"}
FLAG = {"M": "Mixed", "S": "Sarcasm", "I": "Informal/Code-mixed", "A": "Ambiguous"}
ORDER = ["Positive", "Neutral", "Negative"]
COLORS = {"Positive": "#3a6b5c", "Neutral": "#9a9a9a", "Negative": "#a8473f"}
STOP = set("""a an the is it its this that these those i im me my we our you your u he she they them his her
and or but so if of to in on at for with by from as be been being was were are am do does did done have has had
not no very too also just only than then there here what which who whom when while after before about into over
can could will would should may might must one all any some more most much many such own same other both each few
product products flipkart item thanks thank buy bought get got use used using""".split())
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11})


def cohen_kappa(a, b):
    labels = sorted(set(a) | set(b))
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return po, pe, (po - pe) / (1 - pe)


def load():
    df = pd.read_csv(ROOT / "data" / "flipkart_sample_300_raw.csv")
    rows = []
    for line in (ROOT / "annotation" / "final_labels.txt").read_text().split("\n"):
        if not line.strip():
            continue
        num, s, asp, flags = line.split()
        rows.append({"ID": f"FK{num}", "Final_Sentiment": SENT[s], "Aspect": ASPECT[asp],
                     "Flags": "" if flags == "-" else ", ".join(FLAG[c] for c in flags)})
    df = df.merge(pd.DataFrame(rows), on="ID")
    df["Annotator"] = ["Haziq (A)" if i < 120 else ("Both (overlap)" if i < 180 else "Aditya (B)")
                       for i in range(len(df))]
    df["Word_Count"] = df.Summary.str.split().str.len()
    df["Char_Count"] = df.Summary.str.len()
    df["Dataset_Label"] = df.Sentiment.str.capitalize()
    star = df.Rate.map(lambda r: "Positive" if r >= 4 else ("Neutral" if r == 3 else "Negative"))
    df["Rating_Text_Mismatch"] = (star != df.Final_Sentiment) & (
        ((df.Rate >= 4) & (df.Final_Sentiment == "Negative")) | ((df.Rate <= 2) & (df.Final_Sentiment == "Positive"))
        | ((df.Rate == 3) & (df.Final_Sentiment != "Neutral")))
    return df, star


def agreement(df):
    ov = df[df.Annotator == "Both (overlap)"].copy()
    dis = pd.read_csv(ROOT / "annotation" / "overlap_initial_labels.csv").set_index("ID")
    ov["A"] = [dis.loc[i, "Annotator_A_Haziq"] if i in dis.index else f for i, f in zip(ov.ID, ov.Final_Sentiment)]
    ov["B"] = [dis.loc[i, "Annotator_B_Aditya"] if i in dis.index else f for i, f in zip(ov.ID, ov.Final_Sentiment)]
    po, pe, k = cohen_kappa(list(ov.A), list(ov.B))
    cm = pd.crosstab(ov.A, ov.B).reindex(index=ORDER, columns=ORDER, fill_value=0)
    return ov, {"n": len(ov), "agree": int((ov.A == ov.B).sum()), "po": po, "pe": pe, "kappa": k,
                "confusion": cm.to_dict()}


def top_words(texts, n=10):
    c = Counter()
    for t in texts:
        c.update(w for w in re.findall(r"[a-z]+", t.lower()) if w not in STOP and len(w) > 2)
    return c.most_common(n)


def bigrams(texts, n=10):
    c = Counter()
    for t in texts:
        w = re.findall(r"[a-z]+", t.lower())
        c.update(f"{x} {y}" for x, y in zip(w, w[1:]) if not (x in STOP and y in STOP))
    return c.most_common(n)


def fig_workflow(path):
    steps = [("Kaggle\nSource", "205,052\nreviews"), ("Cleaning &\nFiltering", "57,531\neligible"),
             ("Stratified\nSampling", "300 records\n194 products"), ("Guideline\nDesign", "Labels, rules\nedge cases"),
             ("Independent\nAnnotation", "A: FK001-180\nB: FK121-300"), ("Agreement\nCheck", "60 overlap\nCohen's kappa"),
             ("Review\nMeeting", "Disputes\nadjudicated"), ("Final\nAnnotated Set", "300 gold\nlabels"),
             ("Insight\nGeneration", "Statistics +\nlinguistics"), ("NLP\nReadiness", "Tasks, risks\nimpact")]
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.6); ax.axis("off")
    pos = [(0.15 + i * 1.95, 2.85) for i in range(5)] + [(0.15 + (4 - i) * 1.95, 0.4) for i in range(5)]
    for i, ((x, y), (t, s)) in enumerate(zip(pos, steps)):
        ax.add_patch(FancyBboxPatch((x, y), 1.75, 1.45, boxstyle="round,pad=0.03", fc="white", ec="black", lw=1.1))
        ax.text(x + 0.875, y + 1.02, f"{i + 1}. {t}", ha="center", va="center", fontsize=9.5, fontweight="bold",
                linespacing=1.1)
        ax.text(x + 0.875, y + 0.38, s, ha="center", va="center", fontsize=8.5, linespacing=1.1)
    arrow = dict(arrowstyle="-|>", color="black", lw=1.2)
    for i in range(4):
        ax.annotate("", xy=(pos[i + 1][0] - 0.03, 3.57), xytext=(pos[i][0] + 1.78, 3.57), arrowprops=arrow)
        ax.annotate("", xy=(pos[i + 6][0] + 1.78, 1.12), xytext=(pos[i + 5][0] - 0.03, 1.12), arrowprops=arrow)
    ax.annotate("", xy=(pos[5][0] + 0.875, 1.88), xytext=(pos[4][0] + 0.875, 2.82), arrowprops=arrow)
    ax.annotate("", xy=(pos[3][0] + 0.875, 2.82), xytext=(pos[6][0] + 0.875, 1.88),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1, ls="--"))
    ax.text(pos[3][0] + 0.95, 2.35, "guideline revision", fontsize=8, ha="left", va="center", style="italic")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def main():
    df, star = load()
    ov, agr = agreement(df)
    out = ROOT / "figures"
    stats = {"records": len(df), "products": int(df.product_name.nunique()),
             "avg_words": round(df.Word_Count.mean(), 2), "median_words": float(df.Word_Count.median()),
             "min_words": int(df.Word_Count.min()), "max_words": int(df.Word_Count.max()),
             "avg_chars": round(df.Char_Count.mean(), 1),
             "vocab": len(set(w for t in df.Summary for w in re.findall(r"[a-z]+", t.lower()))),
             "rating_counts": df.Rate.value_counts().sort_index().to_dict(),
             "label_counts": df.Final_Sentiment.value_counts().reindex(ORDER).to_dict(),
             "words_by_label": df.groupby("Final_Sentiment").Word_Count.mean().round(2).to_dict(),
             "aspect_counts": df.Aspect.value_counts().to_dict(),
             "aspect_x_sent": pd.crosstab(df.Aspect, df.Final_Sentiment).reindex(columns=ORDER).to_dict("index"),
             "rating_x_sent": pd.crosstab(df.Rate, df.Final_Sentiment).reindex(columns=ORDER).to_dict("index"),
             "flag_counts": {v: int(df.Flags.str.contains(v).sum()) for v in FLAG.values()},
             "any_flag": int((df.Flags != "").sum()),
             "mismatch": int(df.Rating_Text_Mismatch.sum()),
             "agreement": agr,
             "top_words": {s: top_words(df[df.Final_Sentiment == s].Summary) for s in ORDER},
             "bigrams": bigrams(df.Summary, 12),
             "review_titles_unique": int(df.Review.nunique()),
             "review_title_null": int(df.Review.isna().sum())}
    # agreement of human labels with the dataset's VADER-derived labels and with star rating
    _, _, k_vader = cohen_kappa(list(df.Final_Sentiment), list(df.Dataset_Label))
    _, _, k_star = cohen_kappa(list(df.Final_Sentiment), list(star))
    stats["vs_dataset_label"] = {"agree_pct": round((df.Final_Sentiment == df.Dataset_Label).mean() * 100, 1),
                                 "kappa": round(k_vader, 3),
                                 "crosstab": pd.crosstab(df.Final_Sentiment, df.Dataset_Label).to_dict("index")}
    stats["vs_star"] = {"agree_pct": round((df.Final_Sentiment == star).mean() * 100, 1), "kappa": round(k_star, 3)}

    # figures
    fig_workflow(out / "fig1_workflow.png")

    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    vc = df.Final_Sentiment.value_counts().reindex(ORDER)
    bars = ax.bar(ORDER, vc.values, color=[COLORS[s] for s in ORDER], width=0.6)
    for b, v in zip(bars, vc.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 3, f"{v} ({v / len(df) * 100:.1f}%)", ha="center", fontsize=10)
    ax.set_ylabel("Records"); ax.set_ylim(0, vc.max() * 1.18); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(out / "fig2_label_distribution.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ct = pd.crosstab(df.Rate, df.Final_Sentiment).reindex(columns=ORDER, fill_value=0)
    ax.imshow(ct.values, cmap="Greys", vmin=0, vmax=ct.values.max() * 1.25)
    for i in range(ct.shape[0]):
        for j in range(ct.shape[1]):
            v = ct.values[i, j]
            ax.text(j, i, v, ha="center", va="center", fontsize=11, color="white" if v > ct.values.max() * 0.6 else "black")
    ax.set_xticks(range(3), ORDER); ax.set_yticks(range(ct.shape[0]), [f"{r} star" for r in ct.index])
    ax.set_xlabel("Annotated sentiment (text)"); ax.set_ylabel("Customer star rating")
    fig.tight_layout(); fig.savefig(out / "fig3_rating_vs_sentiment.png", dpi=200); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(8, 3.4), sharex=False)
    for ax, s in zip(axes, ORDER):
        words = stats["top_words"][s][:8][::-1]
        ax.barh([w for w, _ in words], [c for _, c in words], color=COLORS[s])
        ax.set_title(s, fontsize=11, fontweight="bold"); ax.spines[["top", "right"]].set_visible(False)
    fig.supxlabel("Frequency (stop-words removed)", fontsize=10)
    fig.tight_layout(); fig.savefig(out / "fig4_top_words.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.boxplot([df[df.Final_Sentiment == s].Word_Count for s in ORDER], tick_labels=ORDER, widths=0.5,
               medianprops=dict(color="black"))
    ax.set_ylabel("Words per review"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(out / "fig5_length_by_sentiment.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.8))
    at = pd.crosstab(df.Aspect, df.Final_Sentiment).reindex(columns=ORDER, fill_value=0)
    at = at.loc[at.sum(axis=1).sort_values().index]
    left = None
    for s in ORDER:
        ax.barh(at.index, at[s], left=left, color=COLORS[s], label=s)
        left = at[s] if left is None else left + at[s]
    ax.legend(frameon=False, fontsize=9, loc="lower right"); ax.set_xlabel("Records")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(out / "fig6_aspect_sentiment.png", dpi=200); plt.close(fig)

    # annotated dataset export
    cols = ["ID", "product_name", "product_price", "Rate", "Review", "Summary", "Word_Count", "Annotator",
            "Final_Sentiment", "Aspect", "Flags", "Rating_Text_Mismatch", "Dataset_Label"]
    df[cols].to_csv(ROOT / "annotation" / "annotated_dataset.csv", index=False)
    with pd.ExcelWriter(ROOT / "annotation" / "annotated_dataset.xlsx") as xw:
        df[cols].to_excel(xw, sheet_name="Annotated_Dataset", index=False)
        ov[["ID", "Summary", "A", "B", "Final_Sentiment"]].rename(
            columns={"A": "Haziq_Label", "B": "Aditya_Label"}).to_excel(xw, sheet_name="Overlap_Agreement", index=False)
    (ROOT / "reports" / "stats.json").write_text(json.dumps(stats, indent=2, default=str))
    print(json.dumps(stats, indent=1, default=str))


if __name__ == "__main__":
    main()
