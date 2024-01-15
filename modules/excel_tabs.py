from datetime import datetime

import pandas
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils.cell import get_column_letter
from openpyxl.styles import NamedStyle
from openpyxl.styles import PatternFill
from openpyxl.styles import numbers
from openpyxl.formatting.rule import FormulaRule

titles_row = 6
summary_range = "!$A$4:$B$23"
ad_checks_range = "!$A$262:$C$271"
tracked_sql_id_range = "!$A$236:$B$245"

ns_yyyy_mm_dd_h_mm_ss = NamedStyle(name="datetime", number_format="yyyy-mm-dd h:mm:ss")
ns_h_mm_ss = NamedStyle(name="time", number_format="h:mm:ss")

redFill = PatternFill(start_color='EE1111', end_color='EE1111', fill_type='solid')
amberFill = PatternFill(start_color='FFCC00', end_color='FFCC00', fill_type='solid')
greenFill = PatternFill(start_color='11EE11', end_color='11EE11', fill_type='solid')


def create_sheet_checks(work_book: Workbook, tabs: list):
    """
    Create the checks tab
    """
    work_sheet = work_book.create_sheet("Checks", 0)

    # summary_range = "!$A$4:$B$23"
    # ad_checks_range = "!$A$236:$C$244"

    ranges = [
        summary_range,
        summary_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range
    ]

    titles = [
        "file",
        "beginDateTime",
        "library_cache_lock_event_waits",
        "cursor_mutex_x_event_waits",
        "cursor_mutex_s_event_waits",
        "version_one",
        "version_all",
        "library_cache_mutex_x_event_waits",
        "cursor_pin_s_wait_on_x_event_waits",
        "execute_to_parse",
        "concurrency_db_time",
        "ratio_exceptions_events"
    ]

    print_ranges(ranges, work_sheet)

    print_titles(titles, work_sheet)

    row_start = 7
    for j in range(0, len(tabs)):
        row = row_start + j

        # Tab name
        column = 2
        work_sheet.cell(row=row, column=column, value=tabs[j])

        column_start = column + 1
        for i in range(0, len(titles)):
            column = column_start + i
            lookup_col = 2
            column_letter = get_column_letter(column)

            work_sheet.cell(row=row, column=column,
                            value=f"=VLOOKUP({column_letter}${titles_row},INDIRECT(_xlfn.CONCAT($B{row}, {column_letter}$5)), {lookup_col}, FALSE)")
            if column_letter == "D":
                work_sheet.cell(row=row, column=column).style = ns_yyyy_mm_dd_h_mm_ss

        # Conditional formatting
        work_sheet.conditional_formatting.add(f"E{row}:N{row}", FormulaRule(formula=[
            f"E{row}=False"], stopIfTrue=True, fill=greenFill))
        work_sheet.conditional_formatting.add(f"E{row}:I{row}", FormulaRule(formula=[
            f"E{row}=True"], stopIfTrue=True, fill=redFill))
        work_sheet.conditional_formatting.add(f"J{row}:N{row}", FormulaRule(formula=[
            f"J{row}=True"], stopIfTrue=True, fill=amberFill))


