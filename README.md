# CCE-2: Dataset Annotation & Insight Generation (Flipkart Product Reviews)

Natural Language Processing Lab, TY B.Tech. Computer Engineering, SAKEC (A.Y. 2026-27)
Team: Haziq Landge (36, 124BTCM1193), Aditya Madhavi (37, 124BTCM1163). Guide: Ms. Shreyasee Patra

**Domain:** E-Commerce Reviews. **Task:** 3-class sentiment (Positive / Neutral / Negative) + aspect + error-prone flags on 300 reviews.

## Folder guide

| Path | Contents |
|---|---|
| `data/flipkart_sample_300_raw.csv` | 300 sampled raw records (IDs FK001-FK300) with original source columns |
| `annotation/annotation_guidelines.md` | Label definitions, aspects, flags, decision rules R1-R10 |
| `annotation/final_labels.txt` | Final adjudicated labels (compact format) |
| `annotation/overlap_initial_labels.csv` | Both annotators' pre-adjudication labels for disputed overlap records |
| `annotation/annotated_dataset.xlsx` / `.csv` | Final annotated dataset + overlap agreement sheet |
| `scripts/sample_dataset.py` | Cleaning, filtering and stratified sampling from the Kaggle file |
| `scripts/analysis.py` | Agreement (Cohen's kappa), statistics, all figures |
| `figures/` | Figures used in the report |
| `reports/stats.json` | All computed statistics |

## Key results

- Inter-annotator agreement on 60 overlap records: 85.0%, Cohen's kappa = 0.735 (substantial)
- Final labels: Positive 160 (53.3%), Negative 116 (38.7%), Neutral 24 (8.0%)
- Agreement with the source's VADER-derived labels: 80.0% (kappa 0.638)
- Only 12 of 60 three-star reviews are neutral in text

## Reproduce

```bash
pip install pandas matplotlib openpyxl
python scripts/sample_dataset.py path/to/Dataset-SA.csv   # optional: re-draw the sample
python scripts/analysis.py                                  # agreement, stats, figures, xlsx
```

## Source

N. Vaghani, "Flipkart Product reviews with sentiment Dataset", Kaggle, 2023.
https://www.kaggle.com/datasets/niraliivaghani/flipkart-product-customer-reviews-dataset (DbCL v1.0).
