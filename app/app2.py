import attr
from flask import Flask
from flask_restplus import Api as rApi, Model
from flask_restplus import Resource as PlusResource
from flask_restplus import fields as PlusFields
from marshmallow import fields, Schema, utils

app = Flask(__name__)
app.config.from_object('app.conf.config-dev')
#app.wsgi_app = ProxyFix(app.wsgi_app)
###################################
# Wrap the Api with swagger.docs. It is a thin wrapper around the Api class that adds some swagger smarts
api = rApi(app, version='1.0', title='RestPlus Docs')

ns = api.namespace('model', description='model operations')
###################################

def convert_schema_to_model(mschema:Schema, name='') -> Model:
    m_fields = mschema.declared_fields
    model_fields = {}

    for var, v_attr in m_fields.items():
        required = v_attr.required
        default = get_default(v_attr)
        description = v_attr.metadata.get('description', None)

        if 'restplus_field' in v_attr.metadata:
            model_fields[var] = v_attr.metadata['restplus_field']
            continue

        # Otherwise we will attempt to convert marshmallow fields defined in the schema passed to us into flask_restplus fields
        # in order to be able to be used in restplus models for swagger documentation.  Tricky cases are fields such as
        # Dict, Nested, List, basically any collection.
        if isinstance(v_attr, fields.Nested):
            converted_field = get_conversion(type(v_attr))
            model_fields[var] = converted_field(convert_schema_to_model(v_attr.nested, name=v_attr.name),
                                                required=required,
                                                default=default,
                                                description=description)
        elif isinstance(v_attr, fields.List):
            contained = get_conversion(type(v_attr.container))
            container = get_conversion(type(v_attr))
            model_fields[var] = container(contained(required=v_attr.container.required,
                                                    default=get_default(v_attr.container),
                                                    description=v_attr.container.metadata.get('description', None)),
                                          default=get_default(v_attr),
                                          description=v_attr.metadata.get('description', None))

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
            model_fields[var] = converted(required=required, default=default, description=description)


    model = api.model(name, model_fields)
    return model

@attr.s
class ModelAttr:
    field_class = attr.ib()
    required = attr.ib(default=False)  # type: bool
    default = attr.ib(default=None)

def get_nested_field(m_field: fields.Nested) -> PlusFields.Nested:
    from collections import deque
    nested_fields = deque()
    # Copy down the top-level Nested field
    nested_fields.append(ModelAttr(get_conversion(m_field), required=m_field.required, default=m_field.default))
    nested = get_conversion(type(m_field.nested))
    current_field = m_field.nested

    while isinstance(nested, PlusFields.Nested):
        nested_fields.append(ModelAttr(nested, required=current_field.required, default=get_default(current_field.default)))
        nested = get_conversion(type(current_field.nested))
        nested_fields.append(ModelAttr(nested, required=current_field.nested.required, default=get_default(current_field.nested.default)))
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

def get_default(field):
    return None if isinstance(field.default, utils._Missing) else field.default

class PlusDict(PlusFields.Raw):
    pass

class PlusSchema(PlusFields.Raw):
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

    try:
        return mapping[m_field]
    except KeyError:
        if app.debug:
            print(f"Could not interpret a flask_restplus field mapping for marshmallow field type {m_field}. Defaulting to a flast_restplus Raw field type.")
        return PlusFields.Raw


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

    # resource_fields = {
    #     'a': PlusFields.Integer(required=True, description='a field', example='blah'),
    #     'b': PlusFields.String(required=True),
    #     'c': PlusFields.Boolean
    # }
    #
    # resource_model = api.model('ModelInputSchema', resource_fields)

class InnerSchema(Schema):
    meow = fields.Integer(required=True)
    wolf = fields.String(required=True)

    # resource_fields = {
    #     'meow': PlusFields.Integer(required=True),
    #     'wolf': PlusFields.String(required=True)
    # }
    # resource_model = api.model('InnerSchema', resource_fields)

class ModelOutputSchema(Schema):

    a = fields.Integer(required=True, desription='something special')
    b = fields.String(default='asdf')
    c = fields.Nested(InnerSchema())
    d = fields.List(fields.String())
    e = fields.Dict(keys=fields.String(), values=fields.Integer())

    # resource_fields = {
    #     'a': PlusFields.Integer(required=True),
    #     'b': PlusFields.String(required=False),
    # }
modelOutputSchema = convert_schema_to_model(ModelOutputSchema(), 'ModelOutputSchema')

class Swagg(PlusResource):


    __schema__ = ModelInputSchema

    @ns.doc('get_Swagg', model=modelOutputSchema,
            body=modelOutputSchema)
    @ns.param('id', 'description')
    def post(self):
        """ Some info here"""
        return {200, 'Success'}

class Another(PlusResource):

    __schema__ = ModelInputSchema

    @ns.expect(convert_schema_to_model(ModelOutputSchema()))
    def post(self):
        """ This info comes from the docstring"""
        return {201, "Party"}

api.add_resource(Swagg, '/swagg')
model_input = ModelInputSchema()
print('')



#model = convert_schema_to_model(ModelOutputSchema())
#print('')

if __name__ == '__main__':
    api.app.run(debug=True)