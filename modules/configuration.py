import configparser
import json

# from typing import Dict

thresholds = None
track_sql_ids = None
track_sql_modules = None


def read_config_file():
    config = configparser.ConfigParser()
    config.read('AWR2Excel.ini')
    return config


def read_configuration():
    global thresholds, track_sql_ids, track_sql_modules

    config = read_config_file()

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
    track_sql_ids = config_read_list(config["TRACK_SQLID"]['track_sqL_ids'])

    # Read SQL Ids to track
    track_sql_modules = config_read_list(config["TRACK_SQLMODULE"]['track_sql_modules'])

    # print_configuration(thresholds, track_sql_ids, track_sql_modules)

    return


def print_configuration():
    global thresholds, track_sql_ids, track_sql_modules
    print(f"\nConfiguration:")
    print(f"\tthresholds:        {thresholds}")
    print(f"\ttrack_sqL_ids:     {track_sql_ids} - {type(track_sql_ids)}")
    print(f"\ttrack_sql_modules: {track_sql_modules} - {type(track_sql_modules)}")


def config_read_list(value: str) -> list:
    ret_value = []
    if value.startswith("[") and value.endswith("]"):
        # handle special case of k=[1,2,3] or other json-like syntax
        try:
            ret_value = json.loads(value)
        except Exception:
            # for backward compatibility with legacy format (eg. where config value is [a, b, c] instead of proper json ["a", "b", "c"]
            ret_value = [elem.strip() for elem in value[1:-1].split(",")]
    return ret_value
