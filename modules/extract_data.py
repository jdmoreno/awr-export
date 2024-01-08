# from constants import awr_sections
# from constants import table_size
# from constants import summary_section_key
# from constants import sql_indexes

import modules.configuration as configuration
# from modules.configuration import track_sql_ids

from datetime import datetime
from io import StringIO

# import constants
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

            case 7:
                df_summary = report[summary_section_key]

                total_cpu = df.at[0, '%Total CPU']
                df_summary.loc[len(df_summary)] = {'Parameter': 'totalCPU', 'Value': total_cpu}

                busy_cpu = df.at[0, '%Busy CPU']
                df_summary.loc[len(df_summary)] = {'Parameter': 'busyCPU', 'Value': busy_cpu}

            case 9 | 10 | 11 | 12 | 13 | 14:
                # SQL tables. Move SQLId, User and SQL statement to left colunm for easier comparison
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
                report[awr_sections[section_index]] = df.iloc[0:table_size].reindex(index=range(0, table_size))

            case _:
                print("Section {} not expected".format(section_index))
    else:
        # This is to create an empty section if the section is missing from the AWr file, i.e. where there is no SQL versions
        report[awr_sections[section_index]] = pd.DataFrame(index=range(0, table_size), columns=range(0, 1))


def extract_sql_table(df):
    """
    Extract information from a table with information about SQL statements
    Move sql_indexes columns as key columns of the table
    Consolidate information about tracked modules and SQL Id
    """
    # global track_sql_ids

    section_df = df.iloc[0:table_size]
    sorted_df = section_df[sql_indexes].copy()

    # Can't since module are duplicate
    # sorted_df.set_index(keys='SQL Module', inplace=True)

    for column in section_df.columns:
        if column not in sorted_df.columns:
            sorted_df[column] = section_df[column]

    # print(f"\ntrack_sql_ids: {configuration.track_sql_ids} - type: {type(configuration.track_sql_ids)}")
    # for sql_id in configuration.track_sql_ids:
    #     executions = at("sql_id", "Executions", sorted_df)
    #     if executions is None:
    #         executions = 0
    #
    #     sql_statement = at("sql_id", "SQL Text", sorted_df)
    #     if sql_statement is None:
    #         sql_statement = ""
    #
    #     track_elements.add_sql_id(sql_id, executions, sql_statement)
    #
    #     print(f"{sql_id} - {sql_statement} - {executions}")

    return sorted_df.reindex(index=range(0, table_size))


def extract_sql_table_with_tracking(df):
    """
    Extract information from a table with information about SQL statements
    Move sql_indexes columns as key columns of the table
    Consolidate information about tracked modules and SQL Id
    """
    # sorted_df = (df.iloc[0:table_size]).set_index(keys="SQL Id", inplace=False)
    # print(f"sorted_df SQL Id - \n{sorted_df}")

    temp_df = df.iloc[0:table_size]
    # sorted_df = section_df[sql_indexes].copy()

    for row in temp_df.index:

        sql_id = temp_df.loc[row]["SQL Id"]

        sql_module = temp_df.loc[row]["SQL Module"]
        if sql_module is None:
            sql_module = ""

        sql_text = temp_df.loc[row]["SQL Text"]
        if sql_text is None:
            sql_text = ""

        executions = temp_df.loc[row]["Executions"]
        if executions is None:
            executions = 0

        print(f"{sql_module} - {sql_id} - {sql_text}")

        if sql_id in configuration.track_sql_ids:
            track_elements.add_sql_id(sql_id, executions, sql_text)
            # print(f"\tAdded to tracked_sql_id: {sql_id} - {executions} - {sql_text}")

        if sql_module in configuration.track_sql_modules:
            track_elements.add_sql_module(sql_module, sql_id, executions, sql_text)
            # print(f"\tAdded to tracked_sql_module: {module} - {sql_id} - {executions} - {sql_text}")

    return temp_df
