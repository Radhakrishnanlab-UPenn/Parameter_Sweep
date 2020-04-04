#!/usr/bin/env python

import sys, copy
import tempfile as tf
import os, csv, json
import subprocess
import sweep

change_ext = lambda filename, ext : os.path.splitext(filename)[0] + ext

def Odesolve(sweeper):
    """
    Solves a single instance of a sweeper
    gets the data and performs cleanup
    """
    sweeper.Change_Parameters()
    sweeper.Createtempfile()
    Outfilename = sweeper.change_report()
    sweeper.headers()
    sweeper.Writefile()
    sweeper.OdeRun()
    data = sweeper.Get_Data()
    status = sweeper.Cleanup()

class RunSweep:
    """
    Sets up, runs, collects data and
    cleans up particular instances of a
    parameter sweep
    """
    def __init__(self, inputfile, parameter, conv = 1.0):
        self.root = sweep.Generate_Xml(inputfile)
        self.parameter = parameter
        self.conv = conv
        self.status = "not started"

    def Change_Parameters(self):
        """
        Changes the sweep parameters
        """
        for param in self.parameter:
            if param["Paramtype"] == "Initial Species Values" :
                conv = self.conv
            else:
                conv = 1
            oldval, newval = sweep.SetCpsValues(self.root, param, conv = conv)
            param["value_change"] = (float(oldval)/conv, float(newval)/conv)
        
    def Createtempfile(self):
        fp = tf.NamedTemporaryFile(delete=False)
        self.tmpfile = fp.name

    def change_report(self, XPathstr = ".//*[@type='timeCourse']"):
        Task_Time_Course = sweep.Get_Elem(self.root, XPathstr)[0]
        Outfilename = change_ext(self.tmpfile, ".csv")
        Task_Time_Course = sweep.Set_Elem(Task_Time_Course, "target", Outfilename)
        self.output = Outfilename

        return Outfilename

    def headers(self):

        self.header = sweep.Get_Headers(self.root, ".//Table")

    def Writefile(self):
        sweep.Write_File(self.root, self.tmpfile)
        self.status = "ready"

    def OdeRun(self, copasipath='CopasiSE'):
        out = err = ''
        Copasi_Command = copasipath + ' --verbose ' + self.tmpfile
        p = subprocess.Popen(Copasi_Command,shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        for lines in iter(p.stdout.readline,''):
            out += lines.rstrip()
        for lines in iter(p.stderr.readline,''):
            err += lines.rstrip()
        streams = p.communicate()
        self.status = "completed"

        return out, err

    def Get_Data(self):
        """
        Extracts data for a particular run and appends to
        the input dictionary
        """
        time_course_data = { key : [] for key in self.header }

        if self.status == "completed":

            with open(self.output) as fp:
                reader = csv.DictReader(fp, fieldnames = self.header)
                for ii, row in enumerate(reader):
                    if ii == 0:
                        continue
                    else:
                        for key in row:
                            time_course_data[key].append(float(row[key]))

            self.data = time_course_data
        else:
            print "Run not completed for %s" % self.tmpfile

        return time_course_data

    def Cleanup(self):
        """
        Cleans up the temporary files
        """
        cpstatus = os.remove(self.tmpfile)
        csvstatus = os.remove(self.output)

        return cpstatus, csvstatus

if __name__ == '__main__':

    #Copasifile = "test/ErbB4-JAK2-STAT5_Yamda_Combined_Exec.cps"
    Inputfile = sys.argv[1]
    with open(Inputfile) as fp:
        Input_Data = json.load(fp)

    Sweep_Space_Full = sweep.Generate_Sweeps(Input_Data["sweep_info"])
    control_input = Input_Data["sweep_info"]["Nrg"]
    control_input["value"] = control_input["control"]
    del control_input["control"]
    control_sweep = RunSweep(Input_Data["Copasifile"], [control_input], conv = Input_Data["conv"])
    Odesolve(control_sweep)
    sweepers = []
    for elem in Sweep_Space_Full:
        sweeper = RunSweep(Input_Data["Copasifile"], elem, conv = Input_Data["conv"])
        Odesolve(sweeper)
        sweepers.append(sweeper)
