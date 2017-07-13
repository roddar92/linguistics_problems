# Bookshelf

This application is based on ontology schema and productions.

> Ontology is the description of the world based on entities, attributes and relationships between entities. Ontology is often presented as ordered structure of concepts of an specific shpere.

> Attribute is property of an entity.

> Production - rules stored in knowledge base. While system parses user query it searchers the most relevant rule for the answer generation. 

> In general case rules can be persented as context-free grammar. In our case productions are patterns for synonyms and sub-categories.

## How would it work?

1. User types the query
2. System tokenize this query and removes stopwords
3. For any word of the query:
   * searcher find matches in all fields of the book
   * otherwise, system calls the knowledge base and find answers by the query context
   
## How to lmprove the current algorithm?

1. Add new books in the JSON file
2. Write rules either for herous if book is feature or for the sub-category