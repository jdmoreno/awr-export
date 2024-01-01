#!/usr/bin/python
'''
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

'''

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
TableSize = 10
NoneType = type(None)
sqlIndexes = ["SQL Id", "SQL Module", "SQL Text"]

# list of awr sections to parse
awr_sections = [
            'This table displays database instance information', 
            'This table displays host information',
            'This table displays snapshot information',                     
            'This table displays load profile', 
            'This table displays top 10 wait events by total wait time', 
            'This table displays wait class statistics ordered by total wait time',
            'This table displays system load statistics',
            'This table displays CPU usage and wait statistics',
            'This table displays IO profile',
            'This table displays top SQL by elapsed time', 
            'This table displays top SQL by CPU time', 
            'This table displays top SQL by user I/O time', 
            'This table displays top SQL by buffer gets', 
            'This table displays top SQL by physical reads', 
            'This table displays top SQL by unoptimized read requests', 
            'This table displays top SQL by number of executions', 
            'This table displays top SQL by number of parse calls', 
            'This table displays top SQL by amount of shared memory used', 
            'This table displays top SQL by version counts', 
            'This table displays top SQL by cluster wait time', 
            'This table displays Foreground Wait Events and their wait statistics',
            'This table displays instance efficiency percentages'
            ]

def getData(content, filter):    
    '''
        Find AWR Table Section using the filter
    '''
    table = content.find('table', {'summary': filter})     
    # Testing if it didn´t find awr section
    if not isinstance(table, NoneType):    
        ret = pd.read_html(StringIO(str(table)), header=0)
        section_df = ret[0] 
        # ret[0].rename(columns = {'Unnamed: 0': 'Info'}, inplace=True)
    else:
        section_df = None
    return section_df

def strToFloat(strNum):  
    tmp_strNum = strNum.replace(" (mins)", "") # Remove '(mins)'
    tmp_strNum = tmp_strNum.replace(",", "") # Remove ','
    return float(tmp_strNum)

def extractAWRData(sectionIndex, soup, report):  
    '''
        Print the pandas dataframe in the format defined
    '''
    sectionInfo = awr_sections[sectionIndex]
    df = getData(soup, sectionInfo)

    # if not isinstance(data, NoneType):    
    # df = data[0]

    # print(data, df)
        # Just for quick tests. Don't forget to comment
        # if sectionIndex not in [1,2]:
        #     return
        
    print('\tSection {}: {}'.format(sectionIndex, sectionInfo))
    if not isinstance(df, NoneType):    
        match sectionIndex:
            case 0:
                dfSummary = report["summaryDF"]

                dbName = df.at[0, 'DB Name']                        
                dfSummary.loc[len(dfSummary)] = {'Parameter':'dbName', 'Value':dbName }

            case 1:
                dfSummary = report["summaryDF"]

                hostName = df.at[0, 'Host Name']                        
                dfSummary.loc[len(dfSummary)] = {'Parameter':'hostName', 'Value':hostName }

            case 2:           
                dfSummary = report["summaryDF"]

                dateTime_str = df.at[0, 'Snap Time'] # Format: 01-Oct-23 13:00:33
                dateTime_format = "%d-%b-%y %H:%M:%S"
                begin_dateTime = datetime.strptime(dateTime_str, dateTime_format)

                dfSummary.loc[len(dfSummary)] = {'Parameter':'beginDateTime', 'Value':begin_dateTime }

                dfSummary.loc[len(dfSummary)] = {'Parameter':'beginTime', 'Value':begin_dateTime.time() }

                dateTime_str = df.at[1, 'Snap Time'] # Format: 01-Oct-23 13:00:33
                end_dateTime = datetime.strptime(dateTime_str, dateTime_format)
                dfSummary.loc[len(dfSummary)] = {'Parameter':'endDateTime', 'Value':end_dateTime }

                beginSessions = df.at[0, 'Sessions']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'beginSessions', 'Value':beginSessions }

                endSessions = df.at[1, 'Sessions']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'endSessions', 'Value':endSessions }

                elapsedTime = strToFloat(df.at[2, 'Snap Time'])
                dfSummary.loc[len(dfSummary)] = {'Parameter':'elapsedTime', 'Value':elapsedTime }

                dbTime = strToFloat(df.at[3, 'Snap Time'])
                dfSummary.loc[len(dfSummary)] = {'Parameter':'dbTime', 'Value':dbTime }

            case 3:           
                dfSummary = report["summaryDF"]

                logicalRead = df.at[4, 'Per Second']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'logicalRead', 'Value':logicalRead }

                physicalRead = df.at[6, 'Per Second']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'physicalRead', 'Value':physicalRead }

                physicalWrite = df.at[7, 'Per Second']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'physicalWrite', 'Value':physicalWrite }

                parsesSQL = df.at[15, 'Per Second']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'parsesSQL', 'Value':parsesSQL }

                executesSQL = df.at[20, 'Per Second']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'executesSQL', 'Value':executesSQL }

            case 6:                        
                dfSummary = report["summaryDF"]

                beginLoadAverage = df.at[0, 'Load Average Begin']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'beginLoadAverage', 'Value':beginLoadAverage }

                endLoadAverage = df.at[0, 'Load Average End']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'endLoadAverage', 'Value':endLoadAverage }

                userCPU = df.at[0, '%User']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'userCPU', 'Value':userCPU }

            case 7:                        
                dfSummary = report["summaryDF"]

                totalCPU =  df.at[0, '%Total CPU']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'totalCPU', 'Value':totalCPU }

                busyCPU = df.at[0, '%Busy CPU']
                dfSummary.loc[len(dfSummary)] = {'Parameter':'busyCPU', 'Value':busyCPU }

            case 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 19:   
                # SQL tables. Move SQLId, User and SQL statement to left colunm for easier comparison
                extractSQLTable(sectionIndex, report, df)

            case 18:   
                extractSQLTable(sectionIndex, report, df)

            case 19:   
                extractSQLTable(sectionIndex, report, df)

            case 19:   
                extractSQLTable(sectionIndex, report, df)

            case 4 | 5 | 8 | 20 | 21:                  
                sectionKey = f'section_{sectionIndex}'
                report[sectionKey] = df.iloc[0:TableSize].reindex(index=range(0, TableSize))

            case 22:   
                sectionKey = f'section_{sectionIndex}'
                report[sectionKey] = df.iloc[0:TableSize].reindex(index=range(0, TableSize))

            case _:
                print ("Section {} not expected".format(sectionIndex))
    else:
        sectionKey = f'section_{sectionIndex}'
        report[sectionKey] = pd.DataFrame(index=range(0, TableSize), columns=range(0, 1))

    if awr_sections[sectionIndex] == 'This table displays top SQL by version counts':
        sql_ordered_by_version_count(report[sectionKey])

    if awr_sections[sectionIndex] == 'This table displays top 10 wait events by total wait time':
        top_10_foreground_events_by_total_wait_time()

    if awr_sections[sectionIndex] == 'This table displays top SQL by number of executions':
        sql_ordered_by_executions()

    if awr_sections[sectionIndex] == 'This table displays instance efficiency percentages':
        instance_efficiency_percentages()

    if awr_sections[sectionIndex] == 'This table displays load profile':
        load_profile()

