"""Single-scenario entry point for REAP / PREP-SHOT.

Reads ``config.json`` and ``params.json``, loads the input set in the
configured folder (overridable with ``-i``/``--input_folder``), builds and
solves the optimisation model, and writes results to
``<output_folder>/<output_filename>.nc``.
"""

import logging
import os
from os import path, makedirs

from prepshot.load_data import load_json, get_required_config_data, load_data
from prepshot.logs import setup_logging, log_parameter_info
from prepshot.model import create_model
from prepshot.parameters import parse_arguments
from prepshot.solver import build_solver, solve_model
from prepshot.utils import extract_result, update_output_filename

CONFIG_FILENAME = 'config.json'
PARAMS_FILENAME = 'params.json'


def setup(params_data, args):
    """Load data and prepare the output folder; return (parameters, output_filename)."""
    config_data = load_json(CONFIG_FILENAME)
    required_config_data = get_required_config_data(config_data)

    filepath = path.dirname(path.abspath(__file__))
    input_filename = args.input_folder or str(
        config_data['general_parameters']['input_folder']
    )
    input_filepath = path.join(filepath, input_filename)

    for param in params_data.keys():
        value = getattr(args, param)
        if value is not None:
            params_data[param]["file_name"] = (
                params_data[param]["file_name"] + f"_{value}"
            )

    parameters = load_data(params_data, input_filepath)
    parameters.update(required_config_data)

    output_folder = path.join(
        '.', str(config_data['general_parameters']['output_folder'])
    )
    if not path.exists(output_folder):
        makedirs(output_folder)
        logging.warning("Folder %s created", output_folder)

    output_filename = path.join(
        output_folder, str(config_data['general_parameters']['output_filename'])
    )
    return parameters, output_filename


def run_model(parameters, output_filename, args):
    """Build and solve the model; write netCDF output if solved."""
    model = create_model(parameters)
    output_filename = update_output_filename(output_filename, args)
    solver = build_solver(parameters)
    if solve_model(model, solver, parameters):
        ds = extract_result(model, isinflow=parameters['isinflow'])
        ds.to_netcdf(f'{output_filename}.nc')
        logging.info("Results are written to %s.nc", output_filename)


def main():
    params_data = load_json(PARAMS_FILENAME)
    params_list = [params_data[key]["file_name"] for key in params_data]
    args = parse_arguments(params_list)

    config_data = load_json(CONFIG_FILENAME)
    setup_logging()
    log_parameter_info(config_data)

    parameters, output_filename = setup(params_data, args)
    run_model(parameters, output_filename, args)


if __name__ == "__main__":
    main()
