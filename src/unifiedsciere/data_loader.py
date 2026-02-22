import json
import os
from itertools import chain
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv

from .types import Corpus, Mention, Relation, Sentence

# Load environment variables
load_dotenv()


def load_corpus(
    dataset: Literal["scier", "scinlp", "gsap"],
    split: Literal["train", "dev", "test"],
    data_type: Literal["gold", "predictions"] = "gold",
    trained_on: Literal["scier", "scinlp", "gsap"] | None = None,
    ner_field: str = "ner",
    rel_field: str = "relations",
) -> Corpus:
    """Load and process corpus data from configured data folders.

    This function reads data folder paths from environment variables:
    - DATA_GOLD_FOLDER: Path to gold standard data
    - DATA_PREDICTIONS_FOLDER: Path to prediction data

    The function automatically constructs filenames based on the dataset and split:
    - For gold data: "{dataset}_{split}.jsonl" (e.g., "scinlp_dev.jsonl")
    - For predictions: "{trained_on}_{dataset}_{split}.jsonl" (e.g., "gsap_scinlp_test.jsonl")

    Args:
        dataset: Dataset to load - "scier", "scinlp", or "gsap"
        split: Data split to load - "train", "dev", or "test"
        data_type: Type of data to load - "gold" or "predictions"
        trained_on: For predictions, the dataset the model was trained on (required if data_type="predictions")
        ner_field: Field name for named entity recognition data
        rel_field: Field name for relations data

    Returns:
        Corpus object containing sentences, mentions, and relations

    Raises:
        ValueError: If environment variables are not set, data folder doesn't exist,
                   or trained_on is not provided for predictions

    Examples:
        >>> # Load gold standard data
        >>> corpus = load_corpus("scinlp", "dev", data_type="gold")

        >>> # Load predictions from a model trained on gsap, evaluated on scinlp test set
        >>> corpus = load_corpus("scinlp", "test", data_type="predictions", trained_on="gsap")
    """
    # Validate and construct filename
    if data_type == "predictions":
        if trained_on is None:
            raise ValueError(
                "trained_on parameter is required when data_type='predictions'. "
                "Specify which dataset the model was trained on (e.g., 'gsap', 'scinlp', 'scier')."
            )
        filename = f"{trained_on}_{dataset}_{split}.jsonl"
    else:
        filename = f"{dataset}_{split}.jsonl"

    # Get data folder from environment
    if data_type == "gold":
        data_folder = os.getenv("DATA_GOLD_FOLDER")
        if not data_folder:
            raise ValueError(
                "DATA_GOLD_FOLDER environment variable not set. "
                "Please create a .env file with DATA_GOLD_FOLDER defined."
            )
    elif data_type == "predictions":
        data_folder = os.getenv("DATA_PREDICTIONS_FOLDER")
        if not data_folder:
            raise ValueError(
                "DATA_PREDICTIONS_FOLDER environment variable not set. "
                "Please create a .env file with DATA_PREDICTIONS_FOLDER defined."
            )
    else:
        raise ValueError(
            f"Invalid data_type: {data_type}. Must be 'gold' or 'predictions'"
        )

    # Convert to Path and verify it exists
    data_path = Path(data_folder)
    if not data_path.exists():
        raise ValueError(f"Data folder does not exist: {data_path}")

    # Load documents using internal function
    docs = _load_docs(data_path, [filename])

    # Determine annotator name
    annotator = "gold" if data_type == "gold" else trained_on

    # Process documents into corpus using internal function
    return _process_docs(
        docs,
        ner_field=ner_field,
        rel_field=rel_field,
        dataset=dataset,
        annotator=annotator,
        is_prediction=(data_type == "predictions"),
    )


