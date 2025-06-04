local neo4j Zugangsdaten Jan:
KG_name: openAIRE_KG_Projects
password: own password


Zeigt ein Projekt, seine zugehörigen Publikationen, Funder und ggf. Länder:

MATCH (p:Project)-[r]-(x)
WHERE p.title CONTAINS "climate" // oder ein konkreter Titelteil
RETURN p, r, x
LIMIT 1


Ein Funder, alle zugehörigen Projekte und Publikationen

MATCH (f:Funder {name: "European Commission"})<-[:FUNDED_BY]-(p:Project)
OPTIONAL MATCH (p)-[:HAS_PUBLICATION]->(pub:Publication)
RETURN f, p, pub
LIMIT 100


Zeigt ein vollständiges Mini-Ökosystem:

MATCH (p:Project)-[:FUNDED_BY]->(f:Funder),
      (p)-[:LOCATED_IN]->(c:Country),
      (p)-[:HAS_PUBLICATION]->(pub:Publication)
WHERE p.startDate STARTS WITH "2019"
RETURN p, f, c, pub
LIMIT 100


Projekte nach Zeit und Land clustern

MATCH (p:Project)-[:LOCATED_IN]->(c:Country)
WHERE p.startDate >= "2020-01-01"
RETURN c.jurisdiction AS country, count(p) AS projects
ORDER BY projects DESC
LIMIT 10


Verbindungen zwischen Fundern über gemeinsame Publikationen

MATCH (f1:Funder)<-[:FUNDED_BY]-(p1:Project)-[:HAS_PUBLICATION]->(pub:Publication)<-[:HAS_PUBLICATION]-(p2:Project)-[:FUNDED_BY]->(f2:Funder)
WHERE f1 <> f2
RETURN DISTINCT f1, f2, pub
LIMIT 50


random netz

MATCH (p:Project)-[r]-(x)
WITH p, r, x
ORDER BY rand()
RETURN p, r, x
LIMIT 100
