"""Span normalization corrections for unified entity mentions.

Applies regex-based rules to strip systematic prefixes/suffixes from mention
spans that differ across models (e.g., "the BERT model" -> "BERT").
"""

import re
from collections import defaultdict

from ..types import Corpus, Mention

# Rules are (position, token_pattern_regex) applied per (dataset, label).
# "prefix": match against first token(s), strip if matched
# "suffix": match against last token(s), strip if matched
# Multi-token patterns use " " as separator and match the joined tail/head.

# fmt: off
RULES: dict[str, dict[str, list[tuple[str, str]]]] = {
    "gsap-ere": {
        "Method": [
            ("prefix", r"^(?:the|The|a|A|an|An|our|Our|their|this|This|these|These|its)$"),
        ],
        "_all": [
            ("suffix", r"^'s$"),
        ],
    },
    "scinlp": {
        "Dataset": [
            ("prefix", r"^(?:the|The)$"),
            ("suffix", r"^(?:datasets?|benchmarks?|corpus|sets?)$"),
            ("suffix_multi", r"^(?:test set|data set)$"),
        ],
        "Method": [
            ("prefix", r"^(?:the|The)$"),
        ],
    },
    "scier": {
        "Dataset": [
            ("suffix", r"^(?:corpus|papers|submissions)$"),
        ],
    },
}
# fmt: on


def _apply_rules_to_mention(
    mention: Mention,
    rules: list[tuple[str, str]],
) -> tuple[Mention, list[str]]:
    """Apply normalization rules to a single mention.

    Returns the (possibly modified) mention and a list of applied rule descriptions.
    """
    tokens = mention.text.split(" ")
    applied: list[str] = []

    begin_token = mention.begin_token
    end_token = mention.end_token
    begin = mention.begin
    end = mention.end

    for position, pattern in rules:
        if len(tokens) <= 1:
            # Don't strip if it would empty the mention
            break

        if position == "prefix":
            if re.match(pattern, tokens[0]):
                stripped = tokens[0]
                tokens = tokens[1:]
                # Advance begin by stripped token length + 1 (space separator)
                begin += len(stripped) + 1
                begin_token += 1
                applied.append(f"prefix:{stripped}")

        elif position == "suffix":
            if re.match(pattern, tokens[-1]):
                stripped = tokens[-1]
                tokens = tokens[:-1]
                # Retreat end by stripped token length + 1 (space separator)
                end -= len(stripped) + 1
                end_token -= 1
                applied.append(f"suffix:{stripped}")

        elif position == "suffix_multi":
            # Match last 2 tokens joined by space
            if len(tokens) >= 3:
                tail = " ".join(tokens[-2:])
                if re.match(pattern, tail):
                    stripped = tail
                    tokens = tokens[:-2]
                    end -= len(stripped) + 1
                    end_token -= 2
                    applied.append(f"suffix_multi:{stripped}")

    if not applied:
        return mention, []

    new_text = " ".join(tokens)
    new_mention = Mention(
        id=mention.id,
        document_id=mention.document_id,
        sent_idx=mention.sent_idx,
        text=new_text,
        label=mention.label,
        begin=begin,
        end=end,
        begin_token=begin_token,
        end_token=end_token,
        split=mention.split,
        score=mention.score,
        annotator=mention.annotator,
        dataset=mention.dataset,
        label_original=mention.label_original,
    )
    return new_mention, applied


def normalize_spans(
    corpus: Corpus,
    dataset: str,
    normalize_gold: bool = False,
    normalize_predicted: bool = True,
) -> tuple[Corpus, dict]:
    """Apply span normalization rules to a corpus.

    Strips systematic prefixes/suffixes from mention text based on
    model-specific rules derived from cross-model span difference analysis.

    Args:
        corpus: Input corpus
        dataset: Model/dataset name whose rules to apply ("gsap-ere", "scinlp", "scier")
        normalize_gold: If True, apply to gold mentions
        normalize_predicted: If True, apply to predicted mentions

    Returns:
        Tuple of:
        - New Corpus with normalized mention spans
        - Statistics dict with correction counts
    """
    dataset_rules = RULES.get(dataset, {})

    stats: dict = {
        "gold_corrections": 0,
        "predicted_corrections": 0,
        "corrections_by_rule": defaultdict(int),
        "corrections_by_label": defaultdict(int),
        "examples": [],
    }

    def _process_mentions(mentions: list[Mention]) -> tuple[list[Mention], int]:
        result = []
        count = 0
        for m in mentions:
            # Collect applicable rules: label-specific + _all
            rules = list(dataset_rules.get(m.label, []))
            rules.extend(dataset_rules.get("_all", []))

            if not rules:
                result.append(m)
                continue

            new_m, applied = _apply_rules_to_mention(m, rules)
            result.append(new_m)

            if applied:
                count += 1
                for desc in applied:
                    stats["corrections_by_rule"][desc] += 1
                stats["corrections_by_label"][m.label] += 1
                if len(stats["examples"]) < 20:
                    stats["examples"].append(
                        {
                            "original": m.text,
                            "corrected": new_m.text,
                            "label": m.label,
                            "rules": applied,
                        }
                    )
        return result, count

    # Process gold
    if normalize_gold:
        new_gold, n = _process_mentions(corpus.mentions)
        stats["gold_corrections"] = n
    else:
        new_gold = corpus.mentions

    # Process predicted
    if normalize_predicted:
        new_pred, n = _process_mentions(corpus.mentions_predicted)
        stats["predicted_corrections"] = n
    else:
        new_pred = corpus.mentions_predicted

    # Relations reference Mention objects directly — update subject/object references
    # Since we create new Mention objects, we need to remap relations
    if normalize_gold:
        gold_id_map = {m.id: m for m in new_gold}
        new_gold_rels = []
        for r in corpus.relation:
            subj = gold_id_map.get(r.subject.id, r.subject)
            obj = gold_id_map.get(r.object.id, r.object)
            from ..types import Relation

            new_gold_rels.append(
                Relation(
                    subject=subj,
                    label=r.label,
                    object=obj,
                    score=r.score,
                    annotator=r.annotator,
                    dataset=r.dataset,
                )
            )
    else:
        new_gold_rels = corpus.relation

    if normalize_predicted:
        pred_id_map = {m.id: m for m in new_pred}
        new_pred_rels = []
        for r in corpus.relations_predicted:
            subj = pred_id_map.get(r.subject.id, r.subject)
            obj = pred_id_map.get(r.object.id, r.object)
            from ..types import Relation

            new_pred_rels.append(
                Relation(
                    subject=subj,
                    label=r.label,
                    object=obj,
                    score=r.score,
                    annotator=r.annotator,
                    dataset=r.dataset,
                )
            )
    else:
        new_pred_rels = corpus.relations_predicted

    new_corpus = Corpus(
        sentences=corpus.sentences,
        mentions=new_gold,
        relation=new_gold_rels,
        mentions_predicted=new_pred,
        relations_predicted=new_pred_rels,
    )

    # Convert defaultdicts to regular dicts for serialization
    stats["corrections_by_rule"] = dict(stats["corrections_by_rule"])
    stats["corrections_by_label"] = dict(stats["corrections_by_label"])

    return new_corpus, stats
