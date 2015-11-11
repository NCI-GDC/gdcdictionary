Glossary
========

The glossary directory is proposed to contain instances of the
`term.yaml` schema; i.e., all the GDC dictionary representations of
terms used elsewhere in the GDC dictionary system.

YAML is preferred for readability, but either YAML or JSON files
should be acceptable. If a YAML + JSON pair of files exists in the
same path, and have the same basename, then the data they represent
should be equivalent.

Ultimately, we imagine all the file representations here and their
synonym relationships, as specified in the instances, are best stored
as term node and edge instances in the graph.

For humans looking at directories, let's use the following file naming
convention:

`term_with_spaces_replaced_by_underscores_<Abbreviated UID of term>.[yaml|json]`

The `term` part of the filename should match the value of the "term"
field, and the `<UID>` part should match the value of the `id` field
in the file.




