# awr-export
Oracle AWR html export and sanity checks

Based on: https://www.linkedin.com/pulse/easy-way-developers-dbas-analyze-data-from-oracle-awr-alexandre-marti

## Arguments:
| Argument    | Description                            | Mandatory |
|-------------|----------------------------------------|-----------|
| -files, -f  | Comma-delimited list of HTML AWR files | Yes       |
| -config, -c | Path to configuration file (.toml)     | No        |
| -output, -o | Output directory                       | No        |


## Usage:
```commandline
python AWR2Excel.py -files ".\test\in\PRD - 2023-10-02\awr_rmgtibp_1_231002_1100_1130.html"
```

```commandline
python ".\awr-export\AWR2Excel.py" -c AWR2Excel-ppd.toml -o "output" -f ".\PPD\AWR-PPD-PARALLEL-15thJAN\*.html"
```

## Checks
Summary of the checks implemented:

| **Group**                                     | **Condition**                                         | **Warning**                                      | **Error**                                       | **Status**  | **Comment**                                       |
|-----------------------------------------------|-------------------------------------------------------|--------------------------------------------------|-------------------------------------------------|-------------|---------------------------------------------------|
| Error during processing                       | Inserts in exceptions table                           | above 5% of the insert in Events table           | above 5% of the insert in Events table          | Pending     | Working on it but not part of ASD RCA             |
| Foreground Events by Total Wait Time          | Cursor: mutex S                                       | Not in top 10 in wait events ordered by %DB Time | Not in top 5 in wait events ordered by %DB Time | Implemented |                                                   |
| Foreground Events by Total Wait Time          | Cursor: mutex X                                       | Not in top 10 in wait events ordered by %DB Time | Not in top 5 in wait events ordered by %DB Time | Implemented |                                                   |
| Foreground Events by Total Wait Time          | Library cache lock                                    | Not in top 10 in wait events ordered by %DB Time | Not in top 5 in wait events ordered by %DB Time | Implemented |                                                   |
| Instance Efficiency Percentages (Target 100%) | Execute to Parse %                                    | Below 50%                                        | Below 90%                                       | Implemented |                                                   |
| Load Profile                                  | DB Time(s) vs DB CPU(s)                               | 50%                                              | 80%                                             | Pending     | Working on it                                     |
| Load Profile                                  | Parses (SQL)                                          | 50                                               | 100                                             | Pending     | Parses already checked in %DB time on concurrency |
| SQL Id version count                          | Individual versions of SQL statement                  | 20                                               | 50                                              | Implemented |                                                   |
| SQL Id version count                          | Total versions of SQL statements                      | 100                                              | 200                                             | Implemented |                                                   |
| Summary                                       | DB Time vs Elapsed time                               | 10                                               | 18                                              | Pending     | Similar to DB Time(s) vs DB CPU(s)                |
| Top 10 Foreground Events by Total Wait Time   | %DB time on Concurrency Wait Class of Total Wait Time | 5%                                               | 10%                                             | Implemented |                                                   |
| Host CPU                                      | CPU load is not above 80% consistently for 5 min      | 80%                                              |                                                 |             |                                                   |

Details can be found at: https://andotce.royalmailgroup.com/display/EPSP/EPS+Cloud+-+DV+-+80+-+Oracle+Database+Management+System+-+Regression+tests

## Configuration
The thresholds for the checks are configured in the file AWR2Excel.ini
```
# below the threshold
limit_execute_to_parse_error = 40

# Above the threshold
limit_library_cache_lock_event_waits_error = 0
limit_cursor_mutex_s_event_waits_error = 0
limit_cursor_mutex_x_event_waits_error = 0
limit_version_one_error = 50
limit_version_all_error = 200

limit_concurrency_db_time_error = 5
limit_library_cache_mutex_x_event_waits_error = 0
limit_cursor_pin_s_wait_on_x_event_waits_error = 0
limit_exceptions_events_ratio_error = 10

``` 

| **Condition**                                         | **Parameter**                              |
|-------------------------------------------------------|--------------------------------------------|
| Inserts in exceptions table                           | limit_exceptions_events_ratio_error        |
| Cursor: mutex S                                       | limit_cursor_mutex_s_event_waits_error     |
| Cursor: mutex X                                       | limit_cursor_mutex_x_event_waits_error     |
| Library cache lock                                    | limit_library_cache_lock_event_waits_error |
| Execute to Parse %                                    | limit_execute_to_parse_error               |
| DB Time(s) vs DB CPU(s)                               | Pending                                    |
| Parses (SQL)                                          | Pending                                    |
| Individual versions of SQL statement                  | limit_version_one_error                    |
| Total versions of SQL statements                      | limit_version_all_error                    |
| DB Time vs Elapsed time                               | Pending                                    |
| %DB time on Concurrency Wait Class of Total Wait Time | limit_concurrency_db_time_error            |
| CPU load is not above 80% consistently for 5 min      | limit_cpu_error                            |

## Examples
* Example: AWR with versions and concurrency DB Time % below 5%
```
python AWR2Excel.py -files ".\test\in\PRD - 2023-10-02\awr_rmgtibp_1_231002_1100_1130.html"
```
* Example: AWR without versions
```
python AWR2Excel.py -files ".\test\in\PPD - 2023-12-23 - asd -soak\awrrpt_1_160_161.html"
```
* Example: AWR with some problems in the instance efficiency percentages
```
python AWR2Excel.py -files ".\test\in\PRD - 2023-10-02\awr_rmgtibp_1_231002_1500_1505.html"
```
* Example: AWR with concurrency DB Time % above 25%
```
python AWR2Excel.py -files ".\test\in\PRD - 2023-10-02\awr_rmgtibp_1_231002_1200_1230.html"
```
* Example: AWR with writes in exception log
```
python AWR2Excel.py -files ".\test\in\PPD - 2023-12-23 - asd -soak\awrrpt_1_187_188.html"
```
* Example: AWRs production 2023-10-02 rollback
```
python AWR2Excel.py -files ".\test\in\PRD - 2023-10-02\*.html"
```
* Example: AWRs preproduction 2023-12-23 ASD soak
```
python AWR2Excel.py -files ".\test\in\PPD - 2023-12-23 - asd -soak\*.html"
```
* Example: AWRs preproduction Jan 6TH release soak 2023-12-21
```
python AWR2Excel.py -files ".\test\in\PPD - 2023-12-21 - 6th - soak\*.html"
```
* Help:
```
python AWRp.py -h
```
