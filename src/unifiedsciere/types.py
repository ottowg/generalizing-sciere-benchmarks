from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field


@dataclass
class Sentence:
    text: str
    doc_id: str
    idx: int
    split: str
    n_mentions: int = 0
    tokens: list[str] = field(default_factory=list)

    @property
    def id(self):
        return f"{self.doc_id} {self.idx}"

    @property
    def n_tokens(self) -> int:
        """Number of tokens (uses gold tokenization when available, falls back to whitespace split)."""
        return len(self.tokens) if self.tokens else len(self.text.split())


@dataclass
class Mention:
    id: str
    document_id: str
    sent_idx: str
    text: str
    label: str
    begin: int
    end: int
    begin_token: int
    end_token: int
    split: str
    score: float = 1.0  # Confidence score (1.0 for gold annotations)
    annotator: str = "gold"  # "gold" or model name (e.g., "gsap-ere", "scier", "scinlp")
    dataset: str = ""  # Dataset name (e.g., "gsap-ere", "scier", "scinlp")
    label_original: str = ""  # Original label before unification mapping


@dataclass
class Relation:
    subject: Mention
    label: str
    object: Mention
    score: float = 1.0  # Confidence score (1.0 for gold annotations)
    annotator: str = "gold"  # "gold" or model name (e.g., "gsap-ere", "scier", "scinlp")
    dataset: str = ""  # Dataset name (e.g., "gsap-ere", "scier", "scinlp")

    @property
    def signature(self):
        return self.subject.label, self.label, self.object.label

    @property
    def split(self):
        return self.subject.split

    @property
    def document_id(self):
        return self.subject.document_id

    @property
    def sent_idx(self):
        return self.subject.sent_idx

    @property
    def subject_begin_token(self):
        return self.subject.begin_token

    @property
    def subject_end_token(self):
        return self.subject.end_token

    @property
    def object_begin_token(self):
        return self.object.begin_token

    @property
    def object_end_token(self):
        return self.object.end_token


@dataclass
class Outlet:
    """Publication outlet (conference, journal, workshop, or preprint server).

    Fields mirror the schema in ``data/metadata/outlet_info.json``.
    """

    id: str  # e.g. "outlet_000"
    name: str  # e.g. "Annual Meeting of the Association for Computational Linguistics"
    abbr: str = ""  # e.g. "ACL"
    outlet_type: str = ""  # "conference", "journal", "workshop", "preprint"
    outlet_topic: str = ""  # e.g. "Natural Language Processing"
    wikidata_id: str = ""  # e.g. "Q2992422"
    canonical_url: str = ""  # e.g. "https://aclanthology.org/"
    dblp_outlet_id: str = ""  # e.g. "conf/cvpr" or "journals/corr"
    identification_pattern: str = ""  # regex used for matching venue strings

    # ── OpenAlex enrichment ───────────────────────────────────────────────
    openalex_id: str = ""  # e.g. "S137773608" (short form without URL prefix)
    issn_l: str = ""  # linking ISSN (mainly for journals)
    h_index: int | None = None  # H-index from OpenAlex summary_stats
    i10_index: int | None = None  # i10-index from OpenAlex summary_stats
    works_count: int | None = None  # total indexed works in OpenAlex
    cited_by_count: int | None = None  # total citation count in OpenAlex
    mean_citedness_2yr: float | None = None  # 2-year mean citedness (impact factor proxy)
    openalex_type: str = ""  # source type as reported by OpenAlex (e.g. "conference")
    openalex_topics: list[str] = field(default_factory=list)  # top topic display names

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "abbr": self.abbr,
            "outlet_type": self.outlet_type,
            "outlet_topic": self.outlet_topic,
            "wikidata_id": self.wikidata_id,
            "canonical_url": self.canonical_url,
            "dblp_outlet_id": self.dblp_outlet_id,
            "identification_pattern": self.identification_pattern,
            # OpenAlex fields
            "openalex_id": self.openalex_id,
            "issn_l": self.issn_l,
            "h_index": self.h_index,
            "i10_index": self.i10_index,
            "works_count": self.works_count,
            "cited_by_count": self.cited_by_count,
            "mean_citedness_2yr": self.mean_citedness_2yr,
            "openalex_type": self.openalex_type,
            "openalex_topics": self.openalex_topics,
        }


