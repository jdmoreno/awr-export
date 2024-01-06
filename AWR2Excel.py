import pandas as pd
from bs4 import BeautifulSoup
import glob
import argparse
from io import StringIO
# from openpyxl import Workbook
# from openpyxl.utils.dataframe import dataframe_to_rows
from pathlib import Path
from datetime import datetime
# import configparser
import modules.configuration as configuration
import modules.sanity_checks as sanity_checks
import modules.excel_tabs as excel_tabs

# Global variables
table_size = 10
none_type = type(None)
sql_indexes = ["SQL Id", "SQL Module", "SQL Text"]
summary_section_key = 'Summary'
checks_section_key = 'Checks'

# list of awr sections to parse
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


def get_data(content, section_filter):
    """
        Find AWR Table Section using the filter
    """
    table = content.find('table', {'summary': section_filter})
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

    section_info = awr_sections[section_index]
    df = get_data(soup, section_info)

    # print('\tSection {}: {}'.format(section_index, section_info))
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
                report[awr_sections[section_index]] = extract_sql_table(df)

            case 18:
                report[awr_sections[section_index]] = extract_sql_table(df)

            case 19:
                report[awr_sections[section_index]] = extract_sql_table(df)

            case 4 | 5 | 8 | 20:
                report[awr_sections[section_index]] = df.iloc[0:table_size].reindex(index=range(0, table_size))

            case 21:
                key_list = []
                value_list = []
                # print(f"instance efficiency percentages - df - {df}")
                populate_kv_lists(df.columns, key_list, value_list, 0)
                populate_kv_lists(df.columns, key_list, value_list, 2)

                for row in df.itertuples():

                    if row[1] == row[1]:
                        populate_kv_lists(row, key_list, value_list, 1)

                    if row[3] == row[3]:
                        populate_kv_lists(row, key_list, value_list, 3)

                report[awr_sections[section_index]] = pd.DataFrame(data={"Parameter": key_list, "Value": value_list})

            case 22:
                report[awr_sections[section_index]] = df.iloc[0:table_size].reindex(index=range(0, table_size))

            case _:
                print("Section {} not expected".format(section_index))
    else:
        # This is to create an empty section if the section is missing from the AWr file, i.e. where there is no SQL versions
        report[awr_sections[section_index]] = pd.DataFrame(index=range(0, table_size), columns=range(0, 1))


def populate_kv_lists(df, key_list, value_list, index):
    # print(f"Key {df[index]} - type {df[index]}")
    # print(f"Value {df[index+1]} - type {df[index+1]}")
    key = df[index].replace(":", "").replace("%", "").strip()
    if type(df[index + 1]) is float:
        value = df[index + 1]
    else:
        value = float(df[index + 1][0:6])
    # print(f"Key {key} - Value {value}")
    key_list.append(key)
    value_list.append(value)


def extract_sql_table(df):
    section_df = df.iloc[0:table_size]
    sorted_df = section_df[sql_indexes].copy()
    for column in section_df.columns:
        if column not in sorted_df.columns:
            sorted_df[column] = section_df[column]
    return sorted_df.reindex(index=range(0, table_size))


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
            return

        # Read configuration
        try:
            thresholds = configuration.read_configuration()
        except OSError as err:
            print(f"OS error:", err)
            return
        except ValueError as err:
            print(f"Could not convert data to a number {err=}, {type(err)=}")
            return
        except KeyError as err:
            print(f"Configuration error {err=}, {type(err)=}")
            return
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            return

        # Process AWR files
        filelist = args.files.split(',')

        reports: dict = {}
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

                    # Extract and format the information of an AWR file
                    # for i, info in enumerate(infolist):            
                    # print (i, info)
                    for i in range(0, len(awr_sections)):
                        extract_awr_data(i, soup, report)
                        # if len(sections) == 0 or str(i) in sections:
                        # extractAWRData(i, info, soup, args.fmt, report)

                    # add the report to the list of reports
                    summary_df = report[summary_section_key].copy()
                    summary_df.set_index("Parameter", inplace=True)
                    begin_date_time = sanity_checks.at("beginDateTime", "Value", summary_df)

                    # Perform sanity checks of this report
                    sanity_checks.perform_sanity_checks(report, checks_section_key, thresholds)

                    # Add the report to the list of reports
                    reports[begin_date_time] = report
                finally:
                    if file_stream is not None:
                        file_stream.close()

        excel_tabs.print_reports(reports)

    finally:
        print('AWR2Excel.py Finished')


# def configuration():
#     config = read_config_file()
#     limit_execute_to_parse_error = float(config['CHECKS_THRESHOLDS']['limit_execute_to_parse_error'])
#     limit_concurrency_db_time_error = float(config['CHECKS_THRESHOLDS']['limit_concurrency_db_time_error'])
#     limit_event_waits_error = float(config['CHECKS_THRESHOLDS']['limit_event_waits_error'])
#     limit_version_one_error = float(config['CHECKS_THRESHOLDS']['limit_version_one_error'])
#     limit_version_all_error = float(config['CHECKS_THRESHOLDS']['limit_version_all_error'])
#     # print("\nConfiguration:")
#     # print(f"\tlimit_execute_to_parse_error: {limit_execute_to_parse_error}")
#     # print(f"\tlimit_concurrency_db_time_error: {limit_concurrency_db_time_error}")
#     # print(f"\tlimit_event_waits_error: {limit_event_waits_error}")
#     # print(f"\tlimit_version_one_error: {limit_version_one_error}")
#     # print(f"\tlimit_version_all_error: {limit_version_all_error}")
#     # print("\n")
#     thresholds = {"limit_execute_to_parse_error": limit_execute_to_parse_error,
#                   "limit_concurrency_db_time_error": limit_concurrency_db_time_error,
#                   "limit_event_waits_error": limit_event_waits_error,
#                   "limit_version_one_error": limit_version_one_error,
#                   "limit_version_all_error": limit_version_all_error}
#     print(f"\nConfiguration: {thresholds}\n")
#     return thresholds


if __name__ == '__main__':
    main()
