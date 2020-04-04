#!/usr/bin/env python

import os, json, glob, re, sys
import pickle, base64
import urllib

header = '    <h1 style="font-size: 14pt">%(headline)s</h1>'
clearstr = """    <p style="clear: both;">
"""
scan_spec_str = "Parameter = %(sparam)s, Value = %(svalue)s, type = %(stype)s"

def Compare_Models(Picklefile1, Picklefile2, Reportfile = "figures/Model_Comparisons.html", Templatefile = "figures/Template.html"):
    """
    Compare old and new models.
    """
    #Plottype = 'timecourse'

    with open(Picklefile1,"rb") as fp: New_Fig_Object = pickle.load(fp)
    with open(Picklefile2,"rb") as fp: Old_Fig_Object = pickle.load(fp)
    with open(Templatefile) as fp: htmllines = fp.read().splitlines()
    Reportfile = Reportfile.split('.')[0] + "_" + New_Fig_Object["sweep_id"] + "_" + Old_Fig_Object["sweep_id"] + ".html"

    htmllines.insert(4, header % { "headline" : "Parameter Sweep Comparisons"})
    imagelem = """    <p style="float:left; text-align: center; width: 30%%;">
        <img src="%(pngstr)s" style="width: 100%%">%(model)s mRNA at %(scan)s
        </p>
    """
    imageentries = []

    for snew, sold in zip(sorted(New_Fig_Object.keys()), sorted(Old_Fig_Object.keys())):
        for Plottype in ["bar", "timecourse"]:

            pngstrnew = "data:image/png;base64," + urllib.quote(New_Fig_Object[snew][Plottype]["pngstr"])
            scan_str_new = New_Fig_Object[snew][Plottype]["scan_label"]
            imagelemstrnew = imagelem % { "pngstr" : pngstrnew, "model" : "New model", "scan" : scan_str_new }
            pngstrold = "data:image/png;base64," + urllib.quote(Old_Fig_Object[sold][Plottype]["pngstr"])
            scan_str_old = Old_Fig_Object[sold][Plottype]["scan_label"]
            imagelemstrold = imagelem % { "pngstr" : pngstrold, "model" : "Old model", "scan" : scan_str_old }
            imageentries.append(imagelemstrnew + "\n" + imagelemstrold + "\n" + clearstr)

    htmllines.insert(5, "\n".join(imageentries))
    with open(Reportfile,"w") as fp: fp.write("\n".join(htmllines))

def Time_Intervals(Picklefile, Reportfile = "figures/Plot_Figures.html", Templatefile = "figures/Template.html"):
    """
    Generates a report for three different time intervals
    """

    with open(Picklefile,"rb") as fp: Fig_Data = pickle.load(fp)
    Fig_Object = Fig_Data["plots"]
    with open(Templatefile) as fp: htmllines = fp.read().splitlines()
    Reportfile = Reportfile.split('.')[0] + "_" + Fig_Data["sweep_id"] + ".html"

    htmllines.insert(4, header % { "headline" : "Expressions" })
    imagelem = """    <p style="float:left; text-align: center; width: 30%%;">
        <img src="%(pngstr)s" style="width: 100%%">%(species)s %(type)s at %(interval)s for %(scan)s
        </p>
    """
    imageentries = []
    sorted_plots = sorted(Fig_Object.keys(), key = lambda x : Input_Data["plot_param"].index(x))
    intervals = [ str(elem) + "h" for elem in Input_Data["end_times"] ]

    for species in sorted_plots:
        for interval in intervals:
            for plottype in ["bar", "timecourse"]:
                pngstr = "data:image/png;base64," + urllib.quote(Fig_Object[species][plottype]["pngstr"][interval])
                scan_str = Fig_Object[species][plottype]["scan_label"][interval]
                imagelemstr = imagelem % { "pngstr" : pngstr, "species" : species, "type" : plottype, "interval" : interval, "scan" : scan_str }

                imageentries.append(imagelemstr + "\n")
            imageentries.append("\n" + clearstr)

    htmllines.insert(5, "\n".join(imageentries))
    with open(Reportfile,"w") as fp: fp.write("\n".join(htmllines))

if __name__ == '__main__':

    #Picklefile1 = "figures/Plot_Figures_new_model.pickle"
    #Picklefile2 = "figures/Plot_Figures_old_jak_dependent.pickle"
    Inputfile = sys.argv[1]
    Outdir = sys.argv[2]
    Reportfile = os.path.join(Outdir, "Time_Intervals_New_Model.html")
    with open(Inputfile) as fp: Input_Data = json.load(fp)
    Picklefile = os.path.join(Outdir, "Plot_Figures_%s.pickle" % Input_Data["sweep_id"])
    Time_Intervals(Picklefile)
