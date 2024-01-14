# import configparser
import tomllib
import json
import logging

# from typing import Dict

config = None
thresholds = None
track_sql_ids = None
track_sql_modules = None


def read_config_file(file_path: str):
    with open(file_path, mode="rb") as file:
        local_config = tomllib.load(file)
    logging.debug(f"config: {local_config}")
    return local_config


def read_configuration(file_path: str):
    global thresholds, track_sql_ids, track_sql_modules, config

    config = read_config_file(file_path)

    # Read thresholds
    limit_execute_to_parse_error = float(config['CHECKS_THRESHOLDS']['limit_execute_to_parse_error'])
    limit_concurrency_db_time_error = float(config['CHECKS_THRESHOLDS']['limit_concurrency_db_time_error'])

    limit_library_cache_lock_event_waits_error = float(
        config['CHECKS_THRESHOLDS']['limit_library_cache_lock_event_waits_error'])
    limit_library_cache_mutex_x_event_waits_error = float(
        config['CHECKS_THRESHOLDS']['limit_library_cache_mutex_x_event_waits_error'])
    limit_cursor_mutex_s_event_waits_error = float(
        config['CHECKS_THRESHOLDS']['limit_cursor_mutex_s_event_waits_error'])
    limit_cursor_mutex_x_event_waits_error = float(
        config['CHECKS_THRESHOLDS']['limit_cursor_mutex_x_event_waits_error'])
    limit_cursor_pin_s_wait_on_x_event_waits_error = float(
        config['CHECKS_THRESHOLDS']['limit_cursor_pin_s_wait_on_x_event_waits_error'])

    limit_version_one_error = float(config['CHECKS_THRESHOLDS']['limit_version_one_error'])
    limit_version_all_error = float(config['CHECKS_THRESHOLDS']['limit_version_all_error'])

    limit_exceptions_events_ratio_error = float(
        config['CHECKS_THRESHOLDS']['limit_exceptions_events_ratio_error']) / 100

    thresholds = {"limit_execute_to_parse_error": limit_execute_to_parse_error,
                  "limit_concurrency_db_time_error": limit_concurrency_db_time_error,
                  "limit_library_cache_lock_event_waits_error": limit_library_cache_lock_event_waits_error,
                  "limit_library_cache_mutex_x_event_waits_error": limit_library_cache_mutex_x_event_waits_error,
                  "limit_cursor_mutex_s_event_waits_error": limit_cursor_mutex_s_event_waits_error,
                  "limit_cursor_mutex_x_event_waits_error": limit_cursor_mutex_x_event_waits_error,
                  "limit_cursor_pin_s_wait_on_x_event_waits_error": limit_cursor_pin_s_wait_on_x_event_waits_error,

                  "limit_version_one_error": limit_version_one_error,
                  "limit_version_all_error": limit_version_all_error,

                  "limit_exceptions_events_ratio_error": limit_exceptions_events_ratio_error
                  }

    # Read SQL Ids to track
    tracker = config["TRACKER"]
    logging.debug(f"tracker: {tracker}")

    # Store sql ids to track
    tracker_element = tracker["track_sql_ids"]
    logging.debug(f"tracker_element: {tracker_element}")
    track_sql_ids = []

    for value in tracker_element.values():
        track_sql_ids.extend(value)

    logging.debug(f"track_sql_ids: {track_sql_ids}")

    # Store sql modules to track
    tracker_element = tracker["track_sql_modules"]
    logging.debug(f"tracker_element: {tracker_element}")
    track_sql_modules = []

    for value in tracker_element.values():
        track_sql_modules.extend(value)

    logging.debug(f"track_sql_modules: {track_sql_modules}")
    return


def print_configuration():
    global thresholds, track_sql_ids, track_sql_modules
    print(f"\nConfiguration:")
    print(f"\tthresholds:        {thresholds}")
    print(f"\ttrack_sqL_ids:     {track_sql_ids} - {type(track_sql_ids)}")
    print(f"\ttrack_sql_modules: {track_sql_modules} - {type(track_sql_modules)}")


# def config_read_list(value: str) -> list:
#     ret_value = []
#     if value.startswith("[") and value.endswith("]"):
#         # handle special case of k=[1,2,3] or other json-like syntax
#         try:
#             ret_value = json.loads(value)
#         except Exception:
#             # for backward compatibility with legacy format (eg. where config value is [a, b, c] instead of proper json ["a", "b", "c"]
#             ret_value = [elem.strip() for elem in value[1:-1].split(",")]
#     return ret_value
