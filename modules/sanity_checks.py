import pandas
import pandas as pd
from modules.common import at
from modules.constants import summary_section_key

def perform_sanity_checks(report: dict, checks_section_key: str, thresholds: dict):
    check_results = {}

    for section_index, dataframe in report.items():
        match section_index:
            case 'This table displays top SQL by version counts':
                sql_ordered_by_version_count(dataframe, thresholds, check_results)

            case 'This table displays top SQL by number of executions':
                sql_ordered_by_executions(dataframe, thresholds, check_results)

            case 'This table displays top SQL by CPU time':
                sql_ordered_by_cpu_time(dataframe, thresholds, check_results)

            case 'This table displays top 10 wait events by total wait time':
                top_10_foreground_events_by_total_wait_time(dataframe, thresholds, check_results)

            case 'This table displays instance efficiency percentages':
                instance_efficiency_percentages(dataframe, thresholds, check_results)

            case 'This table displays load profile':
                load_profile(dataframe, thresholds, check_results)

            case 'This table displays wait class statistics ordered by total wait time':
                wait_classes_by_total_wait_time(dataframe, thresholds, check_results)

            case 'This table displays wait class statistics ordered by total wait time':
                wait_classes_by_total_wait_time(dataframe, thresholds, check_results)

    checks_list = []
    results_list = []
    evidences_list = []
    # print(check_results)
    for key, value in check_results.items():
        result = value["result"]
        evidence = value["evidence"]

        checks_list.append(key)
        results_list.append(result)
        evidences_list.append(evidence)

    report[checks_section_key] = pd.DataFrame(
        data={"Check": checks_list, "Result": results_list, "Evidence": evidences_list})


def wait_classes_by_total_wait_time(dataframe, thresholds, check_results):
    limit_concurrency_db_time = thresholds["limit_concurrency_db_time_error"]

    # Use first column as index
    temp_df = dataframe.set_index("Wait Class", inplace=False)
    concurrency_db_time = at("Concurrency", "% DB time", temp_df)
    if concurrency_db_time is None:
        concurrency_db_time = 0

    concurrency_db_time_flag = concurrency_db_time > limit_concurrency_db_time

    # Print check results
    # print(f"concurreency_db_time_flag: {concurrency_db_time_flag} - evidence: {concurrency_db_time}")

    # Update checklist
    check_results['concurrency_db_time'] = {'result': concurrency_db_time_flag, 'evidence': concurrency_db_time}


def load_profile(dataframe, thresholds, check_results):
    # print('load_profile')
    # print(dataframe)
    return


def instance_efficiency_percentages(dataframe, thresholds, check_results):
    limit_execute_to_parse = thresholds["limit_execute_to_parse_error"]

    temp_df = dataframe.set_index("Parameter", inplace=False)
    execute_to_parse = at("Execute to Parse", "Value", temp_df)
    if execute_to_parse is None:
        execute_to_parse = 0

    execute_to_parse_flag = not (execute_to_parse > limit_execute_to_parse)

    # Print check results
    # print(f"execute_to_parse_flag: {execute_to_parse_flag} - evidence: {execute_to_parse}")

    # Update checklist
    check_results['execute_to_parse'] = {'result': execute_to_parse_flag, 'evidence': execute_to_parse}


def sql_ordered_by_version_count(dataframe, thresholds, check_results):
    limit_version_one = thresholds["limit_version_one_error"]
    limit_version_all = thresholds["limit_version_all_error"]

    version_one_flag = False
    version_all_flag = False

    # version_one_statement = ""
    version_one = 0
    version_all = 0

    version_one_details = {}
    # print(f"dataframe \n{dataframe} \n keys {dataframe.keys()} \n {dataframe.columns()}")

    if "Version Count" in dataframe.columns:
        versions = dataframe["Version Count"]
        sql_id = dataframe["SQL Id"]
        sql_text = dataframe["SQL Text"]

        for index, version in versions.items():
            # Check if not a number
            if version == version:
                version_all = version_all + version
                if not version_one_flag and version >= limit_version_one:
                    version_one_details[sql_id[index]] = sql_text[index]
                    # version_one_statement = sql_text[index]
                    # version_one_statement = sql_text[index]
                    if not version_one_flag:
                        version_one = version
                        version_one_flag = True

    if version_all >= limit_version_all:
        version_all_flag = True

    # Print check results
    # print(f"version_one_flag: {version_one_flag} - evidence: {version_one_flag}")
    # print(f"version_one_flag: {version_all_flag} - evidence: {version_all}")

    # Update checklist
    check_results['version_one'] = {'result': version_one_flag, 'evidence': version_one, 'comment': version_one_details}
    check_results['version_all'] = {'result': version_all_flag, 'evidence': version_all}


