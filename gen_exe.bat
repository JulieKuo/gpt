@echo off


set result_path=%1
set requirements_path=%2
set python_path=%3
set log_path=%4


cd /d %result_path% 
echo 1. Change working directory > %log_path%

echo 2. Install virtualenv and pyinstaller >> %log_path%
pip install virtualenv pyinstaller

echo 3. Create venv >> %log_path%
virtualenv .venv

echo 4. Activate venv >> %log_path%
call .venv\Scripts\activate

echo 5. Install packages >> %log_path%
pip install -r %requirements_path%

echo 6. Copy python_path to result_path >> %log_path%
copy %python_path% %result_path%

echo 7. Generate exe file >> %log_path%
pyinstaller -F %python_path%

echo 8. Move exe file to upper directory >> %log_path%
move dist\*.exe %result_path%

echo 9. Delete folders >> %log_path%
rd /s /q .venv
rd /s /q build
rd /s /q dist

echo 10.Delete files >> %log_path%
del /f /q *.py
del /f /q *.spec

echo 11. Deactivate >> %log_path%
deactivate

echo Done!