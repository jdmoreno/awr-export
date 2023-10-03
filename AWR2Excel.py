#!/usr/bin/python
'''
    AWRp.py - Oracle AWR Parser 
    Copyright 2019 Alexandre Marti. All rights reserved. To more info send mail to alexandremarti@gmail.com.
    Licensed under the Apache License, Version 2.0. See LICENSE.txt for terms & conditions.

    Purpose: Print AWR HTML file content as a table format.
    Author: Alexandre Marti
                  
    Usage:       
        python AWRp.py -files <html file name list or mask>         

    Optional Parameters
        -fmt: table type output format. the default format is psql 
              csv,plain,simple,grid,fancy_grid,pipe,orgtbl,jira,presto,psql,rst,mediawiki,moinmoin,youtrack,html,latex,latex_raw,latex_booktabs,textile,excel
              more details on https://pypi.org/project/tabulate/
              
        -listsections : print a list of all sections parsed by AWRp.py. It´s useful to find section number for parameter -sections
        -sections: used to restrict which awr sections the AWRp.py will return. use -listsections to get the list of sections available.        

    Example1:
        python AWRp.py -files /files/awrfile.html
    
    Example2:    
        python AWRp.py -files /files/*.html
        
    Example3:    
        python AWRp.py -files '/files/awrfile01.html','/files/awrfile02.html'

    Example4:        
        python AWRp.py -listsections
        
    Example5:        
        python AWRp.py -files /files/*.html -sections 1,3,4               

    Help:
        python AWRp.py -h

'''

import pandas as pd
from bs4 import BeautifulSoup
from tabulate import tabulate
import glob   
import argparse
import os
from io import StringIO 
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows

# Global variables        
TableSize = 10
NoneType = type(None)

def getData(content, filter):    
    '''
        Find AWR Table Section using the filter
    '''
    table = content.find('table', {'summary': filter})       
    # Testing if it didn´t find awr section
    if not isinstance(table, NoneType):    
        ret = pd.read_html(StringIO(str(table)), header=0)

        # 
        ret[0].rename(columns = {'Unnamed: 0': 'Info'}, inplace=True)
        return ret

def printTable(sectionIndex, sectionInfo, soup, fmt):  
    '''
        Print the pandas dataframe in the format defined
    '''
    data = getData(soup, sectionInfo)
    print('\nSECTION {}: {}\n'.format(sectionIndex, sectionInfo))

    if not isinstance(data, NoneType):    
        df = data[0]
        # update summary

        match sectionIndex:
            case 0:
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 1:
                summaryDF = []
                hostName = df.at[0, 'Host Name']                        
                summaryDF = ['hostName', hostName]

                df = pd.DataFrame({'Values':summaryDF})
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 2:           
                summaryDF = []
                beginDateTime = df.at[0, 'Snap Time']
                summaryDF.append(('beginDateTime', beginDateTime))

                # summaryDF.update({'Values':['beginDateTime', beginDateTime]})

                endDateTime = df.at[1, 'Snap Time']
                summaryDF.append(('endDateTime', endDateTime))
                # summaryDF.update({'Values':['endDateTime', endDateTime]})

                # beginSessions = df.at[0, 'Sessions']
                # summaryDF.update({'beginSessions': beginSessions})

                # endSessions = df.at[1, 'Sessions']
                # summaryDF.update({'endSessions': endSessions})

                # df = pd.DataFrame([summaryDF])
                # df = pd.DataFrame(summaryDF, columns=['Values'])
                df = pd.DataFrame(columns=['Values'])
                for (key, value) in summaryDF:
                    df[key, 'Values'].loc[key] = value
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 3:           
                summaryDF = {}             
                logicalRead = df.at[4, 'Per Second']
                summaryDF.update({'logicalRead': logicalRead})

                physicalRead = df.at[6, 'Per Second']
                summaryDF.update({'physicalRead': physicalRead})

                physicalWrite = df.at[7, 'Per Second']
                summaryDF.update({'physicalWrite': physicalWrite})

                parsesSQL = df.at[15, 'Per Second']
                summaryDF.update({'parsesSQL': parsesSQL})

                executesSQL = df.at[20, 'Per Second']
                summaryDF.update({'executesSQL': executesSQL})
                print(summaryDF)

            case 6:                        
                summaryDF = {}             
                beginLoadAverage = df.at[0, 'Load Average Begin']
                summaryDF.update({'beginLoadAverage': beginLoadAverage})

                endLoadAverage = df.at[0, 'Load Average End']
                summaryDF.update({'endLoadAverage': endLoadAverage})

                userCPU = df.at[0, '%User']
                summaryDF.update({'userCPU': userCPU})
                print(summaryDF)

            case 7:                        
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 8:                        
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 9: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 10: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 11: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 12: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 13: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 14: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 15: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 16: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 17: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 18: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case 19: 
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))

            case _:
                print(tabulate(df.iloc[0:TableSize], headers='keys', tablefmt=fmt, showindex=False))


def main():

    try:
        # CMD Parameters
        version = '1.0'
        version_description = 'AWRp - Oracle AWR Parser {}'.format(version)

        parser = argparse.ArgumentParser(description = version_description) 
        parser.add_argument('-files', help='Comma-delimited list of HTML AWR files', default='')
        parser.add_argument('-fmt', help='Table Format to display. The default is psql', 
                            default='psql', 
                            choices=['jira','csv','plain','simple','grid','fancy_grid','pipe','orgtbl','presto','psql','rst','mediawiki','moinmoin','youtrack','html','latex','latex_raw','latex_booktabs','textile','excel'])
        parser.add_argument('-listsections', help='List of all sections parsed by AWRp.py', action='store_true')        
        parser.add_argument('-sections', help='Comma-delimited numbers of awr sections to be returned by AWRp.py', default='')
               
        # If parse fail will show help
        args = parser.parse_args()
        
        sections = []
        if args.sections != '':
            sections = args.sections.split(',')

        # list of awr sections to parse
        infolist = ['This table displays database instance information', 
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
                    'This table displays top 10 wait events by total wait time'
                    ]
        
        if args.listsections:
            print('Printing the List of Parseable AWR Sections')
            print('===========================================\n')                
            for i, info in enumerate(infolist):                                
                print('    Section {}: {}'.format(i, info)) 
                
        elif args.files == '':
            print('Ops! You need to pass the HTML file name.')
            print('Example:')            
            print('    AWRp.py -file /path/awrfile.html or AWRp.py -file /path/*.html')            
        else:                
            filelist = args.files.split(',')
            
            for fn in filelist:
                files=glob.glob(fn)           
                for file in files:
                    try:
                        print('Data from File: {}\n'.format(file))
                        f=open(file)
                        
                        soup = BeautifulSoup(f,'lxml')     
                        for i, info in enumerate(infolist):                        
                            if len(sections) == 0 or str(i) in sections:
                                printTable(i, info, soup, args.fmt)

                    finally:
                        f.close()
    
    finally:    
        print('\nAWRp.py Finished\n')

if __name__ == '__main__':
    main()
