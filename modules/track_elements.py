tracked_sql_ids = {}
tracked_sql_modules = {}


def add_sql_id(sql_id: str, executions: int, sql_statement: str):
    # global tracked_sql_ids
    tracked_sql_ids[sql_id] = [executions, sql_statement]


def add_sql_module(sql_module: str, sql_id: str, executions: int, sql_statement: str):
    # global tracked_sql_ids
    tracked_sql_modules[sql_id] = [executions, sql_statement, sql_module]


def get_tracked_sql_ids() -> dict:
    return tracked_sql_ids


def get_tracked_sql_modules() -> dict:
    return tracked_sql_modules
