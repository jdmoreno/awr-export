import pandas as pd
from bs4 import BeautifulSoup
import glob
# import argparse
import logging
from pathlib import Path

import modules.arguments as arguments
from modules.constants import awr_sections
from modules.constants import summary_section_key
from modules.constants import checks_section_key

import modules.constants as constants
import modules.configuration as configuration
import modules.extract_data as extract_data
import modules.sanity_checks as sanity_checks
import modules.excel_tabs as excel_tabs
import modules.track_elements as track_elements
import modules.aggregations as aggregations


def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        # CMD Parameters
        version = '1.0'
        version_description = 'AWR2Excel - Oracle AWR to Excel utility {}'.format(version)

        # Process arguments
        args = arguments.process_arguments(version_description)
        arguments.print_arguments()

        if args.files == '':
            print('You need to pass the AWR HTML file name.')
            print('Example: AWR2Excel.py -file /path/awrfile.html or AWR2Excel.py -file /path/*.html')
            return


        # Read configuration
        try:
            config_path = args.config
            print(f"config path {config_path}")
            configuration.read_configuration(config_path)
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

        configuration.print_configuration()

        # Identify the files to process
        filelist = args.files.split(',')

        reports: dict = {}
        for fn in filelist:
            # files = glob.glob(fn)

            file_path = Path(fn)
            parent_path = file_path.parent
            file_name = file_path.name
            files = sorted(parent_path.rglob(file_name))

            for file in files:
                process_awr(file, reports)

        excel_tabs.print_reports(reports)

    finally:
        # print(f"\nget_tracked_sql_modules - {track_elements.get_tracked_sql_modules()}")
        print('\nAWR2Excel.py Finished')


def process_awr(file, reports):
    file_stream = None
    try:
        file_stream = open(file)
        print('Processing data from AWR file: {}'.format(file))

        # Scrap AWR html report
        soup = BeautifulSoup(file_stream, 'lxml')
    finally:
        if file_stream is not None:
            file_stream.close()
    # Create report, summary section and add the AWR filename to the summary section
    report = {summary_section_key: pd.DataFrame(columns=['Parameter', 'Value'])}
    report[summary_section_key].loc[len(report[summary_section_key])] = {'Parameter': 'file',
                                                                         'Value': Path(file).name}
    # clear tracked stuff
    track_elements.clear_tracked_sql_ids()
    track_elements.clear_tracked_sql_modules()
    # Extract and format the tables from the AWR file
    for section_index in range(0, len(awr_sections)):
        extract_data.process_section(section_index, soup, report)
    # add the report to the list of reports
    summary_df = report[summary_section_key].copy()
    summary_df.set_index("Parameter", inplace=True)
    # begin_date_time = sanity_checks.at("beginDateTime", "Value", summary_df)
    # Append tracked SQLs section to report
    complete_track_sql_ids = {}
    found_sql_ids = track_elements.get_tracked_sql_ids()
    for sql_id in configuration.track_sql_ids:
        value = found_sql_ids.get(sql_id)
        if value is None:
            executions = 0
            sql_statement = ""
        else:
            executions = value[0]
            sql_statement = value[1]
        complete_track_sql_ids[sql_id] = [executions, sql_statement]
    tracked_sql_ids_df = pd.DataFrame.from_dict(complete_track_sql_ids, orient="index",
                                                columns=["Executions", "SQL Text"])
    tracked_sql_ids_df.reset_index(inplace=True)
    tracked_sql_ids_df.rename(columns={'index': 'SQL Id'}, inplace=True)
    report[constants.tracked_sql_ids_section_key] = tracked_sql_ids_df.iloc[0:constants.table_size].reindex(
        index=range(0, constants.table_size))
    # Append tracked Modules section to report
    tracked_sql_ids_df = pd.DataFrame.from_dict(track_elements.get_tracked_sql_modules(), orient="index",
                                                columns=["Executions", "SQL Text", "SQL Module"])
    tracked_sql_ids_df.reset_index(inplace=True)
    tracked_sql_ids_df.rename(columns={'index': 'SQL Id'}, inplace=True)
    report[constants.tracked_sql_modules_section_key] = tracked_sql_ids_df.iloc[0:constants.table_size].reindex(
        index=range(0, constants.table_size))

    # aggregations
    aggregations.aggregations()
    aggregations_df = pd.DataFrame.from_dict(aggregations.accum_aggregations, orient="index")
    aggregations_df.reset_index(inplace=True)
    # print(f"{aggregations_df.columns}")
    aggregations_df.rename(columns={'index': 'Aggregation', 0: 'Total'}, inplace=True)
    # print(f"{aggregations_df.columns}")
    # print(f"{aggregations_df}")
    report[constants.aggregations_section_key] = aggregations_df.iloc[0:constants.table_size].reindex(index=range(0, constants.table_size))

    # Perform sanity checks of this report
    sanity_checks.perform_sanity_checks(report, checks_section_key, configuration.thresholds)

    # Add the report to the list of reports
    begin_date_time = sanity_checks.at("beginDateTime", "Value", summary_df)
    reports[begin_date_time] = report


# def process_arguments(version_description):
#     parser = argparse.ArgumentParser(description=version_description)
#     parser.add_argument('-files', help='Comma-delimited list of HTML AWR files', default='')
#     parser.add_argument('-config', help='Path to configuration file', default='AWR2Excel.ini')
#     # If parse fail will show help
#     args = parser.parse_args()
#     return args


if __name__ == '__main__':
    main()
