'''
* File: earthd_pi_ingest.py 
 *
 * Ingest data in sheet 'PHYSICAL INFO' of Tephera data template to PetDB database.
 *
 * @author       Peng Ji
 * @created      Oct 3, 2022
 * @copyright    2007-2022 Interdisciplinary Earth Data Alliance, Columbia University. All Rights Reserved.
 *               Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *               Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

annotation_type_num     annotation_type_name           name appeared in Earthd template
91                          VolcanoSource              VOLCANO_SOURCE
92                          VolcanoNumber              VOLCANO_NUMBER
93                          Eruption                   ERUPTION
94	                        Formation                  FORMATION
95	                        Member                     MEMBER
96                          TephraName                 TEPHRA_NAME
97                          TephraComment              TEPHRA_COMMENT
98                          DepositMechanism           DEPOSIT_MECHANISM
99                          TephraThickness            TEPHRA_THICKNESS
100                         TephraThicknessUnit        TEPHRA_THICKNESS_UNIT
101                         TephraGrainSize            TEPHRA_GRAIN_SIZE
102                         TephraFreshColor           TEPHRA_FRESH_COLOR
103                         TephraAlteredColor         TEPHRA_ALTERED_COLOR
'''


#import pandas as pd
import xlrd
from datetime import date, datetime
import psycopg2
from config import config
import os

earthdHeader = ["SAMPLE_NAME", "VOLCANO_SOURCE", "VOLCANO_NUMBER", "ERUPTION", "FORMATION", "MEMBER", "TEPHRA_NAME", "TEPHRA_COMMENT", "DEPOSIT_MECHANISM", "TEPHRA_THICKNESS",
                "TEPHRA_THICKNESS_UNIT", "TEPHRA_GRAIN_SIZE", "TEPHRA_FRESH_COLOR", "TEPHRA_ALTERED_COLOR"]
tephraAnnotationDict = {"VOLCANO_SOURCE": 91, "VOLCANO_NUMBER": 92, "ERUPTION": 93, "FORMATION": 94,
                        "MEMBER": 95, "TEPHRA_NAME": 96, "TEPHRA_COMMENT": 97, "DEPOSIT_MECHANISM": 98, "TEPHRA_THICKNESS": 99,
                        "TEPHRA_THICKNESS_UNIT": 100, "TEPHRA_GRAIN_SIZE": 101, "TEPHRA_FRESH_COLOR": 102, "TEPHRA_ALTERED_COLOR": 103}


def findSampleIdByName(sampleName):
    for row in range(2, sampleSheet.nrows):
        if sampleSheet.cell_value(row, 0) == -1:
            return None
        if str(sampleSheet.cell_value(row, 1)).strip() == sampleName.strip():
            # return match 'SAMPLE_ID'(equal to sampling_feature_code in table sampling_feature)
            return str(sampleSheet.cell_value(row, 0)).strip()

def cleanAnnotationInDB (refNum):
    annotationCheckQuery = '''  select sfa.sampling_feature_annotation_num,sfa.annotation_num  from sampling_feature_annotation sfa join annotation a  on sfa.annotation_num=a.annotation_num  where a.annotation_type_num >90 and a.data_source_num =%s ''' 
    arrySampleAnnotationNum = []
    arryAnnotationNum = []
    with conn.cursor() as curs:
        curs.execute( annotationCheckQuery, (refNum, ))
        rows = curs.fetchall()
    for row in rows:
        print(row)
        arrySampleAnnotationNum.append(row[0])
        arryAnnotationNum.append(row[1])
    resSampleAnnotationNum = tuple([*set(arrySampleAnnotationNum)])
    resAnnotationNum = tuple([*set(arryAnnotationNum)])
    deleteSampleAnnotationQuery = ''' DELETE FROM sampling_feature_annotation WHERE sampling_feature_annotation_num in ''' + str(resSampleAnnotationNum)
    deleteAnnotationQuery = ''' DELETE FROM annotation where annotation_num in ''' + str(resAnnotationNum)
    with conn.cursor() as curs:
        if len(resSampleAnnotationNum)>0:
            curs.execute(deleteSampleAnnotationQuery)
        if len(resAnnotationNum)>0:
            curs.execute(deleteAnnotationQuery)
        conn.commit()

    # main function

reportFileName = 'earthd_pi_ingest_report_' + str(date.today()) + '.txt'
reportFileObj = open(reportFileName, 'w')
entries = os.listdir('validated_files/')

