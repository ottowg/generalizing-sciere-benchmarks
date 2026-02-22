# Data Model

All core types are defined in `src/unifiedsciere/types.py`.

## ERE Types

### Sentence

A single sentence from a scientific document.

| Field | Type | Description |
|-------|------|-------------|
| `text` | str | Sentence text |
| `doc_id` | str | Document identifier |
| `idx` | int | Sentence index within document |
| `split` | str | "train", "dev", or "test" |
| `n_mentions` | int | Number of entity mentions in this sentence |

Property: `id` = `"{doc_id} {idx}"`

### Mention

An entity mention (named entity span) within text.

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier (`"{doc_id} {begin_token} {end_token} {label}"`) |
| `document_id` | str | Document identifier |
| `sent_idx` | str | Sentence index |
| `text` | str | Surface form |
| `label` | str | Entity type (unified or original) |
| `begin` / `end` | int | Character offsets |
| `begin_token` / `end_token` | int | Token offsets (inclusive) |
| `split` | str | Data split |
| `score` | float | Confidence (1.0 for gold) |
| `annotator` | str | "gold" or model name ("gsap", "scier", "scinlp") |
| `dataset` | str | Source dataset |
| `label_original` | str | Original label before unification (empty until mapped) |

### Relation

A typed relationship between two entity mentions.

| Field | Type | Description |
|-------|------|-------------|
| `subject` | Mention | Subject entity |
| `label` | str | Relation type |
| `object` | Mention | Object entity |
| `score` | float | Confidence (1.0 for gold) |
| `annotator` | str | "gold" or model name |
| `dataset` | str | Source dataset |

Properties: `signature` = `(subject.label, label, object.label)`,
`split`, `document_id`, `sent_idx`, token positions for both subject and object.

### Corpus

Container for a loaded dataset split.

| Field | Type | Description |
|-------|------|-------------|
| `sentences` | list[Sentence] | All sentences |
| `mentions` | list[Mention] | Gold entity mentions |
| `relation` | list[Relation] | Gold relations |
| `mentions_predicted` | list[Mention] | Predicted entity mentions |
| `relations_predicted` | list[Relation] | Predicted relations |

Additional attributes set after loading: `ambiguity_stats_gold`,
`ambiguity_stats_pred`, `missing_relations_gold`, `missing_relations_pred`.

Method: `format_relation(relation_id, predicted=False)` — returns a
formatted string with sentence context and relation triple.

## Metadata Types

### PaperMetadata

Bibliographic metadata for a paper, normalised across arXiv (GSAP),
Semantic Scholar (SciER), and ACL Anthology (SciNLP).

Key fields: `doc_id`, `dataset`, `split`, `title`, `authors`, `year`,
`venue`, `abstract`, `article_type`, `conference`, `doi`, `arxiv_id`,
`acl_id`, `s2_corpus_id`, `dblp_id`, `outlet_id`, `repositories`.

Methods: `to_dict()`, `to_bib()`.

### Outlet

A publication venue (conference, journal, workshop, or preprint server).

Key fields: `id`, `name`, `abbr`, `outlet_type`, `outlet_topic`,
`dblp_outlet_id`, `identification_pattern`.

### RepositoryLink

A link to a paper in a digital library (arXiv, ACL Anthology, Semantic
Scholar, DBLP).

Fields: `repository`, `url_landing_page`, `url_pdf`, `url_repository`.