def top_10_foreground_events_by_total_wait_time(dataframe, thresholds, check_results):
    # Use first column as index
    temp_df = dataframe.set_index("Event", inplace=False)

    # Obtain the items
    library_cache_lock_event_waits = at("library cache lock", "Waits", temp_df)
    if library_cache_lock_event_waits is None:
        library_cache_lock_event_waits = 0

    library_cache_locks_event_waits_flag = library_cache_lock_event_waits > thresholds[
        "limit_library_cache_lock_event_waits_error"]

    library_cache_mutex_x_event_waits = at("library cache: mutex X", "Waits", temp_df)
    if library_cache_mutex_x_event_waits is None:
        library_cache_mutex_x_event_waits = 0

    library_cache_mutex_x_event_waits_flag = library_cache_mutex_x_event_waits > thresholds[
        "limit_library_cache_mutex_x_event_waits_error"]

    cursor_mutex_s_event_waits = at("cursor: mutex S", "Waits", temp_df)
    if cursor_mutex_s_event_waits is None:
        cursor_mutex_s_event_waits = 0

    cursor_mutex_s_event_waits_flag = cursor_mutex_s_event_waits > thresholds["limit_cursor_mutex_s_event_waits_error"]

    cursor_mutex_x_event_waits = at("cursor: mutex X", "Waits", temp_df)
    if cursor_mutex_x_event_waits is None:
        cursor_mutex_x_event_waits = 0

    cursor_mutex_x_event_waits_flag = cursor_mutex_x_event_waits > thresholds["limit_cursor_mutex_x_event_waits_error"]

    cursor_pin_s_wait_on_x_event_waits = at("cursor: pin S wait on X", "Waits", temp_df)
    if cursor_pin_s_wait_on_x_event_waits is None:
        cursor_pin_s_wait_on_x_event_waits = 0

    cursor_pin_s_wait_on_x_event_waits_flag = cursor_pin_s_wait_on_x_event_waits > thresholds[
        "limit_cursor_pin_s_wait_on_x_event_waits_error"]

    # Print check results
    # print(f"library_cache_locks_event_waits_flag: {library_cache_locks_event_waits_flag} - evidence: {library_cache_lock_event_waits}")
    # print(f"library_cache_mutex_x_event_waits_flag: {library_cache_mutex_x_event_waits_flag} - evidence: {library_cache_mutex_x_event_waits}")
    # print(f"cursor_mutex_s_event_waits_flag: {cursor_mutex_s_event_waits_flag} - evidence: {cursor_mutex_s_event_waits}")
    # print(f"cursor_mutex_x_event_waits_flag: {cursor_mutex_x_event_waits_flag} - evidence: {cursor_mutex_x_event_waits}")
    # print(f"cursor_pin_s_wait_on_x_event_waits_flag: {cursor_pin_s_wait_on_x_event_waits_flag} - evidence: {cursor_pin_s_wait_on_x_event_waits}")

    # Update checklist
    check_results['library_cache_lock_event_waits'] = {'result': library_cache_locks_event_waits_flag,
                                                       'evidence': library_cache_lock_event_waits}
    check_results['library_cache_mutex_x_event_waits'] = {'result': library_cache_mutex_x_event_waits_flag,
                                                          'evidence': library_cache_mutex_x_event_waits}
    check_results['cursor_mutex_s_event_waits'] = {'result': cursor_mutex_s_event_waits_flag,
                                                   'evidence': cursor_mutex_s_event_waits}
    check_results['cursor_mutex_x_event_waits'] = {'result': cursor_mutex_x_event_waits_flag,
                                                   'evidence': cursor_mutex_x_event_waits}
    check_results['cursor_pin_s_wait_on_x_event_waits'] = {'result': cursor_pin_s_wait_on_x_event_waits_flag,
                                                           'evidence': cursor_pin_s_wait_on_x_event_waits}


def sql_ordered_by_executions(dataframe, thresholds, check_results):
    # print('sql_ordered_by_executions')
    # print(dataframe)
    return


def sql_ordered_by_cpu_time(dataframe, thresholds, check_results):
    # print('sql_ordered_by_cpu_time')
    # print(dataframe)
    temp_df = dataframe.set_index("SQL Id", inplace=False)

    events_inserts_executions = at("7wcmwtk6ay1c9", "Executions", temp_df)
    if events_inserts_executions is None:
        events_inserts_executions = 0
    events_inserts_executions = float(events_inserts_executions)

    exceptions_inserts_executions = at("47byg9a0mdfmx", "Executions", temp_df)
    if exceptions_inserts_executions is None:
        exceptions_inserts_executions = 0
    exceptions_inserts_executions = float(exceptions_inserts_executions)

    if events_inserts_executions > 0:
        ratio_exceptions_events = round(exceptions_inserts_executions / events_inserts_executions, 2)
    else:
        if exceptions_inserts_executions > 0:
            ratio_exceptions_events = 1
        else:
            ratio_exceptions_events = 0
    ratio_exceptions_events_flag = ratio_exceptions_events > thresholds[
        "limit_exceptions_events_ratio_error"]

    # print(f"Events executions {events_inserts_executions}")
    # print(f"Exceptions executions {exceptions_inserts_executions}")
    # print(f"ratio_exceptions_events: {ratio_exceptions_events}")
    # print(f"ratio_exceptions_events_flag: {ratio_exceptions_events_flag}")

    check_results['ratio_exceptions_events'] = {'result': ratio_exceptions_events_flag,
                                                'evidence': exceptions_inserts_executions}

    return


# def at(index: str, column: str, dataframe: pd.DataFrame) -> object:
#     try:
#         item = dataframe.at[index, column]
#     except (KeyError, ValueError):
#         item = 0
#     return item
