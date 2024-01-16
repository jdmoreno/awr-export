# To unify the number of row written to the report for all tables in AWR
table_size = 10

awr_sections = {
    0: "This table displays database instance information",
    1: "This table displays host information",
    2: "This table displays snapshot information",
    3: "This table displays load profile",
    4: "This table displays top 10 wait events by total wait time",
    5: "This table displays wait class statistics ordered by total wait time",
    6: "This table displays system load statistics",
    7: "This table displays CPU usage and wait statistics",
    8: "This table displays IO profile",
    9: "This table displays top SQL by elapsed time",
    10: "This table displays top SQL by CPU time",
    11: "This table displays top SQL by user I/O time",
    12: "This table displays top SQL by buffer gets",
    13: "This table displays top SQL by physical reads",
    14: "This table displays top SQL by unoptimized read requests",
    15: "This table displays top SQL by number of executions",
    16: "This table displays top SQL by number of parse calls",
    17: "This table displays top SQL by amount of shared memory used",
    18: "This table displays top SQL by version counts",
    19: "This table displays top SQL by cluster wait time",
    20: "This table displays Foreground Wait Events and their wait statistics",
    21: "This table displays instance efficiency percentages"
}

# To index SQL tables
sql_indexes = ["SQL Id", "SQL Module", "SQL Text"]

# To create to additional sections in the report
summary_section_key = 'Summary'
checks_section_key = 'Checks'
tracked_sql_ids_section_key = "tracked_sql_ids"
tracked_sql_modules_section_key = "tracked_sql_modules"
aggregations_section_key = "aggregations"
