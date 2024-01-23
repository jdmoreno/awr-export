python AWR2Excel.py -files ".\test\in\PRD - 2023-10-02\awr_rmgtibp_1_231002_1100_1130.html" # AWR with versions
python AWR2Excel.py -files ".\test\in\PRD - 2023-10-02\awr_rmgtibp_1_231002_1500_1505.html" # AWR with some problems in the instance efficiency percentages
python AWR2Excel.py -files ".\test\in\PPD - 2023-12-23 - asd -soak\awrrpt_1_160_161.html"   # AWR no versions
python AWR2Excel.py -files ".\test\in\PRD - 2023-10-02\*.html"                              # AWRs production rollback 2023-10-02
python AWR2Excel.py -files ".\test\in\PPD - 2023-12-23 - asd -soak\*.html"                  # AWRs preproduction ASD soak 2023-12-23

python AWR2Excel.py -files ".\test\in\PPD - 2023-12-21 - 6th - soak\*.html"                 # AWRs preproduction Jan 6TH releas soak 2023-12-21



# Summary
python "C:\3.git\2.jm.code\awr-export\AWR2Excel.py" --s -files "C:\2.documents\rmg\Projects\EPS.Platform\Platform.Projects\2023.Active.Space.decommision\parallel\PPD\*.html" --c "AWR2Excel-ppd.toml"

# One day
python "C:\3.git\2.jm.code\awr-export\AWR2Excel.py" -files "C:\2.documents\rmg\Projects\EPS.Platform\Platform.Projects\2023.Active.Space.decommision\parallel\PPD\AWR-PPD-PARALLEL-16thJAN\*.html" --c "AWR2Excel-ppd.toml"

# One AWR
python AWR2Excel.py --f ".\test\in\PPD - 2023-12-21 - 6th - soak\*.html"
python "D:\3.source.code\phyton.JM\awr-export\AWR2Excel.py" --f ".\awr\PDD\AWR-PPD-PARALLEL-12thJAN\awrrpt_1_447_448.html" --o ".\output" --c "AWR2Excel-ppd.toml"