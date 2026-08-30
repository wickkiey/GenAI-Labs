import importlib
import json

registry_module = importlib.import_module("03_tools.tools.registry")
calculator_module = importlib.import_module("03_tools.tools.calculator")
datetime_module = importlib.import_module("03_tools.tools.datetime_tool")
filesystem_module = importlib.import_module("03_tools.tools.filesystem")
sqlite_module = importlib.import_module("03_tools.tools.sqlite_tool")
search_module = importlib.import_module("03_tools.tools.search")


def test_calculator_evaluates_arithmetic() -> None:
    assert calculator_module.calculator("2+2") == "4"
    assert calculator_module.calculator("15 * 2400 / 100") == "360.0"


def test_calculator_rejects_code() -> None:
    result = calculator_module.calculator("__import__('os').system('echo unsafe')")
    assert result.startswith("Error:")


def test_get_current_time_rejects_unknown_timezone() -> None:
    assert datetime_module.get_current_time("Not/AZone").startswith("Error:")


def test_get_current_time_returns_value_for_utc() -> None:
    assert datetime_module.get_current_time("UTC")


def test_filesystem_lists_seed_files() -> None:
    names = filesystem_module.list_files()
    assert "notes.txt" in names


def test_filesystem_reads_seed_file() -> None:
    content = filesystem_module.read_file("notes.txt")
    assert "sandbox" in content


def test_filesystem_rejects_path_traversal() -> None:
    result = filesystem_module.read_file("../../.env")
    assert result.startswith("Error:")


def test_filesystem_rejects_missing_file() -> None:
    result = filesystem_module.read_file("does_not_exist.txt")
    assert result.startswith("Error:")


def test_sqlite_list_tables_contains_seed_tables() -> None:
    tables = sqlite_module.list_tables()
    assert "employees" in tables
    assert "departments" in tables
    assert "sales" in tables


def test_sqlite_describe_table_reports_columns() -> None:
    description = sqlite_module.describe_table("employees")
    assert "name" in description


def test_sqlite_describe_table_rejects_invalid_name() -> None:
    assert sqlite_module.describe_table("employees; DROP TABLE employees").startswith("Error:")


def test_sqlite_query_database_runs_select() -> None:
    result = json.loads(sqlite_module.query_database("SELECT COUNT(*) FROM employees"))
    assert result["rows"][0][0] == 5


def test_sqlite_query_database_rejects_write_statement() -> None:
    result = sqlite_module.query_database("DROP TABLE employees")
    assert result.startswith("Error:")
    assert "employees" in sqlite_module.list_tables()


def test_sqlite_query_database_rejects_stacked_statements() -> None:
    result = sqlite_module.query_database("SELECT 1; DROP TABLE employees")
    assert result.startswith("Error:")
    assert "employees" in sqlite_module.list_tables()


def test_search_documents_finds_keyword() -> None:
    matches = search_module.search_documents("vector")
    assert "vectors.txt" in matches


def test_search_documents_no_match() -> None:
    assert search_module.search_documents("zzz-not-present") == "(no matches)"


def test_tool_registry_contains_all_tools() -> None:
    # importing the individual modules above populates the shared registry
    for name in [
        "calculator",
        "get_current_time",
        "list_files",
        "read_file",
        "search_documents",
        "list_tables",
        "describe_table",
        "query_database",
    ]:
        assert name in registry_module.TOOL_REGISTRY
