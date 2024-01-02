#!/usr/bin/python
"""
    AWR2Excel.py - Oracle AWR Parser

    Usage:
        python AWR2Excel.py -files <html file name list or mask>

    Example1:
        python AWR2Excel.py -files /files/awrfile.html

    Example2:
        python AWR2Excel.py -files /files/*.html

    Example3:
        python AWR2Excel.py -files '/files/awrfile01.html','/files/awrfile02.html'

    Help:
        python AWR2Excel.py -h

"""

import pandas as pd
from bs4 import BeautifulSoup
from tabulate import tabulate
import glob
import argparse
import os
from io import StringIO
import openpyxl
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from pathlib import Path
from datetime import datetime

# Global variables        
table_size = 10
none_type = type(None)
sql_indexes = ["SQL Id", "SQL Module", "SQL Text"]
summary_section_key = 'Summary'
checks_section_key = 'Checks'

# list of awr sections to parse
awr_sections = {
    0:"This table displays database instance information",
    1:"This table displays host information",
    2:"This table displays snapshot information",
    3:"This table displays load profile",
    4:"This table displays top 10 wait events by total wait time",
    5:"This table displays wait class statistics ordered by total wait time",
    6:"This table displays system load statistics",
    7:"This table displays CPU usage and wait statistics",
    8:"This table displays IO profile",
    9:"This table displays top SQL by elapsed time",
    10:"This table displays top SQL by CPU time",
    11:"This table displays top SQL by user I/O time",
    12:"This table displays top SQL by buffer gets",
    13:"This table displays top SQL by physical reads",
    14:"This table displays top SQL by unoptimized read requests",
    15:"This table displays top SQL by number of executions",
    16:"This table displays top SQL by number of parse calls",
    17:"This table displays top SQL by amount of shared memory used",
    18:"This table displays top SQL by version counts",
    19:"This table displays top SQL by cluster wait time",
    20: "This table displays Foreground Wait Events and their wait statistics",
    21: "This table displays instance efficiency percentages"
}


def get_data(content, filter):
    """
        Find AWR Table Section using the filter
    """
    table = content.find('table', {'summary': filter})
    # Testing if it didn´t find awr section
    if not isinstance(table, none_type):
        ret = pd.read_html(StringIO(str(table)), header=0)
        section_df = ret[0]
    else:
        section_df = None
    return section_df


def str_to_float(str_num):
    tmp_str_num = str_num.replace(" (mins)", "")  # Remove '(mins)'
    tmp_str_num = tmp_str_num.replace(",", "")  # Remove ','
    return float(tmp_str_num)


