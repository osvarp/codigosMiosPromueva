@echo off
REM
g++ output_graph.cpp -o ograph.exe || goto end

ograph > input.txt || goto end
python g_viz.py < input.txt

:end
echo on