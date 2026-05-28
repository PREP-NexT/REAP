"""MPI batch driver for REAP / PREP-SHOT.

Like ``run_batch_seriel.py`` but uses ``mpi4py`` for rank assignment. Launch
with ``mpirun -n <N> python run_batch.py``; each rank takes scenarios where
``i % size == rank``. Scenarios with an existing ``year.nc`` (and ``.xlsx``)
are skipped, so the batch is resumable.

For single-node multi-GPU runs without MPI, prefer ``run_batch_seriel.py``
with the ``RANK``/``WORLD`` environment variables.
"""

import logging
import os
import re
import socket
from os import path, makedirs

from mpi4py import MPI

from prepshot.load_data import load_json, get_required_config_data, load_data
from prepshot.logs import setup_logging, log_parameter_info
from prepshot.model import create_model
from prepshot.parameters import parse_arguments
from prepshot.solver import build_solver, solve_model
from prepshot.utils import extract_result, update_output_filename

CONFIG_FILENAME = 'config.json'
PARAMS_FILENAME = 'params.json'
INPUT_FOLDER = 'generated_inputs'
OUTPUT_FOLDER = 'output_batch'

comm = MPI.COMM_WORLD


def _scenario_sort_key(name):
    m = re.search(r'_s(\d+)_', name)
    return (0, int(m.group(1))) if m else (1, name)


def setup_batch(params_data, args, filename, batch_flag):
    """Load configuration and parameters for one scenario."""
    config_data = load_json(CONFIG_FILENAME)
    required_config_data = get_required_config_data(config_data)

    filepath = path.dirname(path.abspath(__file__))
    input_filepath = path.join(filepath, INPUT_FOLDER, filename)

    if batch_flag == 0:
        for param in params_data.keys():
            value = getattr(args, param)
            if value is not None:
                params_data[param]["file_name"] = (
                    params_data[param]["file_name"] + f"_{value}"
                )

    parameters = load_data(params_data, input_filepath)
    parameters.update(required_config_data)

    output_subfolder = filename.replace('input', 'output')
    output_folder = path.join('.', OUTPUT_FOLDER, output_subfolder)
    if not path.exists(output_folder):
        makedirs(output_folder)
        logging.warning("Folder %s created", output_folder)

    output_filename = path.join(
        output_folder, str(config_data['general_parameters']['output_filename'])
    )
    return parameters, output_filename


def run_model(parameters, output_filename, args):
    """Build and solve one scenario; write netCDF output if solved."""
    model = create_model(parameters)
    output_filename = update_output_filename(output_filename, args)
    solver = build_solver(parameters)
    if not solve_model(model, solver, parameters):
        return
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

    rank = comm.Get_rank()
    size = comm.Get_size()
    hostname = socket.gethostname()

    makedirs("log", exist_ok=True)
    mpi_log_file = os.path.join("log", f"rank_{rank:03d}.log")

    inputs = sorted(
        [f for f in os.listdir(INPUT_FOLDER) if f.startswith('input')],
        key=_scenario_sort_key,
    )

    batch_flag = 0
    with open(mpi_log_file, "a") as f:
        for i, scenario in enumerate(inputs):
            if i % size != rank:
                continue

            f.write(f"Rank {rank}/{size} on {hostname}: scenario {scenario}\n")
            f.flush()

            parameters, output_filename = setup_batch(
                params_data, args, scenario, batch_flag
            )

            if path.exists(f'{output_filename}.nc'):
                f.write(f"Rank {rank} skipped {scenario} (existing results)\n")
                f.flush()
                continue

            run_model(parameters, output_filename, args)
            batch_flag = 1
            del parameters, output_filename
            f.write(f"Rank {rank} finished {scenario}\n")
            f.flush()

    comm.Barrier()


if __name__ == "__main__":
    main()
