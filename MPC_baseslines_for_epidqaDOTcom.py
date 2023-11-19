# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 17:36:42 2023

@author: mikell
mikellATwustlDOTedu
justinDOTmikellATgmailDOTcom
"""


import os

import glob
import pandas as pd
import numpy as np





from xml.dom import minidom

def parse_MPC_checkxml_file(filename):
    
    
    
    myDict = {}
    
    model = minidom.parse(filename)
    NodeList = model.getElementsByTagName('UUID')
    n = NodeList[0]
    myDict['UUID'] = n.childNodes[0].data
    
    #NodeList = model.getElementsByTagName('BaselineUUID')
    #n = NodeList[0]
    #myDict['BaselineUUID'] = n.childNodes[0].data
    
    NodeList = model.getElementsByTagName('IsBaseline')
    n = NodeList[0]
    myDict['is_baseline'] = n.childNodes[0].data
        
    return(myDict)
    

    
    
def EPIDQA_scrape_MPC_baselines(directory, NumfilesToSearch=100, verbose=0):
    """
    Purpose:
        This function is useful for getting the new BASELINE UUIDs from MPC. 
        These are currently required in EPIDQA.com.
        Someday it will pull automatically?
    
    Implementation Details:
        Find all files and directories MPCChecks directory. 
        Sort these by name so the most recent directories appear at top of list. (using the MPCCheck folder naming convention)
        Only evalute the first NumfilesToSearch directories. 
        
    Parameters
    ----------
    directory : a string representing the directory to parse
        e.g. r"\\TDS\SN\MPCChecks"
        
    NumFoldersToSearch: an integer to only look at the N most recent folders/entries in the MPCCheck directory. 
        
        

    Returns
    -------
    a list of maps that can be converted to pandas dataframe with corresponding keys: 
    
    UUID
    isBaseline 

    """
    
    #folder_list = next(os.walk(directory))[1]
    
    
    #Truebeams
    folder_list = glob.glob("{0}/NDS*".format(directory))
    
    if(len(folder_list)==0):
        #Halycons    
        folder_list = glob.glob("{0}/HAL*".format(directory))
        
    assert len(folder_list) > 0, "unable to locate any directories matching NDS* or HAL* under {0}".format(directory)
        
    folder_list.sort(reverse=True)
    
    if(len(folder_list) < NumfilesToSearch):
        NumfilesToSearch = len(folder_list)
    sub_list = folder_list[0:NumfilesToSearch]
    myList = []
    

    for i in sub_list:
        if verbose > 0: 
            print(i)
        f = "{0}\\Check.xml".format(i)
        
        myMap={}
        if(os.path.exists(f)):
            myMap = parse_MPC_checkxml_file(f)
            shrtf = f.split('\\')[-2]
            myMap['filename']=f
            #ts = shrtf.split('-')
            #myMap['easyID']="{0}-{1}-{2}-{3}-{4}".format(ts[2],ts[3],ts[4],ts[5], ts[-1])
            myList.append(myMap)
        else:
            print("skipping due to file not existing: {0}".format(f))
        
        
    df = pd.DataFrame(myList)
    return(df)

    
def findAndCreateExcelOfBaselines(MPCCheckdir, outfilename, ndirs=100, verbose=0):
    """
    Parameters
    ----------
    MPCCheckdir : string
        e.g. r"\\TDS\\SN\\MPCChecks"
        The MCPChecks folder that contains the folders containing all data relevant to a check. 
        e.g. the NDS-WKS-SN....BeamCheckTemplate6x directories.
        
    outfilename: string
        The full path to write a csv file to. 
        e.g. r"C:\\Users\\name\\epidqa_baselines.csv"
        
    ndirs : integer, optional
    Will look for the check.xml file in the last ndirs acquired. 
    The default is 100. 
    Default should be fine if you just rebaselined within a few days and dont run MPC hourly. 
    
    verbose : int, optional
        Will print more to stdout or stderr. The default is 0.

    Returns
    -------
    The output consists of a csv file makes it easy to selectcopied versions of the Check.xml files associated with baselines in MPC. 
    The Check.xml files are copied to the outdir and then renamed to make it simple to upload into 
    EPIDQA.com
    
    
    EXAMPLE USAGE:
        directory = r"\\TDS\SNofmachine\MPCChecks"
        outfilename = "epidqabaseline.xlsx"
        findAndCreateExcelOfBaselines(directory, out)
        
        Next open up the excel file (will write to the current directory in your pyton interpreter). 
        Then open up epidQA.com and use the 
    """
    
    df =  EPIDQA_scrape_MPC_baselines(MPCCheckdir, NumfilesToSearch=ndirs, verbose=verbose)
    
    index = df.is_baseline == 'true'
    assert np.sum(index) > 0, "no baselines founds, check directory or increase ndirs"
    
    tdf = df[index]
    
    
    tdf.to_excel(outfilename)
    
    return(tdf)