def extract_awr_data(section_index, soup, report):
    """
        Print the pandas dataframe in the format defined
    """
    # Just for quick tests. Don't forget to comment
    # if section_index not in [21]:
    #     return

    section_key = None
    section_info = awr_sections[section_index]
    df = get_data(soup, section_info)

    print('\tSection {}: {}'.format(section_index, section_info))
    if not isinstance(df, none_type):
        match section_index:
            case 0:
                df_summary = report[summary_section_key]

                db_name = df.at[0, 'DB Name']
                df_summary.loc[len(df_summary)] = {'Parameter': 'dbName', 'Value': db_name}

            case 1:
                df_summary = report[summary_section_key]

                host_name = df.at[0, 'Host Name']
                df_summary.loc[len(df_summary)] = {'Parameter': 'hostName', 'Value': host_name}

            case 2:
                df_summary = report[summary_section_key]

                date_time_str = df.at[0, 'Snap Time']  # Format: 01-Oct-23 13:00:33
                date_time_format = "%d-%b-%y %H:%M:%S"
                begin_date_time = datetime.strptime(date_time_str, date_time_format)

                df_summary.loc[len(df_summary)] = {'Parameter': 'beginDateTime', 'Value': begin_date_time}

                df_summary.loc[len(df_summary)] = {'Parameter': 'beginTime', 'Value': begin_date_time.time()}

                date_time_str = df.at[1, 'Snap Time']  # Format: 01-Oct-23 13:00:33
                end_date_time = datetime.strptime(date_time_str, date_time_format)
                df_summary.loc[len(df_summary)] = {'Parameter': 'endDateTime', 'Value': end_date_time}

                begin_sessions = df.at[0, 'Sessions']
                df_summary.loc[len(df_summary)] = {'Parameter': 'beginSessions', 'Value': begin_sessions}

                end_sessions = df.at[1, 'Sessions']
                df_summary.loc[len(df_summary)] = {'Parameter': 'endSessions', 'Value': end_sessions}

                elapsed_time = str_to_float(df.at[2, 'Snap Time'])
                df_summary.loc[len(df_summary)] = {'Parameter': 'elapsedTime', 'Value': elapsed_time}

                db_time = str_to_float(df.at[3, 'Snap Time'])
                df_summary.loc[len(df_summary)] = {'Parameter': 'dbTime', 'Value': db_time}

            case 3:
                df_summary = report[summary_section_key]

                logical_read = df.at[4, 'Per Second']
                df_summary.loc[len(df_summary)] = {'Parameter': 'logicalRead', 'Value': logical_read}

                physical_read = df.at[6, 'Per Second']
                df_summary.loc[len(df_summary)] = {'Parameter': 'physicalRead', 'Value': physical_read}

                physical_write = df.at[7, 'Per Second']
                df_summary.loc[len(df_summary)] = {'Parameter': 'physicalWrite', 'Value': physical_write}

                parses_sql = df.at[15, 'Per Second']
                df_summary.loc[len(df_summary)] = {'Parameter': 'parsesSQL', 'Value': parses_sql}

                executes_sql = df.at[20, 'Per Second']
                df_summary.loc[len(df_summary)] = {'Parameter': 'executesSQL', 'Value': executes_sql}

            case 6:
                df_summary = report[summary_section_key]

                begin_load_average = df.at[0, 'Load Average Begin']
                df_summary.loc[len(df_summary)] = {'Parameter': 'beginLoadAverage', 'Value': begin_load_average}

                end_load_average = df.at[0, 'Load Average End']
                df_summary.loc[len(df_summary)] = {'Parameter': 'endLoadAverage', 'Value': end_load_average}

                user_cpu = df.at[0, '%User']
                df_summary.loc[len(df_summary)] = {'Parameter': 'userCPU', 'Value': user_cpu}

            case 7:
                df_summary = report[summary_section_key]

                total_cpu = df.at[0, '%Total CPU']
                df_summary.loc[len(df_summary)] = {'Parameter': 'totalCPU', 'Value': total_cpu}

                busy_cpu = df.at[0, '%Busy CPU']
                df_summary.loc[len(df_summary)] = {'Parameter': 'busyCPU', 'Value': busy_cpu}

            case 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17:
                # SQL tables. Move SQLId, User and SQL statement to left colunm for easier comparison
                report[awr_sections[section_index]] = extract_sql_table(section_index, report, df)

            case 18:
                report[awr_sections[section_index]] = extract_sql_table(section_index, report, df)

            case 19:
                report[awr_sections[section_index]] = extract_sql_table(section_index, report, df)

            case 4 | 5 | 8 | 20:
                report[awr_sections[section_index]] = df.iloc[0:table_size].reindex(index=range(0, table_size))

            case 21:
                key_list = []
                value_list = []
                populate_kv_lists(df.columns, key_list, value_list, 0)
                populate_kv_lists(df.columns, key_list, value_list, 2)

                for row in df.itertuples():

                    if row[1]==row[1]:
                        populate_kv_lists(row, key_list, value_list, 1)

                    if row[3]==row[3]:
                        populate_kv_lists(row, key_list, value_list, 3)

                report[awr_sections[section_index]] = pd.DataFrame(data={"Parameter":key_list, "Value":value_list})

            case 22:
                report[awr_sections[section_index]] = df.iloc[0:table_size].reindex(index=range(0, table_size))

            case _:
                print("Section {} not expected".format(section_index))
    # else:
    #     # section_key = f'section_{section_index}'
    #     # section_key = section_index
    #     report[awr_sections[section_index]] = pd.DataFrame(index=range(0, table_size), columns=range(0, 1))

