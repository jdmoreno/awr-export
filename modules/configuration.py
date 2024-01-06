import configparser


def read_config_file():
    config = configparser.ConfigParser()
    config.read('AWR2Excel.ini')
    return config


def read_configuration():
    config = read_config_file()
    limit_execute_to_parse_error = float(config['CHECKS_THRESHOLDS']['limit_execute_to_parse_error'])
    limit_concurrency_db_time_error = float(config['CHECKS_THRESHOLDS']['limit_concurrency_db_time_error'])

    limit_library_cache_lock_event_waits_error = float(config['CHECKS_THRESHOLDS']['limit_library_cache_lock_event_waits_error'])
    limit_library_cache_mutex_x_event_waits_error = float(config['CHECKS_THRESHOLDS']['limit_library_cache_mutex_x_event_waits_error'])
    limit_cursor_mutex_s_event_waits_error = float(config['CHECKS_THRESHOLDS']['limit_cursor_mutex_s_event_waits_error'])
    limit_cursor_mutex_x_event_waits_error = float(config['CHECKS_THRESHOLDS']['limit_cursor_mutex_x_event_waits_error'])
    limit_cursor_pin_s_wait_on_x_event_waits_error = float(config['CHECKS_THRESHOLDS']['limit_cursor_pin_s_wait_on_x_event_waits_error'])

    limit_version_one_error = float(config['CHECKS_THRESHOLDS']['limit_version_one_error'])
    limit_version_all_error = float(config['CHECKS_THRESHOLDS']['limit_version_all_error'])

    limit_exceptions_events_ratio_error = float(config['CHECKS_THRESHOLDS']['limit_exceptions_events_ratio_error'])/100

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


    print(f"\nConfiguration: {thresholds}\n")
    return thresholds
