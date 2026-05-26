prompt = """You are generating sentence-level annotations for ML-related information extraction in full documents.

Input:
- Context: a list of tokenized sentences from the document.
- Sentence: one tokenized sentence from the Context.

Task:
Extract only machine-learning-related entities from the Sentence and annotate strict sentence-level relations between them.

If the Sentence contains no machine-learning-related entities, return empty lists:

entities = []

relations = []

Entity annotation:
Return a list named entities.

Each entity must be represented as:

(tuple[list[str], int])

where:
- list[str] is the exact token span from the Sentence.
- int is the entity type:
  - 0 = concept
  - 1 = artifact

Definitions:
- concept: an abstract ML-related idea, process, property, task, method, or activity.
- artifact: a concrete or named ML-related object, system, tool, model, dataset, benchmark, software, hardware, or other produced/used item.

Entity rules:
- Extract entities only from the Sentence, not from the Context.
- Use the Context only to resolve coreference, abbreviations, and local meaning.
- Do not infer ML relevance from general words alone unless the Sentence or Context clearly makes them ML-related.
- Ignore non-ML entities, even if they are technical, scientific, environmental, organizational, or computational.
- If the full Context contains no ML-related content, return empty lists.
- If the Context contains ML-related content but the Sentence does not, return empty lists.

Relation annotation:
Return a list named relations.

Each relation must be represented as:

tuple[tuple[list[str], int], tuple[list[str], int], int]

where:
- the first tuple is the subject entity.
- the second tuple is the object entity.
- the final integer is the relation type:
  - 0 = direct relation
  - 1 = indirect relation
  - 2 = coreference

Relation rules:
- Only create relations between entities listed in entities.
- Use 0 only when the Sentence explicitly states a direct semantic relation between the two entities.
- Use 1 only when the relation is clearly implied by the Sentence but not directly stated.
- Use 2 when two entity spans refer to the same thing.
- Do not add weak, speculative, or document-level relations unless they are supported by the Sentence.
- Do not create relations to entities that appear only in the Context.
- Do not return text labels such as "concept", "artifact", "direct", "indirect", or "coreference".
- Do not include explanations.

Output format:
Return only valid Python-style data structures:

entities = [
    ...
]

relations = [
    ...
]"""
