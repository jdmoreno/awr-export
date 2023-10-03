# awr-export
Oracle AWR html export

Based on: https://www.linkedin.com/pulse/easy-way-developers-dbas-analyze-data-from-oracle-awr-alexandre-marti

# Usage:       
    python AWRp.py -files <html file name list or mask>         

# Optional Parameters
* fmt: table type output format. the default format is psql 
       csv,plain,simple,grid,fancy_grid,pipe,orgtbl,jira,presto,psql,rst,mediawiki,moinmoin,youtrack,html,latex,latex_raw,latex_booktabs,textile,excel
       more details on https://pypi.org/project/tabulate/ 
* listsections : print a list of all sections parsed by AWRp.py. It´s useful to find section number for parameter -sections
* sections: used to restrict which awr sections the AWRp.py will return. use -listsections to get the list of sections available.

# Examples
* Example1:
python AWRp.py -files /files/awrfile.html
    
* Example2:    
python AWRp.py -files /files/*.html
        
* Example3:    
python AWRp.py -files '/files/awrfile01.html','/files/awrfile02.html'

* Example4:        
python AWRp.py -listsections
        
* Example5:        
python AWRp.py -files /files/*.html -sections 1,3,4               

* Help:
python AWRp.py -h

