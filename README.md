# petdb-earthd

## Steps to run earthd_pi_rain_check.py

1. pip3 install xlrd
2. make sure there are folders earthd_files and validated_files exist
3. put the files need to be validated into the folder earthd_files
4. make sure there is no opened files in folder earthd_files
5. python3 earthd_pi_rain_check.py
6. open the file validationResult.txt to check the results
7. fix issues and re-run the script until all files pass the validation

## Steps to run earthd_pi_ingest.py

1. make sure earthd_pi_rain_check.py has been executed
2. make sure there is no opened files in folder validated_files
3. create database.ini
4. python3 db_connect_test.py (test db connection)
5. python3 earthd_pi_ingest.py
6. earthd_pi_ingest_report_YYYY_MM_DD.txt will be created automatically

### note

1. All files passed rain check will be moved to the folder validated_files automatically
2. The file validationResult.txt is reset everytime the script is run
3. Directory structue should looks like below

    ```bash
    ├── earthD (can be changed anyway)
        ├── earthd_files 
        ├── validated_files
        ├── database.ini
        ├── config.py
        ├── db_connect_test.py
        ├── earthd_pi_rain_check.py
        ├── earthd_pi_ingest.py
        ├── README.md
    ```
