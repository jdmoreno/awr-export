# Test cmd
python AWR2Excel.py -files .\test\in\PRD-2023-10-02\awr_rmgtibp_1_231002_1100_1130.html    # AWR with versions
python AWR2Excel.py -files .\test\in\test2\*.html # Several AWR, no versions
python AWR2Excel.py -files .\test\in\PRD-2023-10-02\*.html    # AWRs production rollback


library cache: mutex X
