# -*- coding: utf-8 -*-

import abc

import numpy as np

from astropy import units

from skylab.physics.flux import FluxModel


def get_conversion_factor_to_internal_flux_unit(fluxmodel):
    """Calculates the unit conversion factor for converting the used flux
    unit of the given flux model into the skylab internally used flux unit
    1/(GeV cm2 s).

    Parameters
    ----------
    fluxmodel : FluxModel
        The flux model instance for which to calculate the unit conversion
        factor.

    Returns
    -------
    unit_conversion_factor : float
        The unit conversion factor.
    """
    unit_conversion_factor = (1./fluxmodel.energy_unit * 1./fluxmodel.length_unit**2 * 1./fluxmodel.time_unit).to(1./units.GeV * 1./units.cm**2 * 1./units.s).value
    return unit_conversion_factor


class DetSigEffImplMethod(object):
    """Abstract base class for an implementation method of a detector signal
    efficiency. It defines the interface of a detector signal efficiency
    implementation to interact with the DetSigEff class.
    This class provides a caching mechanism.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.supported_fluxmodels = ()

    @property
    def supported_fluxmodels(self):
        return self._supported_fluxmodels
    @supported_fluxmodels.setter
    def supported_fluxmodels(self, models):
        if(not isinstance(models, tuple)):
            raise TypeError('The supported_fluxmodels property must be of type tuple!')
        self._supported_fluxmodels = models

    def supports_fluxmodel(self, fluxmodel):
        """Checks if the given flux model is supported by this detector signal
        efficiency implementation method.
        """
        for sfm in self.supported_fluxmodels:
            if(isinstance(fluxmodel, sfm)):
                return True
        return False

    @abc.abstractmethod
    def construct(self, data_mc, fluxmodel, livetime):
        """Abstract method to construct the detector signal efficiency.
        This method must be called by the derived class method implementation
        to ensure the compatibility check of the given flux model with the
        supported flux models.

        Parameters
        ----------
        data_mc : ndarray
            The numpy record ndarray holding the monte-carlo event data.
        fluxmodel : FluxModel
            The flux model instance. Must be an instance of FluxModel.
        livetime : float
            The live-time in days to use for the detector signal efficiency.
        """
        if(not self.supports_fluxmodel(fluxmodel)):
            raise TypeError('The DetSigEffImplMethod "%s" does not support the flux model "%s"!'%(self.__class__.__name__, fluxmodel.__class__.__name__))

    @abc.abstractmethod
    def get(self, src_pos, src_flux_params):
        """Abstract method to receive the detector signal efficiency values for
        an array of given sources, given by their source position and source
        flux parameters.

        Parameters
        ----------
        src_pos : numpy record ndarray
            The numpy record array containing the position of the signal
            sources. The required fields of this record array are implementation
            method dependent. But in the most generic case, it must contain the
            following three fields: ra, dec, time.
        src_flux_params : dict
            The dictionary with the flux parameters of the sources. It is
            assumed that the flux parameters are the same for all requested
            sources.
        """
        pass


class DetectorSignalEfficiency(object):
    """This is the detector signal efficiency class.

    To construct a detector signal efficiency object, four ingredients are
    needed: the monte-carlo data events, a signal flux model, the live time, and
    an implementation method that knows howto contruct the actual detector
    efficiency in an efficient way. In general, the implementation method
    depends on the detector, the flux model, and the flux model's signal
    parameters. Hence, for a given detector and flux model, an appropriate
    implementation method needs to be chosen.
    """
    def __init__(self, data_mc, fluxmodel, livetime, implmethod):
        """Constructs a new detector signal efficiency object. It takes
        the monte-carlo data events, a flux model of the signal, and the live
        time to compute the detector signal efficiency.

        Parameters
        ----------
        data_mc : ndarray
            The numpy record ndarray holding the monte-carlo event data.
        fluxmodel : FluxModel
            The flux model instance. Must be an instance of FluxModel.
        livetime : float
            The live-time to use for the detector signal efficiency. Must be
            given in the time unit of the flux model.
        implmethod : DetSigEffImplMethod
            The implementation method to use for constructing and receiving
            the detector signal efficiency. The appropriate method depends on
            the used flux model.
        """
        self.data_mc = data_mc
        self.fluxmodel = fluxmodel
        self.livetime = livetime
        self.implmethod = implmethod

        # Construct the detector signal efficiency.
        self._implmethod.construct(self._data_mc, self._fluxmodel, self._livetime)

    @property
    def data_mc(self):
        """The monte-carlo data events, which should be used to calculate the
        detector signal efficiency.
        """
        return self._data_mc
    @data_mc.setter
    def data_mc(self, data):
        if(not isinstance(data, np.ndarray)):
            raise TypeError('The data_mc property must be of type numpy.ndarray!')
        self._data_mc = data

    @property
    def fluxmodel(self):
        """The flux model, which should be used to calculate the detector
        signal efficiency.
        """
        return self._fluxmodel
    @fluxmodel.setter
    def fluxmodel(self, model):
        if(not isinstance(model, FluxModel)):
           raise TypeError('The fluxmodel property must be an instance of FluxModel!')
        self._fluxmodel = model

    @property
    def livetime(self):
        """The live-time in days.
        """
        return self._livetime
    @livetime.setter
    def livetime(self, lt):
        if(not isinstance(lt, float)):
            raise TypeError('The livetime property must be of type float!')
        self._livetime = lt

    @property
    def implmethod(self):
        return self._implmethod
    @implmethod.setter
    def implmethod(self, method):
        if(not isinstance(method, DetSigEffImplMethod)):
            raise TypeError('The implmethod property must be an instance of DetSigEffImplMethod!')
        self._implmethod = method

    def __call__(self, src_pos, src_flux_params):
        """Retrieves the detector signal efficiency for the given source
        position and source flux parameters.

        Parameters
        ----------
        src_pos : numpy record ndarray
            The numpy record array containing the position of the signal
            sources. The required fields of this record array are implementation
            method dependent. But in the most generic case, it must contain the
            following three fields: ra, dec, time.

        src_flux_params : dict
            The dictionary with the flux parameters of the sources. It is
            assumed that the flux parameters are the same for all requested
            sources.

        Returns
        -------
        detsigeff : 1d ndarray
            The array with the detector signal efficiency value for each given
            source.
        """
        return self._implmethod.get(src_pos, src_flux_params)