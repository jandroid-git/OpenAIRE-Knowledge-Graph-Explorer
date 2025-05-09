local neo4j Zugangsdaten Jan:
KG_name: openAIRE_KG_Projects
password: als GithUb secrete

show whole KG:
MATCH (p:Project)-[:FUNDED_BY]->(f:Funder),
      (p)-[:LOCATED_IN]->(c:Country)
RETURN p, f, c LIMIT SETLIMIT

show projects with country realtionship:
MATCH (p:Project)-[:LOCATED_IN]->(c:Country)
RETURN p, c LIMIT SETLIMIT

show projects with funders realtionship:
MATCH (p:Project)-[:FUNDED_BY]->(f:Funder)
RETURN p, f LIMIT SETLIMIT

show all projects:
MATCH (p:Project) RETURN p LIMIT SETLIMIT
