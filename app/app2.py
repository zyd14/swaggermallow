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
api = rApi(app, version='1.0', title='RestPlus Docs')

ns = api.namespace('model', description='model operations')
###################################

class PlusDict(PlusFields.Raw):
    pass

class PlusSchema(PlusFields.Raw):
    pass

def convert_schema_to_model(mschema:Schema) -> Model:
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
            model_fields[var] = converted_field(Model(v_attr.nested.__repr__(), convert_schema_to_model(v_attr.nested),
                                                required=required,
                                                default=default,
                                                description=description))
        elif isinstance(v_attr, fields.List):
            contained = get_conversion(type(v_attr.container))
            container = get_conversion(type(v_attr))
            model_fields[var] = container(contained(required=v_attr.container.required,
                                                    default=get_default(v_attr.container),
                                                    description=v_attr.container.metadata.get('description', None)),
                                          default=get_default(v_attr),
                                          description=v_attr.metadata.get('description', None))

        elif isinstance(v_attr, fields.Dict):
            converted = convert_dict_field(v_attr, description)
            model_fields[var] = converted(required=required, default=default, description=description)

        else:
            converted = get_conversion(type(v_attr))
            model_fields[var] = converted(required=required, default=default, description=description)


    #model = api.model(name, model_fields)
    return model_fields



def convert_dict_field(v_attr: fields.Dict, description) -> PlusDict:
    dict_description = []
    if 'keys' in v_attr.metadata.keys():
        dict_description.append(f'keys={get_conversion(type(v_attr.metadata["keys"]))}')
    if 'values' in v_attr.metadata.keys():
        dict_description.append(f'values={get_conversion(type(v_attr.metadata["values"]))}')
    if description is None:
        description = ','.join(dict_description)
    else:
        description += f'| Dict types: {",".join(dict_description)}'
    return get_conversion(type(v_attr))


def get_default(field):
    return None if isinstance(field.default, utils._Missing) else field.default

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
    b = fields.String(default='asdf')

modelInputFields = convert_schema_to_model(ModelInputSchema())
modelInput = api.model('ModelInput', modelInputFields)

class InnerSchema(Schema):
    meow = fields.Integer(required=True)
    wolf = fields.String(required=True)

inner_schema_fields = convert_schema_to_model(InnerSchema())
innerSchema = api.model('InnerSchema', inner_schema_fields)

class ModelOutputSchema(Schema):

    a = fields.Integer(required=True, desription='something special')
    b = fields.String(default='asdf')
    c = fields.Nested(InnerSchema())
    d = fields.List(fields.String())
    e = fields.Dict(keys=fields.String(), values=fields.Integer())



modelOutputSchema = convert_schema_to_model(ModelOutputSchema())
modelOutput = api.model('ModelOutputSchema', modelOutputSchema)

class Swagg(PlusResource):


    __schema__ = ModelOutputSchema


    @ns.doc('get_Swagg', model=modelOutput, body=modelOutput)
    def post(self):
        """ Some info here"""
        return {200, 'Success'}

class Another(PlusResource):

    __schema__ = ModelInputSchema


    @ns.doc('Another', model=modelInput)
    def post(self):
        """ This info comes from the docstring"""
        return {201, "Party"}

class OneMore(PlusResource):

    __schema__ = ModelInputSchema

    @ns.doc('OneMore', model=modelInput)
    def post(self):
        """ This is how we start a party!"""

        return {203, "Wahhh"}

api.add_resource(Swagg, '/swagg')
api.add_resource(Another, '/another')
ns.add_resource(OneMore, '/this/is')
model_input = ModelInputSchema()
print('')



#model = convert_schema_to_model(ModelOutputSchema())
#print('')

if __name__ == '__main__':
    api.app.run(debug=True)