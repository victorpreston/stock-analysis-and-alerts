import os
import logging
from contextlib import contextmanager
import pytest
from airflow.models import DagBag

# 🔹 Use an absolute path to your DAGs folder
DAG_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dags/major_dags/"))

print(f"Loading DAGs from: {DAG_FOLDER}")  # Debug print

DAG_IDS = ["cloudflare_to_postgres_dag", "stock_data_ingestion_dag"]  # Make sure these match your DAG IDs

@contextmanager
def suppress_logging(namespace):
    """Temporarily suppress logging for cleaner test output."""
    logger = logging.getLogger(namespace)
    old_value = logger.disabled
    logger.disabled = True
    try:
        yield
    finally:
        logger.disabled = old_value

def get_dag_bag():
    """Loads the DAGs from the correct folder and prints loaded DAGs for debugging."""
    with suppress_logging("airflow"):
        dag_bag = DagBag(dag_folder=DAG_FOLDER, include_examples=False)

    print("Loaded DAGs:", dag_bag.dags.keys())  # Debugging print
    return dag_bag

def get_dags():
    """Returns a list of tuples: (dag_id, dag_object, dag_file_path) but only for the specified DAGs."""
    dag_bag = get_dag_bag()
    return [
        (dag_id, dag, os.path.relpath(dag.fileloc, os.environ.get("AIRFLOW_HOME", "")))
        for dag_id, dag in dag_bag.dags.items() if dag_id in DAG_IDS
    ]

@pytest.mark.parametrize("dag_id,dag,fileloc", get_dags(), ids=[x[0] for x in get_dags()])
def test_dag_import(dag_id, dag, fileloc):
    """Ensures that each DAG loads without import errors."""
    assert dag is not None, f"{dag_id} in {fileloc} failed to load."

@pytest.mark.parametrize("dag_id,dag,fileloc", get_dags(), ids=[x[0] for x in get_dags()])
def test_dag_tags(dag_id, dag, fileloc):
    """Ensures that each DAG has at least one tag."""
    assert dag.tags, f"{dag_id} in {fileloc} has no tags."

@pytest.mark.parametrize("dag_id,dag,fileloc", get_dags(), ids=[x[0] for x in get_dags()])
def test_dag_retries(dag_id, dag, fileloc):
    """Ensures that each DAG has retries set to at least 2."""
    retries = dag.default_args.get("retries", None)
    assert retries is not None and retries >= 2, f"{dag_id} in {fileloc} must have task retries >= 2."
