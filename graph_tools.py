import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import os

#plt.ioff()

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

real_keys = {"taustart",
        "tau_time",
        "f_int",
        "f_int_err",
        "xtrsrc",
        "extract_tpe",
        "id",
        "dataset",
        "wm_ra",
        "wm_decl",
        "band",
        "v_nu",
        "eta_nu",
        "f_datapoints",
        "freq_eff"}
real_values = range(len(real_keys))
real = dict(zip(real_keys, real_values))

#real = {"id": 0, "v_nu": 1, "eta_nu": 2, "max_flux": 3, "avg_flux": 4}

sim = {"id": 0, "eta_nu": 1, "signif": 2, "v_nu": 2,
       "flux": 3, "flux_ratio": 4, "dpts": 5,
       "RA": 6, "dec": 7, "trans_type": 8}

def get_data(db_host, db_name, username, password):
    con = None
    con = connect(dbname=db_name, user=username, host=db_host, password=password)

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    sql_str = """\
    SELECT  im.taustart_ts
            ,im.tau_time
            ,ex.f_int
            ,ex.f_int_err
            ,ax.xtrsrc
            ,ex.extract_type
            ,rc.id as runcatid
            ,rc.dataset
            ,rc.wm_ra
            ,rc.wm_decl
            ,im.band
            ,ax.v_int
            ,ax.eta_int
            ,ax.f_datapoints
            ,im.freq_eff
    FROM extractedsource ex
         ,assocxtrsource ax
         ,image im
         ,runningcatalog rc
         ,runningcatalog_flux rf
    WHERE rf.runcat = rc.id
      and ax.runcat = rc.id
      AND ax.xtrsrc = ex.id
      and ex.image = im.id
      AND rc.dataset = %s
      ORDER BY rc.id
    """ % "1"
    cur.execute(sql_str)

    data = cur.fetchall()

    return data


def get_sim_data(filename):
    # get the simulated data from a file named filename
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, "sim", filename), 'r') as f:
        data = f.readl()

    # split the data into an array with each line being an element and then split again around the comma
    data = data.split('\n')
    data = data[1:-1]
    data = [datum.split(',') for datum in data]

    return data


def create_graph_v_vs_eta(data, outputname, inc_simulated=False):
    fig, ax = plt.subplots()
    legend = []
    print "Beginning to plot %d sources." % len(data)

    x = []
    y = []

    marker_size = 8
    for source in data:
        x.append(source[real["eta_nu"]])
        y.append(source[real["v_nu"]])

    legend.append(ax.scatter(x, y, s=marker_size, color="gray" if inc_simulated else "blue"))

    print "Plotted %d sources." % len(data)

    if inc_simulated:
        sim_sources = ['sim_fred_trans_data.txt', 'sim_gaussian_trans_data.txt',
                       'sim_periodic_trans_data.txt', 'sim_single_flare_trans_data.txt',
                       'sim_slow_fall_trans_data.txt', 'sim_slow_rise_trans_data.txt',
                       'sim_turn_off_trans_data.txt', 'sim_turn_on_trans_data.txt']

        sim_colors = ['#0019A6', '#0A37CC', '#107BE6', '#05D5FF',
                      '#8FECFF', '#48FF00', 'orange', 'red']

        num_sources = len(sim_sources)
        for i in range(num_sources):
            sim_data = get_sim_data(sim_sources[i])
            x = []
            y = []

            print "Plotting simulated sources from %s now." % sim_sources[i]
            for source in sim_data:
                x.append(source[sim["eta_nu"]])
                y.append(source[sim["v_nu"]])
            legend.append(ax.scatter(x, y, s=marker_size, color=sim_colors[i]))

    ax.legend(tuple([entry for entry in legend]),
              ('real data', 'fred', 'gaussian', 'periodic', 'single flare',
               'slow fall', 'slow rise', 'turn off', 'turn on'),
              scatterpoints=3,
              loc='lower right',
              ncol=1,
              fontsize=8)

    ax.set_xlabel(r'$\eta_\nu$', fontsize=20)
    ax.set_ylabel(r'$V_\nu$', fontsize=20)
    #ax.set_title(r'$\eta_\nu$ vs $V_\nu$')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.axis([10**-9,10**7,10**-6,10**1])
    ax.grid(True)

    fig.set_size_inches(7, 7)
    fig.tight_layout()
    plt.savefig(outputname, dpi=300)


