
map_template = """Write a concise summary of the following content,:
{content}
Summary:
"""

reduce_template = """The following is set of summaries:
{doc_summaries}
BY summarizing the above summaries determine what type of document this is. Start your answer with This document.
Summary:"""