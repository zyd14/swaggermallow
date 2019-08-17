import attr
from flask import Flask
from flask_restplus import Api as rApi, Model
from flask_restplus import Resource as PlusResource
from flask_restplus import fields as PlusFields
from werkzeug.contrib.fixers import ProxyFix
from marshmallow import fields, Schema, utils

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

class InnerSchema(Schema):
    meow = fields.Integer(required=True)
    wolf = fields.String(required=True)

    resource_fields = {
        'meow': PlusFields.Integer(required=True),
        'wolf': PlusFields.String(required=True)
    }
    resource_model = api.model('InnerSchema', resource_fields)

class ModelOutputSchema(Schema):

    a = fields.Integer(required=True, desription='something special')
    b = fields.String(default='asdf')
    c = fields.Nested(InnerSchema())
    d = fields.List(fields.String())
    e = fields.Dict(keys=fields.String(), values=fields.Integer())

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

class Another(PlusResource):

    __schema__ = ModelInputSchema

    @ns.expect(ModelInputSchema.resource_model)
    def post(self):
        """ This info comes from the docstring"""
        return {201, "Party"}

api.add_resource(Swagg, '/swagg')
model_input = ModelInputSchema()
print('')

def convert_schema_to_model(mschema:Schema) -> Model:
    m_fields = mschema.declared_fields
    model_fields = {}

    for var, v_attr in m_fields.items():
        required = v_attr.required
        default = None if isinstance(v_attr.default, utils._Missing) else v_attr.default
        description = v_attr.metadata.get('description', None)

        if 'restplus_field' in v_attr.metadata:
            model_fields[var] = v_attr.metadata['restplus_field']
            continue
        if isinstance(v_attr, fields.Nested):
            #model_fields[var] = get_conversion([type(v_attr)](convert_schema_to_model(v_attr.nested), required=v_attr.required, default=v_attr.default))
            try:
                model_fields[var] = convert_schema_to_model(v_attr.nested)
            except Exception as exc:
                raise exc
        elif isinstance(v_attr, fields.List):
            #TODO
            model_fields[var] = None
        elif isinstance(v_attr, fields.Dict):
                dict_description = []
                if 'keys' in v_attr.metadata.keys():
                    dict_description.append(f'keys={get_conversion(type(v_attr.metadata["keys"]))}')
                if 'values' in v_attr.metadata.keys():
                    dict_description.append(f'values={get_conversion(type(v_attr.metadata["values"]))}')
                if description is None:
                    description = ','.join(dict_description)
                else:
                    description += f'| Dict types: {",".join(dict_description)}'
                converted = get_conversion(type(v_attr))
                model_fields[var] = converted(required=required, default=default, description=description)
        else:


            converted = get_conversion(type(v_attr))
            model_fields[var] = converted(required=v_attr.required, default=v_attr.default)

    model = api.model('ModelInputSchema', model_fields)
    return model


@attr.s
class ModelAttr:
    field_class = attr.ib()
    required = attr.ib(default=False)  # type: bool
    default = attr.ib(default=None)

def get_nested_field(m_field: fields.Nested) -> PlusFields.Nested:
    from collections import deque
    nested_fields = deque()
    nested = get_conversion(type(m_field.nested))
    #nested_fields.append(ModelAttr(m_field, required=m_field.required, default=m_field.default))
    current_field = m_field.nested
    while isinstance(nested, PlusFields.Nested):
        nested = get_conversion(type(current_field.nested))
        nested_fields.append(ModelAttr(nested, required=current_field.nested.required, default=current_field.nested.default))
        current_field = current_field.nested
    else:
        nested_fields.append(ModelAttr(nested, required=current_field.required, default=current_field.default))

    inner_field = nested_fields.pop()
    compiled_field = None
    while True:
        try:
            next_field = nested_fields.pop()
        except IndexError:
            break
        compiled_field = next_field.field_class(inner_field.field_class(required=inner_field.required, default=inner_field.default),
                                                required=next_field.required, default=next_field.default)
        inner_field = next_field
    return compiled_field


class PlusDict(PlusFields.Raw):
    pass


def get_conversion(m_field) -> PlusFields:
    mapping = {
        fields.Integer: PlusFields.Integer,
        fields.String: PlusFields.String,
        fields.Boolean: PlusFields.Boolean,
        fields.Decimal: PlusFields.Decimal,
        fields.Date: PlusFields.Date,
        fields.DateTime: PlusFields.DateTime,
        fields.List: PlusFields.List,
        fields.Nested: PlusFields.Nested,
        fields.Url: PlusFields.Url,
        fields.Float: PlusFields.Float,
        fields.Dict: PlusDict
    }

    return mapping[m_field]
model = convert_schema_to_model(ModelOutputSchema())
print('')

if __name__ == '__main__':
    api.app.run()