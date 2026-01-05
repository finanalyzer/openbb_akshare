import os
import logging
import pytest
from dotenv import load_dotenv
from mysharelib.tools import setup_logger, normalize_symbol
from openbb_akshare import project_name


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    setup_logger(project_name)


@pytest.fixture
def logger():
    return logging.getLogger(__name__)


@pytest.fixture
def akshare_api_key():
    load_dotenv() 
    akshare_api_key = os.environ.get("AKSHARE_API_KEY")
    if akshare_api_key is None:
        raise ValueError("AKSHARE_API_KEY environment variable not set.")
    return akshare_api_key


@pytest.fixture
def default_provider():
    return "akshare"
