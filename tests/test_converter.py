"""

Project: swagger-resful

File Name: test_converter

Author: Zachary Romer, zach@scharp.org

Creation Date: 8/18/19

Version: 1.0

Purpose:

Special Notes:

"""
from marshmallow import Schema, fields
from

class ModelInputSchema(Schema):

    a = fields.Integer(required=True)
    b = fields.String(default='asdf')
    c = fields.Decimal(places=2)

class InnerSchema(Schema):
    meow = fields.Integer(required=True)
    wolf = fields.String(required=True)


class ModelOutputSchema(Schema):

    a = fields.Integer(required=True, desription='something special')
    b = fields.String(default='asdf')
    c = fields.Nested(InnerSchema())
    d = fields.List(fields.String())
    e = fields.Dict(keys=fields.String(), values=fields.Integer())


def test_nominal_case()

