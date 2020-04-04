#!/usr/bin/env python

import sys
import os, csv, json, copy
import sweep
from runsweep import RunSweep, Odesolve
from visualize import PlotSweep

def Run_Sweeps(Sweep_Space_Full, Copasifile, conv):
    """
    Runs the individual component of the sweeps
    """
    sweepers = []
    for elem in Sweep_Space_Full:
        sweeper = RunSweep(Copasifile, elem, conv = conv)
        Odesolve(sweeper)
        sweepers.append(sweeper)
    return sweepers


def Plot_Results(sweep_id, sweepers, control_sweep, plot_param, end_times):
    
    ps = PlotSweep(sweep_id, sweepers, plot_param, control_sweep)
    ps.get_data()

    Filenames = []
    for elem in plot_param:
        #for end_time in end_times:
        end_time = 48
        fig = ps.barsubplot(elem, normalization = "control")
        ps.Plotprocess(fig, elem, "barsub", outdir = outdir)
        pngfile = os.path.join(outdir, "%s_%s_%s_%sh.png" % (elem.replace(' ','_'), "barsub", sweep_id, str(end_time)))
        Filenames.append(pngfile)
        fig = ps.timecourse(elem, end_time = end_time, title = "%s hours" % str(end_time))
        ps.Plotprocess(fig, elem, "timecourse", end_time = end_time, outdir = outdir)
        pngfile = os.path.join(outdir, "%s_%s_%s_%sh.png" % (elem.replace(' ','_'), "timecourse", sweep_id, str(end_time)))
        Filenames.append(pngfile)
            #fig = ps.barplot(elem, end_time = end_time, normalization = "control", title = "%s hours" % str(end_time))
            #ps.Plotprocess(fig, elem, "bar", end_time = end_time, outdir = outdir)
        

    ps.save_figstr(outdir = outdir)

    return ps, Filenames

def Control_Sweep(sweep_info, param_key, Copasifile, conv):
    
    sweep_info["Nrg"]["value"] = sweep_info["Nrg"]["control"]
    sweep_info[param_key]["value"] = sweep_info[param_key]["value"][0]
    del sweep_info["Nrg"]["control"]
    control_sweep = RunSweep(Copasifile, sweep_info.values(), conv = conv)
    Odesolve(control_sweep)

    return control_sweep

def Manage_Sweeps(outer_elem):
    """
    Manage the sweeps for a particular range of parameters
    """
    sweep_info_nrg = copy.deepcopy(Input_Data["sweep_info"]["Nrg"])
    Markdown_String = "### %s" % outer_elem["substitute"]["reaction"]
    Bar_Plots = []
    Time_Course = []
    for val in outer_elem["value"]:
        tempdict = copy.deepcopy(outer_elem)
        tempdict["value"] = [val]
        sweep_info = copy.deepcopy(Input_Data["sweep_info"])
        sweep_info[tempdict["substitute"]["name"]] = tempdict
        control_sweep = Control_Sweep(copy.deepcopy(sweep_info), tempdict["substitute"]["name"], Input_Data["Copasifile"], Input_Data["conv"])
        reaction_name = tempdict["substitute"]["reaction"].split(' - ')[-1].replace(' ','_')
        sweep_id = Input_Data["sweep_id"] + "%s_%s_%s" % (reaction_name, tempdict["substitute"]["name"], str(val))
        Sweep_Space_Full = sweep.Generate_Sweeps(sweep_info)
        sweepers = Run_Sweeps(Sweep_Space_Full, Input_Data["Copasifile"], Input_Data["conv"])
        ps, Filenames = Plot_Results(sweep_id, sweepers, control_sweep, Input_Data["plot_param"], Input_Data["end_times"])
        Bar_Plots.append("![Bar Plots %s](%s){width=30%%}" % (outer_elem["substitute"]["reaction"],os.path.join(outdir, Filenames[0])))
        Time_Course.append("![Time Course Plots %s](%s){width=30%%}" % (outer_elem["substitute"]["reaction"],os.path.join(outdir, Filenames[1])))

    Markdown_String += "\n\n" + "\n".join(Bar_Plots) + "\n\n" + "\n".join(Time_Course)

    return Markdown_String
    
            

if __name__ == '__main__':
    
    Inputfile = sys.argv[1]
    outdir = sys.argv[2]

    with open(Inputfile) as fp: Input_Data = json.load(fp)
    with open("Outer_Sweep.json") as fp: outer_sweep = json.load(fp)["outer_sweep"]
    Markdown_Strings = []
    for outer_elem in outer_sweep:
        Markdown_String = Manage_Sweeps(outer_elem)
        Markdown_Strings.append(Markdown_String + "\n\n")
        print "Sweep completed for %s" % outer_elem["substitute"]["reaction"]

    with open("Markdown_Output_JAKI.md","w") as fp: fp.write("\n".join(Markdown_Strings))



