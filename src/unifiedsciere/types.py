from dataclasses import dataclass


@dataclass
class Sentence:
    text: str
    doc_id: str
    idx: int
    split: str
    n_mentions: int = 0

    @property
    def id(self):
        return f"{self.doc_id} {self.idx}"


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
    annotator: str = "gold"  # "gold" or model name (e.g., "gsap", "scier", "scinlp")
    dataset: str = ""  # Dataset name (e.g., "gsap", "scier", "scinlp")
    label_original: str = ""  # Original label before unification mapping


@dataclass
class Relation:
    subject: Mention
    label: str
    object: Mention
    score: float = 1.0  # Confidence score (1.0 for gold annotations)
    annotator: str = "gold"  # "gold" or model name (e.g., "gsap", "scier", "scinlp")
    dataset: str = ""  # Dataset name (e.g., "gsap", "scier", "scinlp")

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