@dataclass
class RepositoryLink:
    """Link to a paper in a specific repository / digital library.

    Each repository entry captures the landing page, the direct PDF link
    (if available), and the repository's base URL for reference.
    """

    repository: str  # e.g. "arxiv", "acl_anthology", "semantic_scholar", "dblp"
    url_landing_page: str = ""  # paper's landing / abstract page
    url_pdf: str = ""  # direct PDF full-text link (empty if unavailable)
    url_repository: str = ""  # repository home page

    # (internal, not part of the public API)
    _REPO_URLS: dict[str, str] = field(
        default=None,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        _REPO_URLS = {
            "arxiv": "https://arxiv.org",
            "acl_anthology": "https://aclanthology.org",
            "semantic_scholar": "https://www.semanticscholar.org",
            "dblp": "https://dblp.org",
        }
        if not self.url_repository:
            self.url_repository = _REPO_URLS.get(self.repository, "")

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "url_landing_page": self.url_landing_page,
            "url_pdf": self.url_pdf,
            "url_repository": self.url_repository,
        }


@dataclass
class PaperMetadata:
    """Bibliographic metadata for a single paper in the unified corpus.

    Normalises the fields returned by arXiv (GSAP), Semantic Scholar (SciER),
    and the ACL Anthology (SciNLP) into a single schema.
    """

    # ── identity ──────────────────────────────────────────────────────────
    doc_id: str  # dataset-internal document id (e.g. "00015_1910_09700.txt")
    dataset: str  # source corpus: "gsap-ere", "scier", "scier_ood", "scinlp"
    split: str  # data split: "train", "dev", "test"

    # ── core bibliographic fields ─────────────────────────────────────────
    title: str = ""
    authors: list[str] = field(default_factory=list)  # ["First Last", ...]
    year: int | None = None  # publication year (from metadata source)
    venue: str = ""  # full venue string (proceedings title / journal name)
    abstract: str = ""

    # ── publication type & venue details ───────────────────────────────────
    article_type: str = ""  # "conference_proceeding", "journal", "preprint"
    conference: str = ""  # short conference name, e.g. "ACL", "NeurIPS", "CVPR"
    conference_year: int | None = (
        None  # year the conference was held (may differ from publication year)
    )

    # ── persistent identifiers ────────────────────────────────────────────
    doi: str = ""  # preferred published-venue DOI, e.g. "10.18653/v1/2020.acl-main.21"
                   # empty for preprint-only papers
    doi_preprint: str = ""  # arXiv preprint DOI, e.g. "10.48550/arXiv.1910.09700"
                            # (derivable from arxiv_id as "10.48550/arXiv.{arxiv_id}")
    arxiv_id: str = ""  # e.g. "1910.09700" (without version suffix)
    acl_id: str = ""  # e.g. "2020.acl-main.21"
    s2_corpus_id: str = ""  # Semantic Scholar corpus id
    s2_paper_id: str = ""  # Semantic Scholar paper hash
    dblp_id: str = ""  # preferred published-venue DBLP key, e.g. "conf/cvpr/LiWCTT20"
                       # or "journals/jmlr/SmithJ20" for journals; empty for preprint-only papers
    dblp_preprint_id: str = ""  # DBLP corr key for the arXiv version, e.g.
                                # "journals/corr/abs-1910-09700" (derived from arxiv_id)

    # ── repository links ──────────────────────────────────────────────────
    repositories: list["RepositoryLink"] = field(default_factory=list)

    # ── outlet ────────────────────────────────────────────────────────────
    outlet_id: str = ""  # matched publication outlet ID (e.g. "outlet_001")

    # ── OpenAlex enrichment ───────────────────────────────────────────────
    openalex_id: str = ""  # OpenAlex work ID (e.g. "W2741809807")
    cited_by_count: int | None = None  # citation count from OpenAlex
    references: list[str] = field(default_factory=list)  # OpenAlex work IDs of references
    openalex_topics: list[dict] = field(default_factory=list)  # [{"name": str, "score": float}, ...]

    # ── Semantic Scholar enrichment ───────────────────────────────────────
    s2_fields_of_study: list[dict] = field(default_factory=list)
    # [{"category": str, "source": str}, ...]
    # source is "s2-fos-model" (S2 classifier) or "external" (author-declared)
    # categories e.g.: "Computer Science", "Mathematics", "Linguistics"

    # ── GSAP-specific ─────────────────────────────────────────────────────
    selection: str = ""  # "huggingface_selection" or "arxiv_random_selection"

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise to a JSON-compatible dict (repositories as list of dicts)."""
        d = asdict(self)
        # asdict recurses, but RepositoryLink has hidden fields — rebuild cleanly
        d["repositories"] = [r.to_dict() for r in self.repositories]
        return d

    @staticmethod
    def _escape_bib(text: str) -> str:
        """Escape special BibTeX characters."""
        if not text:
            return ""
        text = text.replace("&", r"\&")
        text = text.replace("%", r"\%")
        text = text.replace("_", r"\_")
        return text

    def _make_bib_key(self) -> str:
        """Generate a citekey like 'Wei2019'."""
        if self.authors:
            surname = self.authors[0].split()[-1]
            surname = re.sub(r"[^a-zA-Z]", "", surname)
        else:
            surname = "Unknown"
        return f"{surname}{self.year or ''}"

    def to_bib(self) -> str:
        """Render this record as a BibTeX ``@article{...}`` entry."""
        esc = self._escape_bib
        key = self._make_bib_key()
        author_str = " and ".join(self.authors)

        lines = [
            f"@article{{{key},",
            f"  doc_id = {{{self.doc_id}}},",
            f"  dataset = {{{self.dataset}}},",
            f"  group = {{{self.split}}},",
            f"  title = {{{{{esc(self.title)}}}}},",
            f"  author = {{{esc(author_str)}}},",
            f"  year = {{{self.year or ''}}},",
            f"  venue = {{{esc(self.venue)}}},",
        ]
        if self.abstract:
            lines.append(f"  abstract = {{{esc(self.abstract)}}},")
        if self.article_type:
            lines.append(f"  article_type = {{{self.article_type}}},")
        if self.conference:
            lines.append(f"  conference = {{{self.conference}}},")
        if self.conference_year:
            lines.append(f"  conference_year = {{{self.conference_year}}},")
        if self.doi:
            lines.append(f"  doi = {{{self.doi}}},")
        if self.arxiv_id:
            lines.append(f"  arxiv = {{{self.arxiv_id}}},")
        if self.acl_id:
            lines.append(f"  acl_id = {{{self.acl_id}}},")
        if self.s2_corpus_id:
            lines.append(f"  s2_corpus_id = {{{self.s2_corpus_id}}},")
        if self.dblp_id:
            lines.append(f"  dblp_id = {{{self.dblp_id}}},")
        if self.dblp_preprint_id:
            lines.append(f"  dblp_preprint_id = {{{self.dblp_preprint_id}}},")
        if self.outlet_id:
            lines.append(f"  outlet_id = {{{self.outlet_id}}},")
        if self.selection:
            lines.append(f"  selection = {{{self.selection}}},")

        # Pick the best URL: prefer landing page from first repository
        url = ""
        pdf = ""
        for repo in self.repositories:
            if repo.url_landing_page and not url:
                url = repo.url_landing_page
            if repo.url_pdf and not pdf:
                pdf = repo.url_pdf
        if url:
            lines.append(f"  url = {{{url}}},")
        if pdf:
            lines.append(f"  pdf_url = {{{pdf}}},")

        lines.append("}")
        return "\n".join(lines)


@dataclass
class Corpus:
    sentences: list[Sentence]
    mentions: list[Mention]  # Gold standard mentions
    relation: list[Relation]  # Gold standard relations
    mentions_predicted: list[Mention] = None  # Predicted mentions (for prediction data)
    relations_predicted: list[Relation] = (
        None  # Predicted relations (for prediction data)
    )

    def __post_init__(self):
        """Initialize predicted lists if None."""
        if self.mentions_predicted is None:
            self.mentions_predicted = []
        if self.relations_predicted is None:
            self.relations_predicted = []

    def format_relation(
        self,
        relation_id: int,
        predicted: bool = False,
    ) -> str:
        """Format a relation by index with its sentence context.

        Args:
            relation_id: Index into the relations list.
            predicted: If True, use predicted relations; otherwise gold.

        Returns:
            A formatted string containing the sentence and relation.
        """
        relations = self.relations_predicted if predicted else self.relation
        if relation_id < 0 or relation_id >= len(relations):
            raise IndexError(
                f"relation_id out of range: {relation_id} (size={len(relations)})"
            )
        rel = relations[relation_id]
        sent_text = ""
        for sent in self.sentences:
            if sent.doc_id == rel.document_id and str(sent.idx) == str(rel.sent_idx):
                sent_text = sent.text
                break
        subj_label = rel.subject.label_original or rel.subject.label
        obj_label = rel.object.label_original or rel.object.label
        relation_str = (
            f'[{subj_label}: "{rel.subject.text}"] '
            f"-({rel.label})-> "
            f'[{obj_label}: "{rel.object.text}"]'
        )
        if sent_text:
            return f"{sent_text}\n{relation_str}"
        return relation_str

    def print_relation(
        self,
        relation_id: int,
        predicted: bool = False,
    ) -> None:
        """Print a relation by index with its sentence context."""
        print(self.format_relation(relation_id, predicted=predicted))
