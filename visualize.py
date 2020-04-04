#!usr/bin/env python

import os, sys, pickle, base64
import StringIO
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import operator
from string import Template

divlist = lambda lst, fac : [ elem/float(fac) for elem in lst ]
index = lambda data, end_time : np.where(data[:,0] == end_time*60*60)[0][0] if end_time != 'end' else -1

class PlotSweep:
    """
    Class to generate plots for specific
    parameter sweep conditions
    """
    def __init__(self, sweep_id, runsweeps, plot_params, control_sweep):
        self.sweep_id = sweep_id
        self.runsweeps = runsweeps
        self.plot_params = plot_params
        self.control_sweep = control_sweep
        self.plot_data = []
        self.plots = { key : {} for key in self.plot_params }
        self.plottext = {}
        self.scan_param = {}

    def get_data(self):
        self.control_data = { "Time" : self.control_sweep.data["Time"] }
        self.control_data.update({ key : self.control_sweep.data[key] for key in self.plot_params })
        for runsweep in self.runsweeps:
            sweep_data = { "Time" : runsweep.data["Time"] }
            sweep_data.update({ key : runsweep.data[key] for key in self.plot_params })
            self.plot_data.append({ "scan_label" : self.__scan_label(runsweep.parameter), "sweep_data" : sweep_data })
            for param in runsweep.parameter:
                if param["substitute"]["name"] in self.scan_param:
                    self.scan_param[param["substitute"]["name"]].append(param["value"])
                else:
                    self.scan_param[param["substitute"]["name"]] = [param["value"]]

    def __scan_label(self, parameter):
        param_list = []
        for elem in parameter:
            temp_keys = ",".join(elem["substitute"].values())
            temp_keys += " = %2.4f" % elem["value"]
            param_list.append(temp_keys)
        self.scan_label = ', '.join(param_list)

        return self.scan_label

    def timecourse(self, plot_param, end_time = 'end', title = None):
        fig = plt.figure()
        legendstr = []
        for elem in self.plot_data:
            data = np.transpose(np.array([elem["sweep_data"]["Time"], elem["sweep_data"][plot_param]]))
            elem_index = index(data, end_time)
            legendstr.append(elem["scan_label"])
            p = plt.plot(divlist(elem["sweep_data"]["Time"][0:elem_index], 60), elem["sweep_data"][plot_param][0:elem_index])
        plt.xlabel("Time(mins)", fontsize = 14)
        plt.ylabel("%s Conc (nM)" % plot_param.replace('_', ' '), fontsize = 14)
        if title:
            plt.title(str(title), fontsize = 16)
        plt.tick_params(axis = 'both', which = 'major', labelsize = 12)
        plt.legend(legendstr)
        self.plottext["timecourse"] = ', '.join(legendstr)

        return fig
        

    def integrate(self, data, time_index, norm_value = 1.0):
        """
        Integrates time course data for a particular species
        at a specified time
        data is a N X 2 numpy array containing the time and
        species concentration.
        End time is assumed in hours
        """
        end_time_secs = data[time_index, 0]
        avg = np.trapz(data[0:time_index, 1], x = data[0:time_index, 0])/(norm_value*end_time_secs)

        return avg

    def normalize_data(self, plot_param, normalization = "max", end_time = 'end'):
        """
        Normalizes the data with respect to specified
        parameter and returns the integrated average
        """
        integrated_avg = []
        initial_values = []
            
        if normalization == "control":
            control_data = np.transpose(np.array([self.control_data["Time"], self.control_data[plot_param]]))
            control_index = index(control_data, end_time)
            control_average = self.integrate(control_data, control_index)
            integrated_avg.append(control_average/control_average)
        for ii,elem in enumerate(self.plot_data):
            data = np.transpose(np.array([elem["sweep_data"]["Time"], elem["sweep_data"][plot_param]]))
            elem_index = index(data, end_time)
            if normalization == "max":
                norm_value = np.max(data[0:elem_index, 1])
            elif normalization == "control":
                norm_value = control_average
            else:
                norm_value = 1.0
                
            initial_values.append("%s: %s" % (str(ii + 1), elem["scan_label"]))
            integrated_avg.append(self.integrate(data, elem_index, norm_value = norm_value))

        return integrated_avg, initial_values

    def barplot(self, plot_param, end_time='end', conc_unit = 'nM', normalization = "max", title = None):
        """
        Plots the barplot for specified parameter and end time
        interval
        """
        fig = plt.figure()
        integrated_avg, initial_values = self.normalize_data(plot_param, normalization = normalization, end_time = end_time)
        xval = np.arange(len(integrated_avg))
        p = plt.bar(xval + 1, integrated_avg, tick_label = [elem + 1 for elem in xval], width = 0.35, align = 'center')
        plt.ylabel("%s Conc (%s)" % (plot_param, conc_unit), fontsize = 14)
        plt.xlabel("Scan parameters")
        if title:
            plt.title(str(title), fontsize = 16)
        #plt.text(0.9, 0.9, '\n'.join(initial_values))
        control_str = "(Control)" if normalization == "control" else "" 
        self.plottext["bar"] = initial_values[0] + " " + control_str + ", " + ', '.join(initial_values[1:])

        return fig

    def barsubplot(self, plot_param, end_times = [12,24,48], conc_unit = 'nM', normalization = "max"):
        """
        Creates a subplot containing the figures for three
        time intervals in the same plot
        """
        fig = plt.figure()
        ax = []

        for ii, end_time in enumerate(end_times):
            integrated_avg, initial_values = self.normalize_data(plot_param, normalization = normalization, end_time = end_time)
            xval = np.arange(len(integrated_avg))
            if ii == 0:
                ax.append(plt.subplot(len(end_times), 1, ii + 1))
            else:
                ax.append(plt.subplot(len(end_times), 1, ii + 1, sharex = ax[0]))
            p = plt.bar(xval + 1, integrated_avg, tick_label = [elem + 1 for elem in xval], width = 0.35, align = 'center')
            if ii < len(end_times) - 1:
                plt.setp(ax[ii].get_xticklabels(), visible = False)
            else:
                plt.xticks(xval + 1, ["Control"] + ["%.4f nM" % elem for elem in self.scan_param["Nrg"]], rotation = 45)
                plt.xlabel("Nrg Conc (nM)")

            if ii == 1:
                plt.ylabel("%s Conc (%s)" % (plot_param, conc_unit), fontsize = 14)
            plt.title(str(end_time) + " h", fontsize = 12)
        #plt.tight_layout()

            
        control_str = "(Control)" if normalization == "control" else ""
        self.plottext["barsub"] = initial_values[0] + " " + control_str + ", " + ', '.join(initial_values[1:])

        return fig
    
    def store_figstr(self, fig, plottype, plot_param, end_time = 48):
        """
        Stores an appropriate plot object
        """
        self.plots.setdefault(plot_param, {})
        self.plots[plot_param].setdefault(plottype, {})
        for key in ["pngstr","epstr","scan_label"]:
            self.plots[plot_param][plottype].setdefault(key, {})
        self.plots[plot_param][plottype]["pngstr"][str(end_time) + "h"] = self.__figure_text(fig)
        self.plots[plot_param][plottype]["epstr"][str(end_time) + "h"] = self.__figure_text(fig, filetype = 'eps')
        self.plots[plot_param][plottype]["scan_label"][str(end_time) + "h"] = self.plottext[plottype]
        #self.plots[plot_param][plottype]["fig"] = fig

    def save_fig(self, fig, plot_param, plottype, outdir = "figures", end_time=48):
        """
        Saves the figure object as a file
        """
        pngfile = os.path.join(outdir, "%s_%s_%s_%sh.png" % (plot_param.replace(' ','_'), plottype, self.sweep_id, end_time))
        pdffile = os.path.join(outdir, "%s_%s_%s_%sh.pdf" % (plot_param.replace(' ','_'), plottype, self.sweep_id, end_time))
        fig.savefig(pngfile, bbox_inches="tight")
        #fig.savefig(pdffile, dpi = 300)

    def __figure_text(self, fig, filetype = "png"):
        """
        Converts a matplotlib plot object into string
        representation
        """
        imgdata = StringIO.StringIO()

        fig.savefig(imgdata, format = filetype, bbox_inches="tight")
        imgdata.seek(0)

        if filetype == "png":
            figstr = base64.b64encode(imgdata.read())
        elif filetype == "eps":
            figstr = imgdata.read()
        else:
            raise Exception("Filetype %s not supported" % filetype)

        return figstr

    def save_instance(self, outdir="data"):
        """
        Saves a plot instance as a pickle
        """
        with open(os.path.join(outdir, "Sweep_Instance_%s.pickle" % self.sweep_id), "wb") as fp: pickle.dump(self, fp)

    def save_figstr(self, outdir = "figures"):
        """
        Save the plot figure strings as pickle file
        to enable loading and generate reports
        """
        with open(os.path.join(outdir, "Plot_Figures_%s.pickle" % self.sweep_id), "wb") as fp: pickle.dump({ "sweep_id" : self.sweep_id, "plots" : self.plots }, fp)

    def close_fig(self, fig = "all"):
        """
        Closes the figure object
        """
        plt.close(fig)
        
    def Plotprocess(self, fig, plotparam, plottype, outdir = "figures", end_time = 48):
        """
        Plots specified type of plot and saves plot information
        """
        self.store_figstr(fig, plottype, plotparam, end_time = end_time)
        self.save_fig(fig, plotparam, plottype, end_time = end_time, outdir = outdir)
        self.close_fig(fig) 
            

if __name__ == '__main__':
    execfile("runsweep.py")
    ps = PlotSweep(Input_Data["sweep_id"], sweepers, Input_Data["plot_param"], control_sweep)
    ps.get_data()
    for elem in Input_Data["plot_param"]:
        fig = ps.timecourse(elem)
        ps.Plotprocess(fig, elem, "timecourse")
        fig = ps.barplot(elem, normalization = "control")
        ps.Plotprocess(fig, elem, "bar")
        fig = ps.barsubplot(elem, normalization = "control")
        ps.Plotprocess(fig, elem, "barsub")

    ps.save_figstr()
    
