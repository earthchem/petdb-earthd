'''
 * File: earthd_pi_rain_check.py 
 *
 * Validate sheet 'PHYSICAL INFO' of Tephera data template.
 *   1. check if column header correct
 *   2. check if values in column DEPOSIT_MECHANISM correct
 *   3. check if sample exist in sheet SAMPLES and any of data sheets (ROCKS, MINERALS and INCLUSIONS)
 *
 * @author       Peng Ji
 * @created      Oct 3, 2022
 * @copyright    2007-2022 Interdisciplinary Earth Data Alliance, Columbia University. All Rights Reserved.
 *               Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *               Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import xlrd
import os

# pre-defined column header of sheet 'PHSICAL INFO', agreed by Sara and Erin on Oct 13 2022 meeting
# VOLCANO_NUMBER/VOLCANO_NUMER, TEPHRA_NAME/TEPHRA, DEPOSIT_MECHANISM/DEPOSIT_DEPOSIT, TEPHRA_THICKNESS_UNIT/TEPHRA_THICKNESS UNIT

earthdHeader = ["SAMPLE_NAME", "VOLCANO_SOURCE", "VOLCANO_NUMBER", "ERUPTION", "FORMATION",
                "MEMBER", "TEPHRA_NAME", "TEPHRA_COMMENT", "DEPOSIT_MECHANISM", "TEPHRA_THICKNESS",
                "TEPHRA_THICKNESS_UNIT", "TEPHRA_GRAIN_SIZE", "TEPHRA_FRESH_COLOR", "TEPHRA_ALTERED_COLOR"]
# controlled vocabulary used for the property DEPOSIT_MECHANISM
TephraMechanismVoc = ["TEPHRA FALL", "REWORKED",
                    "PYROCLASTIC FLOW", "SURGE DEPOSIT", "LAVA FLOW"]
# controlled vocabulary used for the property TEPHRA_THICKNESS UNIT
#TephraThicknessUnitVoc = ["m", 'cm', 'mm']
# controlled vocabulary used for the property TEPHRA_GRAIN_SIZE
#TephraGrainSizeVoc = ["BLOCKS/BOMBS",
#                      "LAPILLI", "VOLCANIC ASH", "VOLCANIC DUST"]

# match sampleName between sheet 'PHYSICAL INFO' and 'SAMPLES', 'ROCKS','MINERALS','INCLUSIONS'
def matchSampleName(sampleName):
    sheetNames = ['SAMPLES','ROCKS','MINERALS','INCLUSIONS']
    matchSheets = []
    noDataSheets = []
    for sheetName in sheetNames:
        if sheetName != 'SAMPLES':
            rowStart = 8
            rowEndFlagCol = 2
            sampleNameCol = 2
        else:
            rowStart = 2
            rowEndFlagCol = 0
            sampleNameCol = 1
        workSheet = workBook.sheet_by_name(sheetName)
        for row in range(rowStart,workSheet.nrows):
            if workSheet.cell_value(row, rowEndFlagCol) == -1: 
                if row == rowStart:
                     noDataSheets.append(sheetName)             
                break
            else:
                if str(workSheet.cell_value(row, sampleNameCol)).strip() == sampleName:
                    matchSheets.append(sheetName)
                    break
    if 'SAMPLES' in matchSheets:
        if any(matchSheets for item in ['ROCKS','MINERALS','INCLUSIONS']):
            # find match in sheet SAMPLES and one of data sheets(ROCKS, MINERALS, or INCLUSIONS)
            # retrun []
            return []
        else:
            # find match in sheet SAMPLES, but not any of data sheets(ROCKS, MINERALS, or INCLUSIONS)
            # return data sheets which have data  [?]
            return list(set(['ROCKS','MINERALS','INCLUSIONS'])-set(noDataSheets))
    else:
        if any(matchSheets for item in ['ROCKS','MINERALS','INCLUSIONS']):
            # find match in any of data sheets(ROCKS, MINERALS, or INCLUSIONS), but not in SAMPLES
            # return ['SAMPLES']
            return ['SAMPLES']
        else:
            # no match found in sheet SAMPLES or any of data sheets(ROCKS, MINERALS, or INCLUSIONS)
            # return 'SAMPLES' and data sheets which have data  ['SAMPLES', ?]
            return list(set(['SAMPLES','ROCKS','MINERALS','INCLUSIONS'])-set(noDataSheets))



entries = os.listdir('earthd_files/')
validationFileObj = open('validationResult.txt', 'w')
for entry in entries:
    print("Entry is: ", entry)
    validationFileObj.write("******************\n")
    validationFileObj.write(entry + "\n")
    validationFileObj.write("******************\n")

    fileName = 'earthd_files/' + entry
    

    workBook = xlrd.open_workbook(fileName)
    # check if sheet 'PHSICAL INFO' exist
    if ('PHYSICAL INFO' in workBook.sheet_names()):
        physicalInfoSheet = workBook.sheet_by_name('PHYSICAL INFO')
        # check if column header match with pre-defined
        colHeader = physicalInfoSheet.row_values(
            0, start_colx=0, end_colx=len(earthdHeader))
        isHeaderValidated = True # if pass the column header checking
        # column header checking
        for item in colHeader:
            if item == -1:
                validationFileObj.write(
                    "The current quantity of properties less than pre-defined quantity.\n")
                isHeaderValidated = False
                break
            else:
                if item not in earthdHeader:
                    if item in ["TEPHRA_DEPOSIT","VOLCANO_NUMER","TEPHRA_THICKNESS UNIT","TEPHRA"]:
                        isHeaderValidated = True
                    else:
                        validationFileObj.write(
                            "Property \'" + item + "\' does not match pre-defined property.\n")
                        isHeaderValidated = False
        if isHeaderValidated:
            isCellValidated = True
            for row in range(2, physicalInfoSheet.nrows):   # data start from row 2
                if physicalInfoSheet.cell_value(row, 0) == -1:     # end of rows
                    break
                else:
                    # check if sample name exist
                    matchSampleNameResult = matchSampleName(str(physicalInfoSheet.cell_value(row,0)).strip())
                    if  len(matchSampleNameResult) != 0:
                        isCellValidated = False
                        validationFileObj.write("The sample \'" + str(physicalInfoSheet.cell_value(row,0)) + "\'  in cell A" + str(row+1) + " of sheet \'PHYSICAL INFO\' does not match anyone in sheets " + str(matchSampleNameResult) +"\n")
                    # check column TEPHRA_DEPOSIT (index: 8)
                    if str(physicalInfoSheet.cell_value(row,8)).strip()!= '' and str(physicalInfoSheet.cell_value(row,8)) not in TephraMechanismVoc:
                        isCellValidated = False
                        validationFileObj.write("The value \'" + str(physicalInfoSheet.cell_value(row,8)) + "\'  in cell I" + str(row+1) + " of sheet \'PHYSICAL INFO\' is not in the controlled list of \'TEPHRA_DEPOSIT\'.\n")
                    # check column TEPHRA_THICKNESS UNIT (index: 10)
                    #if str(physicalInfoSheet.cell_value(row,10)).strip()!= '' and str(physicalInfoSheet.cell_value(row,10)) not in TephraThicknessUnitVoc:
                    #    isCellValidated = False
                    #    validationFileObj.write("The value \'" + str(physicalInfoSheet.cell_value(row,10)) + "\'  in cell K" + str(row+1) + " of sheet \'PHYSICAL INFO\'is not in the controlled list of \'TEPHRA_THICKNESS UNIT\'.\n")
                    # check column TEPHRA_GRAIN_SIZE (index: 11)
                    #if str(physicalInfoSheet.cell_value(row,11)).strip()!= '' and str(physicalInfoSheet.cell_value(row,11)) not in TehpraGrainSizeVoc:
                    #    isCellValidated = False
                    #    validationFileObj.write("The value \'" + str(physicalInfoSheet.cell_value(row,11)) + "\'  in cell L" + str(row+1) + " of sheet \'PHYSICAL INFO\' is not in the controlled list of \'TEPHRA_GRAIN_SIZE\'.\n")
            if isCellValidated:
                destFileName = 'validated_files/' + entry
                os.rename(fileName, destFileName)           
    else:
        validationFileObj.write("Sheet \'PHYSICAL INFO\' does not exist.\n")
print('Validation is done!')
validationFileObj.close()
