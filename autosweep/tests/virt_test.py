from autosweep.tests.abs_test import AbsTest
from typing import TYPE_CHECKING
from time import sleep
import numpy as np

from autosweep import sweep
if TYPE_CHECKING:
    from pathlib import Path
    from autosweep.instruments.instrument_manager import InstrumentManager
    from autosweep.exec_helpers.reporter import ResultsHold
    from autosweep.data_types.metadata import DUTInfo


class VirtualTest(AbsTest):
    """
    A virtual test, which can be used to exercise the TestExec functionality.
    """

    def __init__(self, dut_info: 'DUTInfo', results: 'ResultsHold', save_path: 'Path'):
        """

        :param dut_info: The information about the device-under-test
        :type dut_info: autosweep.utils.data_types.metadata.DUTInfo
        :param results: Any test results generated by the test are held in this object
        :type results: autosweep.utils.exec_helpers.reporter.ResultsHold
        :param save_path: The path to the folder in which any generated files, like raw data will be saved.
        :type save_path: pathlib.Path
        """
        super().__init__(dut_info=dut_info, results=results, save_path=save_path)
        self.logger.info("Initializing the virtual test")

    def run_acquire(self, instr_mgr: 'InstrumentManager'):
        """
        Generates data for an IV sweep of a 10-ohm and 20-ohm resistor. Does not need any actual instruments.

        :param instr_mgr: An instrument manager with the appropriate instruments
        :type instr_mgr: autosweep.instruments.instrument_manager.InstrumentManager
        :return: None
        """
        self.logger.info("Running the virtual test")

        v = np.linspace(-1, 1, 21)

        traces = {'v': v, 'i0': v/10, 'i1': v/20}
        attrs = {'v': ("Voltage", "V"), 'i0': ("Current", "A"), 'i1': ("Current", "A")}

        s = sweep.Sweep(traces=traces, attrs=attrs)
        sleep(2)

        self.save_data(sweeps={'iv': s}, metadata=None)

    def run_analysis(self, report_headings: list):
        """
        Plots the IV sweep data and reports out the resistance measured in the specs.

        :param report_headings: A collection of headings used in the HTML report
        :type report_headings: list
        :return: None
        """
        self.load_data()
        self.logger.info("Running the virtual analysis")

        iv = self.sweeps['iv']

        fig_hdlr = sweep.FigHandler()
        ax = fig_hdlr.ax
        for col, x, y in iv.itercols():
            ax.plot(x, y, label=col)

        ax.legend()
        labels = iv.get_axis_labels()
        ax.set_xlabel(labels['v'])
        ax.set_ylabel(labels['i0'])

        fig_hdlr.save_fig(path=self.save_path / 'iv.png')

        report_heading = report_headings[0]
        info = {"a": "hello world"}
        self.results.add_spec(report_heading=report_heading, spec='resist_i0', unit='ohm', value=10)
        self.results.add_spec(report_heading=report_heading, spec='resist_i1', unit='ohm', value=20)
        self.results.add_report_entry(report_heading=report_heading, fig_hdlr=fig_hdlr, info=info)