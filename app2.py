import attr
from flask import Flask
from flask_restplus import Api as rApi, Model
from flask_restplus import Resource as PlusResource
from flask_restplus import fields as PlusFields
from werkzeug.contrib.fixers import ProxyFix
from marshmallow import fields, Schema

app = Flask(__name__)
#app.wsgi_app = ProxyFix(app.wsgi_app)
###################################
# Wrap the Api with swagger.docs. It is a thin wrapper around the Api class that adds some swagger smarts
api = rApi(app, version='1.0', title='RestPlus Docs')

ns = api.namespace('model', description='model operations')
###################################

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
    a.metadata = {'restplus_field': PlusFields.Integer(required=True)}
    b = fields.String(default='asdf', metadata={'restplus_field': PlusFields.String(required=True)})
    b.metadata = {'restplus_field': PlusFields.String(required=True)}

    resource_fields = {
        'a': PlusFields.Integer(required=True, description='a field', example='blah'),
        'b': PlusFields.String(required=True),
        'c': PlusFields.Boolean
    }

    resource_model = api.model('ModelInputSchema', resource_fields)


class ModelOutputSchema(Schema):

    a = fields.Integer()
    b = fields.String(default='asdf')
    c = fields.Nested(fields.String())
    resource_fields = {
        'a': PlusFields.Integer(required=True),
        'b': PlusFields.String(required=False),
    }

class Swagg(PlusResource):


    __schema__ = ModelInputSchema

    @ns.doc('get_Swagg', model=ModelInputSchema.resource_model,
            body=ModelInput)
    @ns.param('id', 'description')
    def post(self):
        """ Some info here"""
        return {200, 'Success'}

api.add_resource(Swagg, '/swagg')
model_input = ModelInputSchema()
print('')

def convert_schema_to_model(mschema:Schema) -> Model:
    m_fields = mschema.declared_fields
    model_fields = {}

    for var, v_attr in m_fields.items():
        if 'restplus_field' in v_attr.metadata:
            model_fields[var] = v_attr.metadata['restplus_field']
            continue
        # if isinstance(v_attr, fields.Nested) and v_attr.nested:
        #     model_fields[var] = get_conversion([type(v_attr)](convert_schema_to_model(v_attr.nested), required=v_attr.required, default=v_attr.default)
        # model_fields[var] = get_conversion([type(v_attr)](required=v_attr.required, default=v_attr.default)

    return api.model('ModelInputSchema', model_fields)
#
# def get_nested_field(m_field):
#     from collections import deque
#     nested = get_conversion(m_field.nested)
#     nested_fields = deque()
#     nested_fields.append(nested)
#     while isinstance(nested, PlusFields.Nested):
#         old_nested = nested
#         nested = get_conversion(type(old_nested.nested))
#         nested_fields.append((nested, old_nested.nested.required, old_nested.nested.default))
#
#     inner_field = nested_fields.pop()
#     compiled_field = None
#     while True:
#         try:
#             next_field = nested_fields.pop()
#         except IndexError:
#             break
#         compiled_field = next_field[0](inner_field[0](required=inner_field[1], default=inner_field[2]))
#         inner_field = next_field
#
#
# def get_conversion(m_field) -> PlusFields:
#     mapping = {
#         fields.Integer: PlusFields.Integer,
#         fields.String: PlusFields.String,
#         fields.Boolean: PlusFields.Boolean,
#         fields.Decimal: PlusFields.Decimal,
#         fields.Date: PlusFields.Date,
#         fields.List: PlusFields.List,
#         fields.Nested: PlusFields.Nested,
#         fields.Url: PlusFields.Url,
#         fields.Float: PlusFields.Float
#     }
#     return mapping[m_field]
# model = convert_schema_to_model(ModelOutputSchema())
# print('')

if __name__ == '__main__':
    api.app.run()