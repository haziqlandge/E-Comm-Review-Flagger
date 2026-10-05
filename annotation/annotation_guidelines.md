# Annotation Guidelines v2: Flipkart Product Reviews

**Unit of annotation:** the `Summary` column (the customer's free-text review). Ignore the `Review` column (Flipkart preset headline) and the star rating when assigning sentiment.

## 1. Sentiment (primary label)

| Label | Definition | Include | Exclude | Example |
|---|---|---|---|---|
| Positive | Overall favourable attitude to the product/purchase | Praise, satisfaction, recommendation, value-for-money; positive overall verdict despite a minor drawback | Negated praise ("not good"); praise of a peripheral aspect while the product fails | FK147 "the mivi bar is stunning loving it worth the price" |
| Negative | Overall unfavourable attitude | Defects, failures, safety issues, regret, "dont buy", "waste of money", missing parts, sarcastic criticism | Vague hedges alone ("ok ok") | FK013 "grinder is going to stop immediately while grinding not worth for money" |
| Neutral | No clear polarity, or balanced positives/negatives without a verdict | "ok", "average", balanced contrast, questions, factual statements | Any explicit overall verdict; a clearly dominant concrete defect | FK128 "slow function ok baki all ok" |

## 2. Aspect (secondary label, one per record: the main topic of the opinion)

| Code | Aspect | Covers |
|---|---|---|
| QUAL | Product Quality | material, build, stitching, finish, authenticity |
| PERF | Performance | functional behaviour: sound, cooling, speed, picture, battery |
| DUR | Durability | failure or wear after a period of use |
| VALUE | Value for Money | price, offers, worth for the cost |
| SIZE | Size, Fit & Comfort | dimensions, apparel fit, physical comfort |
| DELIV | Delivery & Packaging | delivery speed, packaging, missing accessories |
| SERV | Service & Installation | installation, demo, customer care, warranty |
| GEN | General | overall opinion without a specific aspect |

## 3. Error-prone flags (zero or more)

- **M** Mixed: both positive and negative evaluations present
- **S** Sarcasm: literal wording differs from intended meaning
- **I** Informal / code-mixed: slang, heavy misspelling, merged words, romanised Hindi
- **A** Ambiguous: intended meaning cannot be determined with confidence

## 4. Decision rules

| Rule | Situation | Decision |
|---|---|---|
| R1 | Explicit overall verdict ("overall good", "rest is good") | Verdict decides the label |
| R2 | Concrete defect + vague hedge ("its okay product, too noisy") | Defect outweighs hedge |
| R3 | Balanced contrast, no verdict ("good but too small") | Neutral, flag M |
| R4 | Core product praised, peripheral aspect criticised | Positive; note aspect |
| R5 | Star rating / headline contradicts text | Label the text only |
| R6 | Sarcasm or irony | Label intended meaning, flag S |
| R7 | Typos, merged words, Hinglish | Most plausible intended meaning, flag I |
| R8 | Questions or purely factual statements | Neutral |
| R9 | Comparison with another product/brand | Stance toward the reviewed product |
| R10 | Conditional / future statements | Currently expressed stance, flag A |

Rules R2, R4 and R7 were added in v2 after the annotation review meeting (see report Table 10).

## 5. Label file format (`final_labels.txt`)

`<number> <P|N|U> <ASPECT> <flags or ->`, e.g. `021 P PERF MI` = FK021, Positive, Performance, Mixed + Informal.