def create_sheet_summary(work_book: Workbook, df_sheets: pd.DataFrame, reports: dict):
    # create_sheet_summary(wb, df_sheets, reports)
    ranges = [
        summary_range,
        summary_range,
        summary_range,
        summary_range,
        summary_range,
        summary_range,
        summary_range,
        "",
        summary_range,
        summary_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,
        ad_checks_range,

        tracked_sql_id_range,
        tracked_sql_id_range,
        tracked_sql_id_range,
        tracked_sql_id_range,
        tracked_sql_id_range
    ]

    titles = [
        "file",
        "hostName",
        "beginDateTime",
        "beginTime",
        "endDateTime",
        "elapsedTime",
        "dbTime",
        "dbTime %",
        "userCPU",
        "endSessions",
        "library_cache_lock_event_waits",
        "cursor_mutex_x_event_waits",
        "cursor_mutex_s_event_waits",
        "version_one",
        "version_all",
        "library_cache_mutex_x_event_waits",
        "cursor_pin_s_wait_on_x_event_waits",
        "execute_to_parse",
        "concurrency_db_time",

        "42578a4znzq41",
        "7wcmwtk6ay1c9",
        "adxgsarcwdbdr",
        "cvq3d9nzdp5w7",
        "47byg9a0mdfmx"
    ]

    """
    Create the summary tab
    """
    work_sheet = work_book.create_sheet("Summary", 1)

    # Print ranges
    print_ranges(ranges, work_sheet)

    # Print titles
    print_titles(titles, work_sheet)

    # Print data
    print(f"df_sheets: {df_sheets}")
    keys = df_sheets.loc[:, "keys"].to_list()
    tabs = df_sheets.loc[:, "sheets"].to_list()
    print(f"tabs: {tabs}, {type(tabs)}")

    row_start = 7
    for j in range(0, len(tabs)):
        row = row_start + j

        # Tab name
        column = 2
        work_sheet.cell(row=row, column=column, value=tabs[j])

        column_start = column + 1
        for i in range(0, len(titles)):
            column = column_start + i
            if i < 10:
                lookup_col = 2
            else:
                if i < 19:
                    lookup_col = 3
                else:
                    lookup_col = 2

            column_letter = get_column_letter(column)
            match column_letter:
                case "E":
                    work_sheet.cell(row=row, column=column,
                                    value=f"=VLOOKUP({column_letter}${titles_row},INDIRECT(_xlfn.CONCAT($B{row}, {column_letter}$5)), {lookup_col}, FALSE)")
                    work_sheet.cell(row=row, column=column).style = ns_yyyy_mm_dd_h_mm_ss

                case "F":
                    work_sheet.cell(row=row, column=column,
                                    value=f"=VLOOKUP({column_letter}${titles_row},INDIRECT(_xlfn.CONCAT($B{row}, {column_letter}$5)), {lookup_col}, FALSE)")
                    work_sheet.cell(row=row, column=column).style = ns_h_mm_ss
                case "G":
                    work_sheet.cell(row=row, column=column,
                                    value=f"=VLOOKUP({column_letter}${titles_row},INDIRECT(_xlfn.CONCAT($B{row}, {column_letter}$5)), {lookup_col}, FALSE)")
                    work_sheet.cell(row=row, column=column).style = ns_yyyy_mm_dd_h_mm_ss

                case "H":
                    work_sheet.cell(row=row, column=column,
                                    value=f"=VLOOKUP({column_letter}${titles_row},INDIRECT(_xlfn.CONCAT($B{row}, {column_letter}$5)), {lookup_col}, FALSE)")
                    work_sheet.cell(row=row, column=column).number_format = "0.00"

                case "J":
                    work_sheet.cell(row=row, column=column, value=f"=$I{row}/$H{row}")
                    work_sheet.cell(row=row, column=column).number_format = "0.00"

                case "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S":
                    work_sheet.cell(row=row, column=column,
                                    value=f"=VLOOKUP({column_letter}${titles_row},INDIRECT(_xlfn.CONCAT($B{row}, {column_letter}$5)), {lookup_col}, FALSE)")
                    work_sheet.cell(row=row, column=column).number_format = numbers.BUILTIN_FORMATS[3]

                case "V" | "W" | "X" | "Y" | "Z":
                    work_sheet.cell(row=row, column=column,
                                    value=f"=_xlfn.IFNA(VLOOKUP({column_letter}${titles_row},INDIRECT(_xlfn.CONCAT($B{row}, {column_letter}$5)), {lookup_col}, FALSE), 0)")
                    work_sheet.cell(row=row, column=column).number_format = numbers.BUILTIN_FORMATS[3]

                case _:
                    work_sheet.cell(row=row, column=column,
                                    value=f"=VLOOKUP({column_letter}${titles_row},INDIRECT(_xlfn.CONCAT($B{row}, {column_letter}$5)), {lookup_col}, FALSE)")


def print_titles(titles, work_sheet):
    row = 6
    column_start = 3
    for i in range(0, len(titles)):
        column = column_start + i
        work_sheet.cell(row=row, column=column, value=titles[i])


def print_ranges(ranges, work_sheet):
    row = 5
    column_start = 3
    for i in range(0, len(ranges)):
        column = column_start + i
        work_sheet.cell(row=row, column=column, value=ranges[i])


def print_reports(reports: dict):
    # print (reports) sorted by date
    list_keys = sorted(reports.keys())

    wb = Workbook()
    sheet_counter = 0
    sheets = []
    # write one sheet per AWR
    for key in list_keys:
        # Create a tab per AWR file
        sheet_name = f"AWR2Excel_{sheet_counter}"
        sheets.append(sheet_name)
        # sheets.append({"key": key, "sheet_name": sheet_name})
        # sheets.append({"key": key, "sheet_name": sheet_name})
        # print(f"sheets: {sheets}")

        sheet_counter += 1
        ws = wb.create_sheet(sheet_name)
        report = reports[key]

        # Write the sections of an AWR
        for section_key in report:
            section_df = report[section_key]
            ws.append([])

            ws.append([section_key])

            for row in dataframe_to_rows(section_df, index=False, header=True):
                ws.append(row)

    # name = sheets[0]["sheet_name"]
    # print(f"sheets: {name}")
    # d = {'keys': list_keys, 'sheets': sheets}
    df_sheets = pandas.DataFrame(data={'keys': list_keys, 'sheets': sheets})
    # print(df)

    # create checks sheet
    create_sheet_checks(wb, sheets)

    # create summary sheet
    create_sheet_summary(wb, df_sheets, reports)

    # convert datetime obj to string
    # write a file object along with .xlsx extension
    str_current_datetime = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
    out_filename = str_current_datetime + "_AWR2Excel" + ".xlsx"
    wb.save(out_filename)
