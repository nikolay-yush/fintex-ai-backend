import os

os.environ["ENV_STATE"] = "test"

from tests.helpers.validate_test_env import validate_test_env


validate_test_env()

pytest_plugins = [
    "tests.fixtures.database",
]