def sql_ordered_by_version_count(df_sql_ordered_by_version_count):
    # SQL Id version count - Total < 200
    # SQL Id version count - Individual < 100
    print('sql_ordered_by_version_count')
    print(df_sql_ordered_by_version_count)

    return

def top_10_foreground_events_by_total_wait_time():
    print('top_10_foreground_events_by_total_wait_time')
    return

def sql_ordered_by_executions():
    print('sql_ordered_by_executions')
    return

def instance_efficiency_percentages():
    print('instance_efficiency_percentages')
    return

def load_profile():
    print('load_profile')
    return

def extractSQLTable(sectionIndex, report, df):
    sectionKey = f'section_{sectionIndex}'
    dfSection = df.iloc[0:TableSize]
    sorted_df = dfSection[sqlIndexes].copy()
    for column in dfSection.columns:
        if column not in sorted_df.columns:
            sorted_df[column] = dfSection[column]
    report[sectionKey] = sorted_df.reindex(index=range(0, TableSize))

def printReports(reports):
    # print (reports) sorted by date
    list_keys = sorted(reports.keys())

    wb = Workbook()
    SheetCounter = 0
    for key in list_keys:
    # Create a tab per AWR file
        SheetName = "AWR2Excel_{}".format(SheetCounter)
        SheetCounter += 1
        ws = wb.create_sheet(SheetName)
        report = reports[key]

    # Write sections
        for sectionKey in report:
            sectionDF = report[sectionKey]
            ws.append([])           

            # Append the name of the section
            sectionList = sectionKey.split("_", 2)
            
            if len(sectionList) > 1:
                sectionIndex = int(sectionList[1])
                sectionTitle = awr_sections[sectionIndex]
            else:
                sectionTitle = "Summary"
            ws.append([sectionKey, sectionTitle])

            for row in dataframe_to_rows(sectionDF, index=False, header=True):
                ws.append(row)           
    # write a file object along with .xlsx extension
    # convert datetime obj to string
    str_current_datetime = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
    out_filename = str_current_datetime + "_AWR2Excel" +".xlsx"
    wb.save(out_filename)

def main():
    try:
        # CMD Parameters
        version = '1.0'
        version_description = 'AWR2Excel - Oracle AWR to Excel utility {}'.format(version)

        parser = argparse.ArgumentParser(description = version_description) 
        parser.add_argument('-files', help='Comma-delimited list of HTML AWR files', default='')
               
        # If parse fail will show help
        args = parser.parse_args()
        
        sections = []

        if args.files == '':
            print('You need to pass the AWR HTML file name.')
            print('Example: AWR2Excel.py -file /path/awrfile.html or AWR2Excel.py -file /path/*.html')            
        else:                
            filelist = args.files.split(',')

            reports = {}
            for fn in filelist:
                files=glob.glob(fn)           
                for file in files:
                    try:
                        print('Processing data from AWR file: {}'.format(file))
                        f = open(file)
                        
                        soup = BeautifulSoup(f,'lxml')     

                        report = {}
                        report["summaryDF"] = pd.DataFrame(columns=['Parameter', 'Value'])

                        # Add the AWR filename to the summary
                        report["summaryDF"].loc[len(report["summaryDF"])] = {'Parameter':'file', 'Value':Path(file).name }

                        # Extract and format the information of a AWR file
                        # for i, info in enumerate(infolist):            
                            # print (i, info)
                        for i in range(0, len(awr_sections)):
                            extractAWRData(i, soup, report)
                            # if len(sections) == 0 or str(i) in sections:
                            # extractAWRData(i, info, soup, args.fmt, report)

                        # add the report to the list of reports
                        dfSummary = report["summaryDF"].copy()
                        dfSummary.set_index("Parameter", inplace=True)
                        # print(dfSummary)

                        beginDateTime = dfSummary.at["beginDateTime", "Value"]      
                        # print(beginDateTime)
                        
                        reports[beginDateTime] = report
                    finally:
                        f.close()

            printReports(reports)
    
    finally:    
        print('AWR2Excel.py Finished')

if __name__ == '__main__':
    main()
