@echo off
setlocal enabledelayedexpansion

:: Set the folder containing the files
set "folder_path=M:\python\pickups\"

:: Specify the output file
set "output_file=allplayers.json"

:: Create or clear the output file
:: echo [] > "%output_file%"

:: Loop through all files in the folder
for %%F in ("%folder_path%\*.*") do (
    echo Processing %%F...
    python arrays.py "%%F" "%output_file%"
)

echo All files processed. Results stored in %output_file%.