# -*- coding: utf-8 -*-
# Author: Dr. Martin Wolf <mail@martin-wolf.org>

import numpy as np

from skyllh.datasets.i3 import (
    PublicData_10y_ps,
)


def create_dataset_collection(
        cfg,
        base_path=None,
        sub_path_fmt=None,
):
    """Defines the dataset collection for IceCube's 10-year
    point-source public data, which is available at
    http://icecube.wisc.edu/data-releases/20210126_PS-IC40-IC86_VII.zip, and
    adds monte-carlo files.

    Parameters
    ----------
    cfg : instance of Config
        The instance of Config holding the local configuration.
    base_path : str | None
        The base path of the data files. The actual path of a data file is
        assumed to be of the structure <base_path>/<sub_path>/<file_name>.
        If None, use the default path ``cfg['repository']['base_path']``.
    sub_path_fmt : str | None
        The sub path format of the data files of the public data sample.
        If None, use the default sub path format
        'icecube_10year_ps'.

    Returns
    -------
    dsc : DatasetCollection
        The dataset collection containing all the seasons as individual
        I3Dataset objects.
    """
    dsc = PublicData_10y_ps.create_dataset_collection(
        cfg=cfg,
        base_path=base_path,
        sub_path_fmt=sub_path_fmt)

    (
        IC40,
        IC59,
        IC79,
        IC86_I,
        IC86_II,
        IC86_III,
        IC86_IV,
        IC86_V,
        IC86_VI,
        IC86_VII,
        IC86_II_VII,
    ) = dsc.get_datasets((
        'IC40',
        'IC59',
        'IC79',
        'IC86_I',
        'IC86_II',
        'IC86_III',
        'IC86_IV',
        'IC86_V',
        'IC86_VI',
        'IC86_VII',
        'IC86_II-VII',
    ))
    IC40.mc_pathfilename_list = 'sim/IC40_MC.npy'
    IC59.mc_pathfilename_list = 'sim/IC59_MC.npy'
    IC79.mc_pathfilename_list = 'sim/IC79_MC.npy'
    IC86_I.mc_pathfilename_list = 'sim/IC86_I_MC.npy'
    IC86_II.mc_pathfilename_list = 'sim/IC86_II-VII_MC.npy'
    IC86_III.mc_pathfilename_list = IC86_II.mc_pathfilename_list
    IC86_IV.mc_pathfilename_list = IC86_II.mc_pathfilename_list
    IC86_V.mc_pathfilename_list = IC86_II.mc_pathfilename_list
    IC86_VI.mc_pathfilename_list = IC86_II.mc_pathfilename_list
    IC86_VII.mc_pathfilename_list = IC86_II.mc_pathfilename_list
    IC86_II_VII.mc_pathfilename_list = IC86_II.mc_pathfilename_list

    def add_run_number_mc(data):
        mc = data.mc
        mc.append_field('run', np.repeat(0, len(mc)))

    def add_time(data):
        mc = data.mc
        mc.append_field('time', np.repeat(0, len(mc)))

    def add_azimuth_and_zenith(data):
        mc = data.mc
        mc.append_field('azi', np.repeat(0, len(mc)))
        mc.append_field('zen', np.repeat(0, len(mc)))

    dsc.add_data_preparation(add_run_number_mc)
    dsc.add_data_preparation(add_time)
    dsc.add_data_preparation(add_azimuth_and_zenith)

    return dsc
