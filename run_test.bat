@echo off
chcp 65001 > nul
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"
python test_simple.py > test_result.txt 2>&1
type test_result.txt
