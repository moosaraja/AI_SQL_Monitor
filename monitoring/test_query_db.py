from top_cpu_queries import get_top_cpu_queries

queries = get_top_cpu_queries(limit=10)

for query in queries:
    print("------------------------")
    print("SQL text DBID:", query.get("sql_text_dbid"))
    print("Plan DBID:", query.get("plan_dbid"))
    print("Plan database:", query.get("plan_database"))
    print("Resolved database:", query.get("database_name"))
    print("CPU:", query.get("total_cpu_ms"))
    print("SQL:", str(query.get("sql_text"))[:100])