def create_graph_max_flux_vs_eta(data, outputname, inc_simulated=False):
    fig, ax = plt.subplots()
    legend = []
    print "Beginning to plot %d sources." % len(data)

    marker_size = 8
    x = []
    y = []
    for source in data:
        x.append(source[real["max_flux"]])
        y.append(source[real["eta_nu"]])

    legend.append(ax.scatter(x, y, s=marker_size, color="gray" if inc_simulated else "blue"))

    print "Plotted %d sources." % len(data)

    if inc_simulated:
        sim_sources = ['sim_fred_trans_data.txt', 'sim_gaussian_trans_data.txt',
                       'sim_periodic_trans_data.txt', 'sim_single_flare_trans_data.txt',
                       'sim_slow_fall_trans_data.txt', 'sim_slow_rise_trans_data.txt',
                       'sim_turn_off_trans_data.txt', 'sim_turn_on_trans_data.txt']

        sim_colors = ['#0019A6', '#0A37CC', '#107BE6', '#05D5FF',
                      '#8FECFF', '#48FF00', 'orange', 'red']

        num_sources = len(sim_sources)
        for i in range(num_sources):
            sim_data = get_sim_data(sim_sources[i])
            x = []
            y = []
            print "Plotting simulated sources from %s now." % sim_sources[i]
            for source in sim_data:
                x.append(source[sim["flux"]])
                y.append(source[sim["eta_nu"]])

            legend.append(ax.scatter(x, y, s=marker_size, color=sim_colors[i]))

    ax.legend(tuple([entry for entry in legend]),
              ('real data', 'fred', 'gaussian', 'periodic', 'single flare',
               'slow fall', 'slow rise', 'turn off', 'turn on'),
              scatterpoints=3,
              loc='lower right',
              ncol=1,
              fontsize=8)

    ax.set_xlabel(r'Max Flux (Jy)', fontsize=20)
    ax.set_ylabel(r'$\eta_\nu$', fontsize=20)
    #ax.set_title(r'$\eta_\nu$ vs $V_\nu$')
    ax.set_xscale('log')
    ax.set_yscale('log')
    #ax.axis([10**-9,10**7,10**-6,10**1])
    ax.grid(True)

    fig.set_size_inches(7, 7)
    fig.tight_layout()
    plt.savefig(outputname, dpi=300)