def _process_docs(
    docs: list[dict[str, Any]],
    ner_field: str = "ner",
    rel_field: str = "relations",
    dataset: str = "",
    annotator: str = "gold",
    is_prediction: bool = False,
) -> Corpus:
    """Process document dictionaries into Corpus structure (internal function).

    Args:
        docs: List of document dictionaries
        ner_field: Field name for named entity recognition data
        rel_field: Field name for relations data
        dataset: Dataset name (e.g., "gsap", "scier", "scinlp")
        annotator: Annotator name ("gold" or model name)
        is_prediction: Whether this is prediction data (loads predicted fields)

    Returns:
        Corpus object containing sentences, mentions, and relations
    """
    sentences: list[Sentence] = []
    mentions: dict[str, Mention] = {}
    relations: list[Relation] = []
    mentions_predicted: dict[str, Mention] = {}
    relations_predicted: list[Relation] = []
    mentions_by_span: dict[tuple[str, int, int], list[Mention]] = {}
    mentions_predicted_by_span: dict[tuple[str, int, int], list[Mention]] = {}
    ambiguity_stats_gold: dict[tuple[str, str, str, str], int] = {}
    ambiguity_stats_pred: dict[tuple[str, str, str, str], int] = {}
    missing_relations_gold = 0
    missing_relations_pred = 0
    missing_relations_gold_logged = 0
    missing_relations_pred_logged = 0
    missing_relations_log_limit = 5
    deprecated_relation_labels = {"versionOf", "processed"}

    def _record_ambiguity(
        stats: dict[tuple[str, str, str, str], int],
        selected_label: str,
        other_label: str,
        relation_label: str,
        role: str,
    ) -> None:
        key = (selected_label, other_label, relation_label, role)
        stats[key] = stats.get(key, 0) + 1

    def _select_mention(
        candidates: list[Mention],
        relation_label: str,
        role: str,
        stats: dict[tuple[str, str, str, str], int],
    ) -> Mention | None:
        if not candidates:
            return None
        preferred_order: dict[tuple[str, str], list[str]] = {
            ("architecture", "object"): ["ModelArchitecture", "MLModelGeneric"],
            ("architecture", "subject"): ["MLModelGeneric", "ModelArchitecture"],
            ("usedFor", "subject"): ["Method", "MLModelGeneric"],
            ("usedFor", "object"): ["MLModelGeneric", "Method"],
            ("sourcedFrom", "object"): ["DataSource", "DatasetGeneric"],
            ("sourcedFrom", "subject"): ["DatasetGeneric", "DataSource"],
            ("trainedOn", "subject"): ["DatasetGeneric", "DataSource"],
            ("appliedTo", "subject"): ["MLModelGeneric", "ModelArchitecture"],
        }
        priority = preferred_order.get((relation_label, role))
        if priority:
            rank = {label: idx for idx, label in enumerate(priority)}
            ordered = sorted(
                candidates,
                key=lambda m: (rank.get(m.label, len(rank)), m.label),
            )
        else:
            ordered = sorted(candidates, key=lambda m: m.label)
        selected = ordered[0]
        if len(candidates) > 1:
            for other in ordered[1:]:
                _record_ambiguity(
                    stats, selected.label, other.label, relation_label, role
                )
        return selected

    for doc in docs:
        pos: int = -1
        begins: list[int] = []
        ends: list[int] = []
        for sent in doc["sentences"]:
            for token in sent:
                pos += 1
                begins.append(pos)
                pos += len(token)
                ends.append(pos)
        split = doc["split"]
        # doc_key is set by _load_docs to either the original doc_key (SCINLP) or doc_id (SCIER/GSAP)
        doc_id = doc["doc_key"]
        doc_token = list(chain(*doc["sentences"]))
        for sent_idx, sent in enumerate(doc["sentences"]):
            sent_text = " ".join(sent)
            sentence = Sentence(sent_text, doc_id, sent_idx, split)
            sentences.append(sentence)
            # Process gold mentions
            sent_ner = doc[ner_field][sent_idx]
            sentence.n_mentions = len(sent_ner)
            for begin_token, end_token, label in sent_ner:
                token = doc_token[begin_token : end_token + 1]
                begin = begins[begin_token]
                end = ends[end_token]
                text = " ".join(token)
                mention_id = f"{doc_id} {begin_token} {end_token} {label}"
                mention = Mention(
                    mention_id,
                    doc_id,
                    sent_idx,
                    text,
                    label,
                    begin,
                    end,
                    begin_token,
                    end_token,
                    split,
                    score=1.0,
                    annotator=annotator if not is_prediction else "gold",
                    dataset=dataset,
                )
                if mention_id in mentions:
                    print(f"Warning: Duplicate mention ID {mention_id}, skipping")
                    continue
                mentions[mention_id] = mention
                span_key = (doc_id, begin_token, end_token)
                mentions_by_span.setdefault(span_key, []).append(mention)

            # Process gold relations
            sent_rels = doc[rel_field][sent_idx]
            for sub_begin, sub_end, obj_begin, obj_end, label in sent_rels:
                if label in deprecated_relation_labels:
                    continue
                try:
                    subj_candidates = mentions_by_span.get(
                        (doc_id, sub_begin, sub_end), []
                    )
                    obj_candidates = mentions_by_span.get(
                        (doc_id, obj_begin, obj_end), []
                    )
                    subj = _select_mention(
                        subj_candidates,
                        relation_label=label,
                        role="subject",
                        stats=ambiguity_stats_gold,
                    )
                    obj = _select_mention(
                        obj_candidates,
                        relation_label=label,
                        role="object",
                        stats=ambiguity_stats_gold,
                    )
                    if subj and obj:
                        rel = Relation(
                            subj,
                            label,
                            obj,
                            score=1.0,
                            annotator=annotator if not is_prediction else "gold",
                            dataset=dataset,
                        )
                        relations.append(rel)
                    else:
                        missing_relations_gold += 1
                        if missing_relations_gold_logged < missing_relations_log_limit:
                            missing_relations_gold_logged += 1
                            print(
                                "Warning: Missing gold relation endpoints "
                                f"(doc={doc_id} sent={sent_idx} "
                                f"sub=({sub_begin},{sub_end}) obj=({obj_begin},{obj_end}) "
                                f"label={label})"
                            )
                except Exception as e:
                    print(e)

            # Process predicted mentions if available
            if is_prediction and "predicted_ner_proba" in doc:
                sent_ner_pred = doc["predicted_ner_proba"][sent_idx]
                for item in sent_ner_pred:
                    begin_token, end_token, label, score = (
                        item[0],
                        item[1],
                        item[2],
                        item[3],
                    )
                    token = doc_token[begin_token : end_token + 1]
                    begin = begins[begin_token]
                    end = ends[end_token]
                    text = " ".join(token)
                    mention_id = f"{doc_id} {begin_token} {end_token} {label}"
                    mention = Mention(
                        mention_id,
                        doc_id,
                        sent_idx,
                        text,
                        label,
                        begin,
                        end,
                        begin_token,
                        end_token,
                        split,
                        score=float(score),
                        annotator=annotator,
                        dataset=dataset,
                    )
                    if mention_id in mentions_predicted:
                        print(
                            f"Warning: Duplicate predicted mention ID {mention_id}, skipping"
                        )
                        continue
                    mentions_predicted[mention_id] = mention
                    span_key = (doc_id, begin_token, end_token)
                    mentions_predicted_by_span.setdefault(span_key, []).append(mention)

            # Process predicted relations if available
            if is_prediction and "predicted_rel_proba" in doc:
                sent_rel_pred = doc["predicted_rel_proba"][sent_idx]
                for item in sent_rel_pred:
                    sub_begin, sub_end, obj_begin, obj_end, label, score = (
                        item[0],
                        item[1],
                        item[2],
                        item[3],
                        item[4],
                        item[5],
                    )
                    if label in deprecated_relation_labels:
                        continue
                    try:
                        subj_candidates = mentions_predicted_by_span.get(
                            (doc_id, sub_begin, sub_end), []
                        )
                        obj_candidates = mentions_predicted_by_span.get(
                            (doc_id, obj_begin, obj_end), []
                        )
                        if not subj_candidates:
                            subj_candidates = mentions_by_span.get(
                                (doc_id, sub_begin, sub_end), []
                            )
                        if not obj_candidates:
                            obj_candidates = mentions_by_span.get(
                                (doc_id, obj_begin, obj_end), []
                            )
                        subj = _select_mention(
                            subj_candidates,
                            relation_label=label,
                            role="subject",
                            stats=ambiguity_stats_pred,
                        )
                        obj = _select_mention(
                            obj_candidates,
                            relation_label=label,
                            role="object",
                            stats=ambiguity_stats_pred,
                        )
                        if subj and obj:
                            rel = Relation(
                                subj,
                                label,
                                obj,
                                score=float(score),
                                annotator=annotator,
                                dataset=dataset,
                            )
                            relations_predicted.append(rel)
                        else:
                            missing_relations_pred += 1
                            if (
                                missing_relations_pred_logged
                                < missing_relations_log_limit
                            ):
                                missing_relations_pred_logged += 1
                                print(
                                    "Warning: Missing predicted relation endpoints "
                                    f"(doc={doc_id} sent={sent_idx} "
                                    f"sub=({sub_begin},{sub_end}) obj=({obj_begin},{obj_end}) "
                                    f"label={label})"
                                )
                    except Exception as e:
                        print(e)

    corpus = Corpus(
        sentences,
        list(mentions.values()),
        relations,
        list(mentions_predicted.values()),
        relations_predicted,
    )
    corpus.ambiguity_stats_gold = ambiguity_stats_gold
    corpus.ambiguity_stats_pred = ambiguity_stats_pred
    corpus.missing_relations_gold = missing_relations_gold
    corpus.missing_relations_pred = missing_relations_pred
    return corpus


def _load_docs(path: Path, fns: list[str]) -> list[dict[str, Any]]:
    """Load documents from JSONL files (internal function).

    Args:
        path: Directory path containing the JSONL files
        fns: List of filenames to load

    Returns:
        List of document dictionaries
    """
    docs: list[dict[str, Any]] = []

    for fn in fns:
        path_split = path / fn
        split = path_split.stem
        print(split)
        jsonl_file = path_split.open()
        for line_idx, line in enumerate(jsonl_file):
            doc = json.loads(line)
            doc["split"] = split
            # Ensure doc_key exists: use doc_id if available (SCIER/GSAP), otherwise generate one
            if "doc_key" not in doc:
                if "doc_id" in doc:
                    doc["doc_key"] = doc["doc_id"]
                else:
                    doc["doc_key"] = f"{split}_{line_idx}"
            docs.append(doc)
    return docs
