def test_query_module_imports():
    from src import queries
    assert callable(queries.kpis)

