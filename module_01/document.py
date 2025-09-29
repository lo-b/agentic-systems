from uuid import uuid4

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

# INFO: data + metadata can be stored using the `Document` class
d = Document(
    id=str(uuid4()),  # an identifier for a document
    page_content="Hello agentic world!",  # string text of the document
    metadata={
        "title": "greeting",
        "label": "foo",
        "tag": "bar",
    },  # dictionary of metadata
)


# TODO: Load the 'some_file.md' markdown file. Create a runnable that adds
# inputs from the A and B title headers and returns the result
# INFO:
#   1. Use the unstructured markdown loader; grab title categories with depth 1;
#   2. Remember that a runnable can only have a single (e.g. a dict) input
#   3. Metadata of a document will be a dict with varying keys,
#      accessing a non-existent key will raise (thrown) a 'KeyError'.
def _f(a, b) -> int:
    return int(a) * int(b)


def f(d) -> int:
    return _f(d["a"], d["b"])


def file_runnable(path: str) -> int:
    md_loader = UnstructuredMarkdownLoader(file_path=path, mode="elements")
    docs = md_loader.load()

    # document ids that are subtitles
    subtitle_ids = []
    for doc in docs:
        has_title_category = doc.metadata["category"] == "Title"
        is_subtitle = has_title_category and doc.metadata["category_depth"] == 1
        if has_title_category and is_subtitle:
            subtitle_ids.append(doc.metadata["element_id"])

    # inputs that have subtitles as parent
    inputs = []
    for doc in docs:
        k = "parent_id"
        has_key = k in doc.metadata
        if has_key and doc.metadata[k] in subtitle_ids:
            inputs.append(doc.page_content)

    r: RunnableLambda[dict[str, int], int] = RunnableLambda(f)
    return r.invoke({"a": inputs[0], "b": inputs[1]})
