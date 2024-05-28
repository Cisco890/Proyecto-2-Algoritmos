from neo4jconnection import Neo4jConnection

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4jq"
    password = "your_password" 
    conn = Neo4jConnection(uri, user, password)
    
    try:
        result = conn.query("MATCH (n) RETURN n LIMIT 1")
        print("Connection successful. Result:", result)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        conn.close()
