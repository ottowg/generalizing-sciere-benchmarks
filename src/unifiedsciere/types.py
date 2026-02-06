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


@dataclass
class Relation:
    subject: Mention
    label: str
    object: Mention

    @property
    def signature(self):
        return self.subject.label, self.label, self.object.label

    @property
    def split(self):
        return self.subject.split

    @property
    def document_id(self):
        return self.subject.document_id


@dataclass
class Corpus:
    sentences: list[Sentence]
    mentions: list[Mention]
    relation: list[Relation]
