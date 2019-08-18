"""

Project: swagger-resful

File Name: test_schema_converter

Author: Zachary Romer, zach@scharp.org

Creation Date: 8/18/19

Version: 1.0

Purpose:

Special Notes:

"""

import attr
from flask import Flask
from flask_restplus import Api, fields as PlusFields
from marshmallow import Schema, fields





@attr.s
class ModelInput:
    a = attr.ib()  # type: int
    b = attr.ib()  # type: str

@attr.s
class ModelOutput:
    x = attr.ib()  # type: int
    y = attr.ib()  # type: str


class ModelInputSchema(Schema):

    a = fields.Integer(required=True)
    b = fields.String(default='asdf', metadata={'restplus_field': PlusFields.String(required=True)})

class InnerSchema(Schema):
    meow = fields.Integer(required=True)
    wolf = fields.String(required=True)

class ModelOutputSchema(Schema):

    a = fields.Integer(required=True, desription='something special')
    b = fields.String(default='asdf')
    c = fields.Nested(InnerSchema())
    d = fields.List(fields.String())
    e = fields.Dict(keys=fields.String(), values=fields.Integer())

def test_nominal_model_conversion():
    app = Flask(__name__)
    #app.config.from_object('app.conf.config-dev')
    api = Api(app, version='1.0', title='RestPlus Docs')

    from app.app2 import convert_schema_to_model
    model = convert_schema_to_model(api, ModelInputSchema(), name='Something')
    assert set(model.keys()) == set(ModelInputSchema().fields.keys())
    assert set(model.__schema__['properties'].keys()) == set(ModelInputSchema().fields.keys())