def perform_sanity_checks(report:dict):
    check_list = []
    result_list = []
    evidence_list = []

    for section_index, dataframe  in report.items():
        match section_index:
            case 'This table displays top SQL by version counts':
                sql_ordered_by_version_count(dataframe, check_list, result_list, evidence_list)

            case 'This table displays top 10 wait events by total wait time':
                top_10_foreground_events_by_total_wait_time(dataframe)

            case 'This table displays instance efficiency percentages':
                instance_efficiency_percentages(dataframe)

            case 'This table displays top SQL by number of executions':
                sql_ordered_by_executions(dataframe)

            case 'This table displays load profile':
                load_profile(dataframe)

            case 'This table displays wait class statistics ordered by total wait time':
                wait_classes_by_total_wait_time(dataframe)


def populate_kv_lists(df, key_list, value_list, index):
    key_list.append(df[index].replace(":", "").replace("%", "").strip())
    value_list.append(float(df[index + 1]))


def sql_ordered_by_version_count(dataframe, check_list, result_list, evidence_list):
    # SQL Id version count - Total < 200
    # SQL Id version count - Individual < 100
    versions = dataframe["Version Count"]
    sql_text = dataframe["SQL Text"]

    limit_version_one = 100
    limit_version_all = 200

    version_one_flag = False
    version_all_flag = False

    version_all = 0
    for index, version in versions.items():
        # Check if not a number
        if version == version:
            version_all = version_all + version
            if not version_one_flag and version >= limit_version_one:
                version_one_statement = sql_text[index]
                version_one_flag = True

    if version_all >= limit_version_all:
        version_all_flag = True

    print(f"Version one flag: {version_one_flag} - SQL statement: {version_one_statement}")
    print(f"Version all: {version_all} - Version all flag: {version_all_flag}")


def top_10_foreground_events_by_total_wait_time(dataframe):
    limit_event_waits = 0

    # Use first column as index
    temp_df = dataframe.set_index("Event", inplace=False)

    # Obtain the items
    library_cache_lock_event_waits = at("library cache lock", "Waits", temp_df)
    library_cache_mutex_x_event_waits = at("library cache: mutex X", "Waits", temp_df)
    cursor_mutex_s_event_waits = at("cursor: mutex S", "Waits", temp_df)
    cursor_mutex_x_event_waits = at("cursor: mutex X", "Waits", temp_df)
    cursor_pin_s_wait_on_x_event_waits = at("cursor: pin S wait on X", "Waits", temp_df)
    print("{} - {} - {} - {} - {}".format(library_cache_lock_event_waits, library_cache_mutex_x_event_waits, cursor_mutex_s_event_waits, cursor_mutex_x_event_waits, cursor_pin_s_wait_on_x_event_waits))

    library_cache_locks_event_waits_flag = library_cache_lock_event_waits > limit_event_waits
    library_cache_mutex_x_event_waits_flag = library_cache_mutex_x_event_waits > limit_event_waits
    cursor_mutex_s_event_waits_flag = cursor_mutex_s_event_waits > limit_event_waits
    cursor_mutex_x_event_waits_flag = cursor_mutex_x_event_waits > limit_event_waits
    cursor_pin_s_wait_on_x_event_waits_flag = cursor_pin_s_wait_on_x_event_waits > limit_event_waits
    print("{} - {} - {} - {} - {}".format(library_cache_locks_event_waits_flag, library_cache_mutex_x_event_waits_flag, cursor_mutex_s_event_waits_flag,
                                          cursor_mutex_x_event_waits_flag, cursor_pin_s_wait_on_x_event_waits_flag))

def at(index: str, column: str, dataframe: pd.DataFrame) -> object:
    try:
        item = dataframe.at[index, column]
    except (ValueError, KeyError):
        item = 0
    return item


def sql_ordered_by_executions(dataframe):
    print('sql_ordered_by_executions')
    # print(dataframe)


