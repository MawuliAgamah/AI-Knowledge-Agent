map_template = """The following is a part of a larger document. Write a concise summary of the following content,:
{content}
Summary:
"""

reduce_template = """The following is set of summaries:
{doc_summaries}
BY summarizing the above summaries determine what type of document this is. Start your answer with This document.
Summary:"""


map_metadata_template = """Write a concise summary of the following content,:
{content}
Summary:
"""

reduce_metadata_template = """The following is set of summaries:
{doc_summaries}
BY summarizing the above summaries determine what type of document this is. Start your answer with This document.
Summary:"""