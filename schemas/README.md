Proposed additional keywords
============================

The schemas defined here follow jsonschema as closely as possbile,
introducing new keywords as needed.

systemAlias
-----------

For implementation. Allows properties to be stored as different
keywords.  The property listed in the properties section is what the
user will refer to it, and the systemAlias value is what it will be
stored in the database as.

systemProperties
---------------

The property keys listed under systemProperties are properties that
the submitter is not allowed to update.

parentType
---------------

The type of object that the parent relationship points to.