def instance_efficiency_percentages(dataframe):
    limit_execute_to_parse = 90
    temp_df = dataframe.set_index("Parameter", inplace=False)
    execute_to_parse = at("Execute to Parse", "Value", temp_df)
    execute_to_parse_flag =  not (execute_to_parse > limit_execute_to_parse)
    print(f"{execute_to_parse} - {execute_to_parse_flag}")


def load_profile(dataframe):
    print('load_profile')
    # print(dataframe)

def wait_classes_by_total_wait_time(dataframe):
    limit_concurrency_db_time = 5
    # Use first column as index
    temp_df = dataframe.set_index("Wait Class", inplace=False)
    concurreency_db_time = at("Concurrency", "% DB time", temp_df)
    concurreency_db_time_flag = concurreency_db_time > limit_concurrency_db_time
    print("{} - {}".format(concurreency_db_time, concurreency_db_time_flag))

def extract_sql_table(section_index, report, df):
    section_df = df.iloc[0:table_size]
    sorted_df = section_df[sql_indexes].copy()
    for column in section_df.columns:
        if column not in sorted_df.columns:
            sorted_df[column] = section_df[column]
    return sorted_df.reindex(index=range(0, table_size))


def print_reports(reports):
    # print (reports) sorted by date
    list_keys = sorted(reports.keys())

    wb = Workbook()
    sheet_counter = 0
    for key in list_keys:
        # Create a tab per AWR file
        sheet_name = "AWR2Excel_{}".format(sheet_counter)
        sheet_counter += 1
        ws = wb.create_sheet(sheet_name)
        report = reports[key]

        # Write sections
        for section_key in report:
            section_df = report[section_key]
            ws.append([])

            ws.append([section_key])

            for row in dataframe_to_rows(section_df, index=False, header=True):
                ws.append(row)
                # write a file object along with .xlsx extension
    # convert datetime obj to string
    str_current_datetime = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
    out_filename = str_current_datetime + "_AWR2Excel" + ".xlsx"
    wb.save(out_filename)


def main():
    try:
        # CMD Parameters
        version = '1.0'
        version_description = 'AWR2Excel - Oracle AWR to Excel utility {}'.format(version)

        parser = argparse.ArgumentParser(description=version_description)
        parser.add_argument('-files', help='Comma-delimited list of HTML AWR files', default='')

        # If parse fail will show help
        args = parser.parse_args()

        if args.files == '':
            print('You need to pass the AWR HTML file name.')
            print('Example: AWR2Excel.py -file /path/awrfile.html or AWR2Excel.py -file /path/*.html')
        else:
            filelist = args.files.split(',')

            reports = {}
            for fn in filelist:
                files = glob.glob(fn)
                for file in files:
                    file_stream = None
                    try:
                        file_stream = open(file)
                        print('Processing data from AWR file: {}'.format(file))

                        soup = BeautifulSoup(file_stream, 'lxml')

                        report = {summary_section_key: pd.DataFrame(columns=['Parameter', 'Value'])}

                        # Add the AWR filename to the summary
                        report[summary_section_key].loc[len(report[summary_section_key])] = {'Parameter': 'file',
                                                                             'Value': Path(file).name}

                        # Extract and format the information of a AWR file
                        # for i, info in enumerate(infolist):            
                        # print (i, info)
                        for i in range(0, len(awr_sections)):
                            extract_awr_data(i, soup, report)
                            # if len(sections) == 0 or str(i) in sections:
                            # extractAWRData(i, info, soup, args.fmt, report)

                        # add the report to the list of reports
                        summary_df = report[summary_section_key].copy()
                        summary_df.set_index("Parameter", inplace=True)
                        begin_date_time = at("beginDateTime", "Value", summary_df)

                        # Perform sanity checks of this report
                        perform_sanity_checks(report)

                        # Add the report to the list of reports
                        reports[begin_date_time] = report
                    finally:
                        if file_stream is not None:
                            file_stream.close()


            print_reports(reports)

    finally:
        print('AWR2Excel.py Finished')


if __name__ == '__main__':
    main()
