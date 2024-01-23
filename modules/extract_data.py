import pandas

import modules.configuration as configuration

from datetime import datetime
from io import StringIO
import logging

from modules.constants import awr_sections
from modules.constants import table_size
from modules.constants import summary_section_key
from modules.constants import sql_indexes

from modules.common import at
import modules.common as common
import pandas as pd

import modules.track_elements as track_elements


def get_section(soup, section_filter):
    """
        Find AWR Table Section using the filter
    """
    table = soup.find('table', {'summary': section_filter})

    # Testing if it didn´t find awr section
    if not isinstance(table, common.none_type):
        ret = pd.read_html(StringIO(str(table)), header=0)
        section_df = ret[0]
    else:
        section_df = None
    return section_df


def process_section(section_index, soup, report):
    """
        Print the pandas dataframe in the format defined
    """
    # Just for quick tests. Don't forget to comment
    # if section_index not in [21]:
    #     return

    section_info = awr_sections[section_index]
    df = get_section(soup, section_info)

    # print('\tSection {}: {}'.format(section_index, section_info))
    if not isinstance(df, common.none_type):
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

                elapsed_time = common.str_to_float(df.at[2, 'Snap Time'])
                df_summary.loc[len(df_summary)] = {'Parameter': 'elapsedTime', 'Value': elapsed_time}

                db_time = common.str_to_float(df.at[3, 'Snap Time'])
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

                system_cpu = df.at[0, '%System']
                df_summary.loc[len(df_summary)] = {'Parameter': 'systemCPU', 'Value': system_cpu}

                idle_cpu = df.at[0, '%Idle']
                df_summary.loc[len(df_summary)] = {'Parameter': 'idleCpu', 'Value': idle_cpu}

            case 7:
                df_summary = report[summary_section_key]

                total_cpu = df.at[0, '%Total CPU']
                df_summary.loc[len(df_summary)] = {'Parameter': 'totalCPU', 'Value': total_cpu}

                busy_cpu = df.at[0, '%Busy CPU']
                df_summary.loc[len(df_summary)] = {'Parameter': 'busyCPU', 'Value': busy_cpu}

            case 9 | 10 | 11 | 12 | 13 | 14:
                # SQL tables. Move SQLId, User and SQL statement to left column for easier comparison
                report[awr_sections[section_index]] = extract_sql_table_with_tracking(df)

            case 15:
                report[awr_sections[section_index]] = extract_sql_table_with_tracking(df)

            case 16:
                report[awr_sections[section_index]] = extract_sql_table_with_tracking(df)

            case 17:
                report[awr_sections[section_index]] = extract_sql_table_with_tracking(df)

            case 18:
                report[awr_sections[section_index]] = extract_sql_table_with_tracking(df)

            case 19:
                report[awr_sections[section_index]] = extract_sql_table_with_tracking(df)

            case 4 | 5 | 8 | 20:
                report[awr_sections[section_index]] = df.iloc[0:table_size].reindex(index=range(0, table_size))

            case 21:
                key_list = []
                value_list = []
                # print(f"instance efficiency percentages - df - {df}")
                common.populate_kv_lists(df.columns, key_list, value_list, 0)
                common.populate_kv_lists(df.columns, key_list, value_list, 2)

                for row in df.itertuples():

                    if row[1] == row[1]:
                        common.populate_kv_lists(row, key_list, value_list, 1)

                    if row[3] == row[3]:
                        common.populate_kv_lists(row, key_list, value_list, 3)

                report[awr_sections[section_index]] = pd.DataFrame(data={"Parameter": key_list, "Value": value_list})

            case 22:
                host_mem_used = df.at[3, 'End']

                df_summary = report[summary_section_key]
                df_summary.loc[len(df_summary)] = {'Parameter': 'hostMemUsed_SGA_PGA', 'Value': host_mem_used}

                # print(f"Memory Statistics - df - {df}")
                # print(f"% Host Mem used for SGA+PGA: {Host_Mem_used}")

                report[awr_sections[section_index]] = df.iloc[0:table_size].reindex(index=range(0, table_size))

            case _:
                print("Section {} not expected".format(section_index))
    else:
        # This is to create an empty section if the section is missing from the AWr file, i.e. where there is no SQL versions
        report[awr_sections[section_index]] = pd.DataFrame(index=range(0, table_size), columns=range(0, 1))


def extract_sql_table_with_tracking(df):
    """
    Extract information from a table with information about SQL statements
    Move sql_indexes columns as key columns of the table
    Consolidate information about tracked modules and SQL Id
    """
    # sorted_df = (df.iloc[0:table_size]).set_index(keys="SQL Id", inplace=False)
    # print(f"sorted_df SQL Id - \n{sorted_df}")

    temp_df = df.iloc[0:table_size]
    column_order = 0
    for column_name in sql_indexes:
        column = temp_df.pop(column_name)
        temp_df.insert(column_order, column_name, column)
        column_order += 1

    for row in temp_df.index:

        sql_id: str = temp_df.loc[row]["SQL Id"]
        if pandas.isna(sql_id):
            sql_id = ""

        sql_module: str = temp_df.loc[row]["SQL Module"]
        if pandas.isna(sql_module):
            sql_module = ""

        sql_text: str = temp_df.loc[row]["SQL Text"]
        if pandas.isna(sql_text):
            sql_text = ""

        executions = temp_df.loc[row]["Executions"]
        if pandas.isna(executions):
            executions = 0

        if sql_id in configuration.track_sql_ids:
            track_elements.add_sql_id(sql_id, executions, sql_text)

        # updated to check sqlplus in cases like sqlplus@RMULBGORA5002 (TNS V1-V3)
        for tracked_module in configuration.track_sql_modules:
            if sql_module in tracked_module:
                track_elements.add_sql_module(sql_module, sql_id, executions, sql_text)

    return temp_df.reindex(index=range(0, table_size))


# def aggregations():
#     accum_aggregations = {}
#
#     tracker = configuration.config["TRACKER"]
#     # logging.debug(f"tracker: {tracker}")
#
#     # Store sql ids to track
#     aggregations_track_sql_ids = tracker["track_sql_ids"]
#
#     tracked_sql_ids = track_elements.get_tracked_sql_ids()
#     for sql_id in tracked_sql_ids:
#         # print(f"aggregations - sql_id: {sql_id}")
#         for aggregation in aggregations_track_sql_ids:
#             if aggregation not in accum_aggregations.keys():
#                 accum_aggregations[aggregation] = 0
#             # print(f"\taggregations - aggregation: {aggregation} - values: {aggregations_track_sql_ids[aggregation]} ")
#             if sql_id in aggregations_track_sql_ids[aggregation]:
#                 # print(f"\t\tadd to aggregation: {aggregation} - sql_id: {sql_id} - executions {tracked_sql_ids[sql_id][0]}")
#                 accum_aggregations[aggregation] = accum_aggregations[aggregation] + tracked_sql_ids[sql_id][0]
#
#     print(f"aggregations: {accum_aggregations}")