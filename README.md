# petdb-earthd

## Steps to run earthd_pi_rain_check.py

1. pip3 install xlrd
2. make sure there are folders earthd_files and validated_files exist
3. put the files need to be validated into the folder earthd_files
4. make sure there is no opened files in folder earthd_files
5. python3 earthd_pi_rain_check.py
6. open the file validationResult.txt to check the results
7. fix issues and re-run the script until all files pass the validation

### note

1. All files passed will be moved to the folder validated_files automatically
2. The file validationResult.txt is reset everytime the script is run
3. Directory structue should looks like below

    ```bash
    ├── earthD (can be changed anyway)
        ├── earthd_files 
        ├── validated_files
        ├── earthd_pi_rain_check.py
        ├── README.md
    ```
