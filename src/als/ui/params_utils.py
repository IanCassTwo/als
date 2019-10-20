"""
Provide logic for mapping processing params < = > GUI controls
"""
import logging
from typing import List

from PyQt5.QtWidgets import QWidget, QSlider

from als.code_utilities import AlsException, log
from als.model.params import ProcessingParameter, RangeParameter

_LOGGER = logging.getLogger(__name__)

_DEFAULT_SLIDER_MAX = 4096


class UnsupportedParamMapping(AlsException):
    """Raised when trying to work on incompatible couple param / control"""


@log
def _check_param_control_pairing(param: ProcessingParameter, control: QWidget):
    """

    Raise an exception if we cannot match this param / control pair

    :param param: The parameter to check
    :type param: ProcessingParameter

    :param control: the control to check
    :type control: QWidget

    :raises UnsupportedParamMapping: param/control pair is not supported
    """

    if not (isinstance(param, RangeParameter) and isinstance(control, QSlider)):

        raise UnsupportedParamMapping("Unsupported parameter / control pair",
                                      f"No recipe for couple {type(param)}/{type(control)}")


@log
def _update_control_from_param(param: ProcessingParameter, control: QWidget):
    """

    Generic function to update a GUI control from a processing parameter

    :param param: The source parameter
    :type param: ProcessingParameter

    :param control: the control to update
    :type control: QWidget
    """

    _check_param_control_pairing(param, control)

    setters_dict = {

        QSlider: control.setValue
    }

    getters_dict = {

        RangeParameter: lambda p: p.value / p.maximum * _DEFAULT_SLIDER_MAX
    }

    # set control value according to param value
    control_value_setter_function = setters_dict[type(control)]
    param_value_transformation_function = getters_dict[type(param)]

    control_value_setter_function(param_value_transformation_function(param))

    # set control tooltip as param description
    control.setToolTip(param.description)


@log
def _update_param_from_control(param: ProcessingParameter, control: QWidget):
    """

    Generic function to update a processing parameter from a GUI control

    :param param: The destination parameter
    :type param: ProcessingParameter

    :param control: the source control
    :type control: QWidget
    """

    _check_param_control_pairing(param, control)

    getters_dict = {

        QSlider: control.value
    }

    value_transformations_dict = {

        RangeParameter: lambda p, v: v / _DEFAULT_SLIDER_MAX * p.maximum
    }

    # set param value according to control value
    control_value_getter_function = getters_dict[type(control)]
    param_value_transformation_function = value_transformations_dict[type(param)]

    param.value = param_value_transformation_function(param, control_value_getter_function())

    _LOGGER.debug(f"New value for {param.name} : {param.value}")


@log
def update_params_from_controls(params: List[ProcessingParameter], controls: List[QWidget]):
    """
    Update a list of processing parameters from a matched list of GUI controls

    :param params: the param list
    :type params: List[ProcessingParameter]

    :param controls: the control list
    :type controls: List[QWidget]
    """

    for param, control in zip(params, controls):
        _update_param_from_control(param, control)


@log
def update_controls_from_params(params: List[ProcessingParameter], controls: List[QWidget]):
    """
    Update a list of GUI controls from a matched list of processing parameters

    :param params: the param list
    :type params: List[ProcessingParameter]

    :param controls: the control list
    :type controls: List[QWidget]
    """
    for param, control in zip(params, controls):
        _update_control_from_param(param, control)


@log
def reset_params(params: List[ProcessingParameter], controls: List[QWidget]):
    """
    Reset a list of ProcessingParameter and update associated controls

    :param params: the param list
    :type params: List[ProcessingParameter]

    :param controls: the control list
    :type controls: List[QWidget]
    """

    for param in params:
        param.reset()
        update_controls_from_params(params, controls)
