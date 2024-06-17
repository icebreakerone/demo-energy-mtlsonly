import os

ENV = os.environ.get("ENV", "dev")
DIRNAME = os.path.dirname(os.path.realpath(__file__))
OPEN_API_ROOT = "/dev" if ENV == "prod" else ""
