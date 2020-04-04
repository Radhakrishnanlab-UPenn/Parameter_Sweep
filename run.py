#!/usr/bin/env python

import tempfile as tf
import os, csv, json
import subprocess
import sweep
from runsweep import RunSweep

change_ext = lambda filename, ext : os.path.splitext(filename)[0] + ext
parameter = { "Paramtype" : "Initial Species Values", "substitute" : {"compartment" : "Cytoplasm","species" : "Her4"}, "value" : 12044283580000000 }
fileid = { "parameter" : parameter }

def CreateRunFile(root):
    """
    Creates a temporary file to write the root copasi
    object and the name of the report file
    """
    fp = tf.NamedTemporaryFile(delete=False)
    filename = fp.name
    XPathstr = ".//*[@type='timeCourse']"
    Task_Time_Course = sweep.Get_Elem(root, XPathstr)[0]
    Outfilename = change_ext(filename, ".csv")
    Task_Time_Course = sweep.Set_Elem(Task_Time_Course, "target", Outfilename)
    headers = sweep.Get_Headers(root, ".//Table")
    sweep.Write_File(root, filename)
    fp.close()

    fileid["name"] = filename
    fileid["output"] = Outfilename
    fileid["header"] = headers
    fileid["status"] = "not started"

    return filename

def OdeRun(input_cps, copasipath='CopasiSE'):
    """
    Wrapper function to call Copasi executable and run for
    a specified set of conditions

    Parameters
    -----------
    input_cps : string
        Name of the input copasi filename (*.cps)
    copasipath : string, optional
        Full path of the copasi executable. By default assumes
        CopasiSE is in system path and passes this name
        to subprocess
    logfile : string, optional
        Name of the output logfile. By default this writes
        the standard out and error of the Copasi command
        into a file with name obtain by joining input_cps
        name and current date and time

    Returns
    -------------
    out : string
        Output from Copasi collected by subprocess
    err : string
        Error messages from Copasi collected by subprocess
    """

    #Get system architecture and use appropriate copasi file
    out = ''
    err = ''
    Copasi_Command = copasipath

    #Call Copasi executable using the name of the input cps
    output_cps = input_cps
    p = subprocess.Popen(Copasi_Command + ' --verbose ' + input_cps,shell=True,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    for lines in iter(p.stdout.readline,''): out += lines.rstrip()
    for lines in iter(p.stderr.readline,''): err += lines.rstrip()
    streams = p.communicate()
    fileid["status"] = "completed"

    return out, err

def Get_Data():
    """
    Extracts data for a particular run and appends to
    the input dictionary
    """

    if fileid["status"] == "completed":
        time_course_data = { key : [] for key in fileid["header"] }

        with open(fileid["output"]) as fp:
            reader = csv.DictReader(fp, fieldnames = fileid["header"])
            for ii, row in enumerate(reader):
                if ii == 0:
                    continue
                else:
                    for key in row:
                        time_course_data[key].append(float(row[key]))

        fileid["data"] = time_course_data
    else:
        print "Run not completed for %s" % fileid["name"]

def Cleanup():
    """
    Cleans up the temporary files
    """
    cpstatus = os.remove(fileid["name"])
    csvstatus = os.remove(fileid["output"])

    return cpstatus, csvstatus

def Manage_Sweep(Runfile, Copasifile, SweepDataFile):
    """
    This function manages parameter setup and runs
    based on user data
    """
    Sweep_Space_Full = sweep.Generate_Sweeps(Runfile)
    root = sweep.Generate_Xml(Copasifile)
    Sweep_Data = {}
    for ii, parameters in enumerate(Sweep_Space_Full):
        Sweep_Data[ii] = {}
        sweeper = RunSweep(Copasifile, parameters, conv = 602214179000000)
        sweeper.Change_Parameters()
        sweeper.Createtempfile()
        Outfilename = sweeper.change_report()
        sweeper.headers()
        sweeper.Writefile()
        sweeper.OdeRun()
        Sweep_Data[ii]["parameter"] = sweeper.parameter
        Sweep_Data[ii]["data"] = sweeper.Get_Data()
        status = sweeper.Cleanup()
    with open(SweepDataFile, "w") as fp: json.dump(Sweep_Data, fp)
