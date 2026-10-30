"""Notebook helpers for Bayesian workflows (sampling / cache)."""

from __future__ import annotations

import os

import arviz as az
import pymc as pm


def load_idata_or_sample(
    model: pm.Model,
    filename: str,
    force_run: bool = False,
    **sample_options,
) -> az.InferenceData:
    """
    Run ``pm.sample`` and save NetCDF, or load existing ``InferenceData`` from disk.

    If ``filename`` exists and ``force_run`` is False, loads with ``az.from_netcdf``.
    Otherwise samples, then writes with ``az.to_netcdf`` (matches CultureWar
    ``notebooks/model_utils.load_idata_or_sample``).

    Parameters
    ----------
    model
        Active PyMC model (must match the model used to produce ``filename``).
    filename
        Path to ``.nc`` file.
    force_run
        If True, sample even when ``filename`` exists.
    **sample_options
        Passed to ``pm.sample`` (e.g. ``nuts_sampler='nutpie'``, ``draws=``, ``tune=``).
    """
    if os.path.exists(filename) and not force_run:
        idata = az.from_netcdf(filename)
        print(f"Loaded InferenceData from {filename}")
        return idata

    with model:
        idata = pm.sample(**sample_options)
    az.to_netcdf(idata, filename)
    print(f"Saved new InferenceData to {filename}")
    return idata