def create_diag_plots(data, filename, inc_simulated=False):

    nullfmt = mpl.ticker.NullFormatter()

    fig = plt.figure(1, figsize=(12,12))
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    fig.subplots_adjust(hspace=0.001, wspace=0.001)

    ax1.set_ylabel(r'$\eta_\nu$', fontsize=28)
    ax3.set_ylabel(r'$V_\nu$', fontsize=28)
    ax3.set_xlabel('Max Flux (Jy)', fontsize=24)
    ax4.set_xlabel('Max Flux / Average Flux', fontsize=24)

    legend = []
    print "Beginning to plot %d sources." % len(data)
    x3_range = [0,0]
    x4_range = [0,0]
    y1_range = [0,0]
    y3_range = [0,0]
    marker_size = 8
    x3 = []
    x4 = []
    y1 = []
    y3 = []
    for source in data:
        x3.append(source[real["max_flux"]])
        x4.append(source[real["max_flux"]]/source[real["avg_flux"]])
        y1.append(source[real["eta_nu"]])
        y3.append(source[real["v_nu"]])

    legend.append(ax1.scatter(x3, y1, s=marker_size, color="gray" if inc_simulated else "blue"))
    ax2.scatter(x4, y1, s=marker_size, color="gray" if inc_simulated else "blue")
    ax3.scatter(x3, y3, s=marker_size, color="gray" if inc_simulated else "blue")
    ax4.scatter(x4, y3, s=marker_size, color="gray" if inc_simulated else "blue")

    x3_range[0] = min(x3)
    x3_range[1] = max(x3)
    x4_range[0] = min(x4)
    x4_range[1] = max(x4)
    y1_range[0] = min(y1)
    y1_range[1] = max(y1)
    y3_range[0] = min(y3)
    y3_range[1] = max(y3)

    print "Plotted %d sources." % len(data)

    if inc_simulated:
        sim_sources = ['sim_fred_trans_data.txt', 'sim_gaussian_trans_data.txt',
                       'sim_periodic_trans_data.txt', 'sim_single_flare_trans_data.txt',
                       'sim_slow_fall_trans_data.txt', 'sim_slow_rise_trans_data.txt',
                       'sim_turn_off_trans_data.txt', 'sim_turn_on_trans_data.txt']

        sim_colors = ['#0019A6', '#0A37CC', '#107BE6', '#05D5FF',
                      '#8FECFF', '#48FF00', 'orange', 'red']

        num_sources = len(sim_sources)
        for i in range(num_sources):
            sim_data = get_sim_data(sim_sources[i])
            x3 = []
            x4 = []
            y1 = []
            y3 = []
            print "Plotting simulated sources from %s now." % sim_sources[i]
            for source in sim_data:
                x3.append(source[sim["flux"]])
                x4.append(source[sim["flux_ratio"]])
                y1.append(source[sim["eta_nu"]])
                y3.append(source[sim["v_nu"]])

            legend.append(ax1.scatter(x3, y1, s=marker_size, color=sim_colors[i]))
            ax2.scatter(x4, y1, s=marker_size, color=sim_colors[i])
            ax3.scatter(x3, y3, s=marker_size, color=sim_colors[i])
            ax4.scatter(x4, y3, s=marker_size, color=sim_colors[i])

            if min(x3) < x3_range[0]:
                x3_range[0] = min(x3)
            if max(x3) > x3_range[1]:
                x3_range[1] = max(x3)

            if min(x4) < x4_range[0]:
                x4_range[0] = min(x4)
            if max(x4) > x4_range[1]:
                x4_range[1] = max(x4)

            if min(y1) < y1_range[0]:
                y1_range[0] = min(y1)
            if max(y1) > y1_range[1]:
                y1_range[1] = max(y1)

            if min(y3) < y3_range[0]:
                y3_range[0] = min(y3)
            if max(y3) > y3_range[1]:
                y3_range[1] = max(y3)


    ax4.legend(tuple([entry for entry in legend]),
               ('real data', 'fred', 'gaussian', 'periodic', 'single flare',
                'slow fall', 'slow rise', 'turn off', 'turn on'),
               scatterpoints=3, loc='lower right', ncol=1, fontsize=8)


    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xscale('log')
    ax3.set_yscale('log')
    ax3.set_xscale('log')
    ax4.set_yscale('log')
    ax4.set_xscale('log')
    # ax1.set_ylim(float(y1_range[0])-0.5,float(y1_range[1])+1.)
    # ax3.set_ylim(float(y3_range[0])-0.5,float(y3_range[1])+1.)
    # ax3.set_xlim(float(x3_range[0])-1,float(x3_range[1])+1)
    # ax4.set_xlim(float(x4_range[0])-0.1,float(x4_range[1])+1.)
    #
    # ax1.set_xlim(ax3.get_xlim())
    # ax4.set_ylim(ax3.get_ylim())
    # ax2.set_xlim(ax4.get_xlim())
    # ax2.set_ylim(ax1.get_ylim())


    ax1.set_ylim(10**-9, 10**7)
    ax2.set_ylim(10**-9, 10**7)
    ax3.set_ylim(10**-6, 10**1)
    ax4.set_ylim(10**-6, 10**1)

    ax2.set_xlim(0.8, 10**2)
    ax4.set_xlim(0.8, 10**2)

    print "limits"

    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    username = ''
    password = ''
    host = 'vlo.science.uva.nl'
    db_name = ''

    #print get_sim_data("sim_single_flare_trans_data.txt")

    data = get_data(host, db_name, username, password)

    #create_graph_v_vs_eta(data, "v_vs_eta.png", True)
    #create_graph_max_flux_vs_eta(data, "max_flux_vs_eta.png", True)
    #create_diag_plots(data, "diag_plots.png", True)
    create_diag_plots(data, "diag_plots_nosim.png", False)
