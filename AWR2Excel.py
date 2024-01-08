import pandas as pd
from bs4 import BeautifulSoup
import glob
import argparse
from pathlib import Path
from modules.constants import awr_sections
from modules.constants import summary_section_key
from modules.constants import checks_section_key

import modules.configuration as configuration
import modules.extract_data as extract_data
import modules.sanity_checks as sanity_checks
import modules.excel_tabs as excel_tabs
import modules.track_elements as track_elements


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
            configuration.read_configuration()
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
            files = glob.glob(fn)
            for file in files:
                file_stream = None
                try:
                    file_stream = open(file)
                    print('Processing data from AWR file: {}'.format(file))

                    # Scrap AWR html report
                    soup = BeautifulSoup(file_stream, 'lxml')

                    # Create report, summary section and add the AWR filename to the summary section
                    report = {summary_section_key: pd.DataFrame(columns=['Parameter', 'Value'])}
                    report[summary_section_key].loc[len(report[summary_section_key])] = {'Parameter': 'file',
                                                                                         'Value': Path(file).name}

                    # Extract and format the tables from the AWR file
                    for section_index in range(0, len(awr_sections)):
                        extract_data.process_section(section_index, soup, report)

                    # add the report to the list of reports
                    summary_df = report[summary_section_key].copy()
                    summary_df.set_index("Parameter", inplace=True)
                    begin_date_time = sanity_checks.at("beginDateTime", "Value", summary_df)

                    # Perform sanity checks of this report
                    sanity_checks.perform_sanity_checks(report, checks_section_key, configuration.thresholds)

                    # Add the report to the list of reports
                    reports[begin_date_time] = report
                finally:
                    if file_stream is not None:
                        file_stream.close()

        excel_tabs.print_reports(reports)

    finally:
        print(f"get_tracked_sql_ids - {track_elements.get_tracked_sql_ids()}")
        print(f"get_tracked_sql_modules - {track_elements.get_tracked_sql_modules()}")
        print('AWR2Excel.py Finished')


if __name__ == '__main__':
    main()
