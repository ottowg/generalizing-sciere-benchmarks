"""Example usage of the UnifiedSciERE data loader."""

from src.unifiedsciere.data_loader import load_corpus

# Example 1: Load gold standard data
print("=" * 60)
print("Example 1: Loading gold standard data")
print("=" * 60)
corpus_gold = load_corpus(
    dataset="scinlp",  # Dataset: scier, scinlp, or gsap
    split="dev",  # Split: train, dev, or test
    data_type="gold",  # Load gold standard annotations
)

print(f"Loaded gold corpus with:")
print(f"  - {len(corpus_gold.sentences)} sentences")
print(f"  - {len(corpus_gold.mentions)} mentions")
print(f"  - {len(corpus_gold.relation)} relations")

# Example 2: Load predictions from a model trained on GSAP, evaluated on SciNLP test set
print("\n" + "=" * 60)
print("Example 2: Loading prediction data")
print("=" * 60)
corpus_pred = load_corpus(
    dataset="scinlp",  # Dataset to evaluate on
    split="test",  # Split: train, dev, or test
    data_type="predictions",  # Load model predictions
    trained_on="gsap",  # Model was trained on GSAP dataset
)

print(f"Loaded prediction corpus with:")
print(f"  - {len(corpus_pred.sentences)} sentences")
print(f"  - {len(corpus_pred.mentions)} mentions")
print(f"  - {len(corpus_pred.relation)} relations")

# Example 3: Accessing corpus data
print("\n" + "=" * 60)
print("Example 3: Accessing corpus data")
print("=" * 60)

# Access first sentence
if corpus_gold.sentences:
    first_sentence = corpus_gold.sentences[0]
    print(f"\nFirst sentence:")
    print(f"  ID: {first_sentence.id}")
    print(f"  Text: {first_sentence.text[:100]}...")  # First 100 chars
    print(f"  Mentions: {first_sentence.n_mentions}")

# Access first mention
if corpus_gold.mentions:
    first_mention = corpus_gold.mentions[0]
    print(f"\nFirst mention:")
    print(f"  ID: {first_mention.id}")
    print(f"  Text: {first_mention.text}")
    print(f"  Label: {first_mention.label}")

# Access first relation
if corpus_gold.relation:
    first_relation = corpus_gold.relation[0]
    print(f"\nFirst relation:")
    print(f"  Subject: {first_relation.subject.text} ({first_relation.subject.label})")
    print(f"  Relation: {first_relation.label}")
    print(f"  Object: {first_relation.object.text} ({first_relation.object.label})")

# Example 4: Loading different dataset combinations
print("\n" + "=" * 60)
print("Example 4: Other dataset combinations")
print("=" * 60)

# Load SciER training data (gold)
corpus_scier_train = load_corpus("scier", "train", data_type="gold")
print(f"SciER train (gold): {len(corpus_scier_train.sentences)} sentences")

# Load predictions from SciNLP model on GSAP test set
corpus_scinlp_on_gsap = load_corpus(
    "gsap", "test", data_type="predictions", trained_on="scinlp"
)
print(f"SciNLP→GSAP predictions: {len(corpus_scinlp_on_gsap.sentences)} sentences")

# Load predictions from SciER model on SciER test set
corpus_scier_on_scier = load_corpus(
    "scier", "test", data_type="predictions", trained_on="scier"
)
print(f"SciER→SciER predictions: {len(corpus_scier_on_scier.sentences)} sentences")
