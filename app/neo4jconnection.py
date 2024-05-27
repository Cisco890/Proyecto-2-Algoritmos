from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self._driver.close()

    def query(self, query, parameters=None, **kwargs):
        with self._driver.session() as session:
            return list(session.run(query, parameters, **kwargs))
