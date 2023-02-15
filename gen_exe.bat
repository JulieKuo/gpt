@echo off


set data_path=%1
set requirements=%2
set python=%3
set log_path=%4


cd /d %data_path% 
echo 1. Change directory to %data_path% > %log_path%

echo 2. Install virtualenvr >> %log_path%
pip install virtualenv

echo 3. Create venv >> %log_path%
virtualenv .venv

echo 4. Activate venv >> %log_path%
call .venv\Scripts\activate

echo 5. Install packages from %requirements% >> %log_path%
pip install -r %requirements%

echo 6. Install pyinstaller >> %log_path%
pip install pyinstaller

echo 7. Generate exe file from %python% >> %log_path%
pyinstaller -F %python%

echo 8. Move exe file to upper directory >> %log_path%
move dist\*.exe %data_path%\..

timeout /t 1

echo 9. Delete folders and files >> %log_path%
rd /s /q .venv build dist
del /f /q *.spec

echo 10. Deactivate >> %log_path%
deactivate

echo Done!