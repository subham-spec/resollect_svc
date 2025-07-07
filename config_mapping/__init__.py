import functools
from datetime import datetime
from typing import Type

import marshmallow
import marshmallow_dataclass
from marshmallow import Schema


def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def schema_load_wrapper(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        params = {
            "unknown": marshmallow.EXCLUDE,
        }
        kwargs.update(params)
        return f(*args, **kwargs)

    return wrapper


# Temporary hack to disable camel-casing for few schemas
class NonCamelCaseSchema(Schema):
    class Meta:
        unknown = marshmallow.EXCLUDE


class BaseSchema(Schema):
    def on_bind_field(self, field_name, field_obj) -> None:
        field_obj.data_key = camelcase(field_obj.data_key or field_name)

    class Meta:
        unknown = marshmallow.EXCLUDE


def get_schema(typee: Type, camel_case=True):
    if camel_case:
        schema = marshmallow_dataclass.class_schema(typee, BaseSchema)
    else:
        schema = marshmallow_dataclass.class_schema(typee, NonCamelCaseSchema)

    return schema

class MongoSchema(Schema):
    def on_bind_field(self, field_name, field_obj) -> None:
        key = field_obj.data_key or field_name
        if not key == "_id":
            field_obj.data_key = camelcase(key)


    def skip_none(self, data, **_kwargs):
        if "createdDate" in data:
            data["createdDate"] = datetime.fromisoformat(data["createdDate"])
        if "lastModifiedDate" in data:
            data["lastModifiedDate"] = datetime.fromisoformat(data["lastModifiedDate"])

        # deleting None value keys
        none_keys = {key for key in data if data[key] is None}
        for key in none_keys:
            data.pop(key)

        return data

    class Meta:
        unknown = marshmallow.EXCLUDE
        ordered = True