for entry in entries:
    print("Entry is: ", entry)
    reportFileObj.write("******************\n")
    reportFileObj.write(entry + "\n")
    reportFileObj.write("******************\n")
    # create dabase connection
    params = config()
    #print('Connecting to the database...')
    conn = psycopg2.connect(**params)

    fileName = 'validated_files/' + entry

    workBook = xlrd.open_workbook(fileName)

    refSheet = workBook.sheet_by_name('REFERENCE')
    sampleSheet = workBook.sheet_by_name('SAMPLES')
    physicalInfoSheet = workBook.sheet_by_name('PHYSICAL INFO')

    refNumber = refSheet.cell_value(0, 1)

    cleanAnnotationInDB(refNumber)


    isRowEnd = False
    for row in range(2, physicalInfoSheet.nrows):
        if isRowEnd:
            break

        #print("row is: ",row)
        for col in range(0, 13):
            if col == 0:
                if physicalInfoSheet.cell_value(row, 0) == -1:
                    isRowEnd = True
                    break
                sampleId = findSampleIdByName(
                    str(physicalInfoSheet.cell_value(row, 0)).strip())
                if sampleId is None:
                    reportFileObj.write("The sample \'" + str(physicalInfoSheet.cell_value(row, 0)) + "\'  in cell A" + str(
                        row+1) + " of sheet \'PHYSICAL INFO\' was not found in sheet \'SAMPLES\'.\n")
                    break
                else:
                    # retrieve sampling_feature_num by sampling_feature_code
                    sampleSelectQuery = ''' SELECT sampling_feature_num FROM sampling_feature WHERE sampling_feature_code=%s AND sampling_feature_type_num=1'''
                    with conn.cursor() as curs:
                        # second param must be tuple
                        curs.execute(sampleSelectQuery, (sampleId, ))
                        sampleNumObj = curs.fetchone()
                    if sampleNumObj is None:
                        reportFileObj.write("The sample \'" + sampleId + "\'(" + str(physicalInfoSheet.cell_value(
                            row, 0)) + ")  in cell A" + str(row+1) + " of sheet \'PHYSICAL INFO\' was not found in database.\n")
                        break
                    sampleNum = sampleNumObj[0]
            else:
                cellValue = physicalInfoSheet.cell_value(row, col)
                if col in (2,3):
                    if physicalInfoSheet.cell_type(row, col) in (2,3):
                        cellValue = str(int(physicalInfoSheet.cell_value(row, col)))
                if str(cellValue).strip() != '':
                    annotationInsertQuery = ''' INSERT INTO annotation(annotation_type_num,annotation_text,data_source_num,annotation_entered_time) VALUES (%s, %s, %s, %s) RETURNING annotation_num'''
                    annotationTypeNum = tephraAnnotationDict[earthdHeader[col]]
                    annotationText = str(cellValue).strip()
                    annotationEnteredTime = datetime.now()
                    annotataionTuple = (
                        annotationTypeNum, annotationText, refNumber, annotationEnteredTime)
                    annotationSelectQuery = ''' SELECT annotation_num FROM annotation WHERE annotation_type_num=%s AND annotation_text=%s AND data_source_num=%s'''
                    with conn.cursor() as curs:
                        curs.execute(
                            annotationSelectQuery, (annotationTypeNum, annotationText, refNumber))
                        annotationNumObj = curs.fetchone()
                    # create new annotation if it does not exist
                    if annotationNumObj is None:
                        with conn.cursor() as curs:
                            curs.execute(annotationInsertQuery,
                                         annotataionTuple)
                            annotationNumObj = curs.fetchone()
                        conn.commit()
                        reportFileObj.write(str(annotataionTuple) + '\n')
                    annotationNum = annotationNumObj[0]
                    #print("annotation is",annotationNum)

                    # create new sampling_feature_annotation if it does not exist
                    sampleAnnotationSelectQuery = ''' SELECT sampling_feature_annotation_num FROM sampling_feature_annotation WHERE sampling_feature_num=%s AND annotation_num=%s '''
                    with conn.cursor() as curs:
                        curs.execute(sampleAnnotationSelectQuery,
                                     (sampleNum, annotationNum))
                        sampleAnnotationNumObj = curs.fetchone()
                    if sampleAnnotationNumObj is None:
                        sampleAnnotationInsertQuery = ''' INSERT INTO sampling_feature_annotation(sampling_feature_num,annotation_num) VALUES (%s,%s) RETURNING sampling_feature_annotation_num'''
                        with conn.cursor() as curs:
                            curs.execute(sampleAnnotationInsertQuery,
                                         (sampleNum, annotationNum))
                            sampleAnnotationNumObj = curs.fetchone()
                        conn.commit()
                        reportFileObj.write(
                            sampleId + ' ' + str(sampleAnnotationNumObj) + '\n')

    conn.close()
print('Ingestion is done.')
