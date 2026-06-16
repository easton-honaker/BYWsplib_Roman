"""Validate the schema.yaml against the Felis specification."""
import tomllib
import yaml
from pydantic import ValidationError

from felis.datamodel import Schema


def test_schema():
    with open("database.toml", "rb") as f:
        settings = tomllib.load(f)
    schema_path = settings["felis_path"]
    data = yaml.safe_load(open(schema_path, "r"))

    try:
        schema = Schema.model_validate(data)  # noqa: F841
    except ValidationError as e:
        print(e)
        raise
