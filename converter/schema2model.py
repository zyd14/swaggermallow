from flask_restplus import Api, Model
from flask_restplus import fields as PlusFields
from marshmallow import fields, Schema, utils


class PlusDict(PlusFields.Raw):
    pass

def convert_schema_to_model(api: Api, mschema: Schema, name: str='') -> Model:
    m_fields = mschema.declared_fields
    model_fields = {}

    for var, v_attr in m_fields.items():
        required = v_attr.required
        default = get_default(v_attr)
        description = v_attr.metadata.get('description', None)

        if 'restplus_field' in v_attr.metadata:
            model_fields[var] = v_attr.metadata['restplus_field'](required=required, default=default, description=description)
            continue

        # Otherwise we will attempt to convert marshmallow fields defined in the schema passed to us into flask_restplus fields
        # in order to be able to be used in restplus models for swagger documentation.  Tricky cases are fields such as
        # Dict, Nested, List, basically any collection.
        if isinstance(v_attr, fields.Nested):
            converted_field = get_conversion(type(v_attr))
            model_fields[var] = converted_field(convert_schema_to_model(api, v_attr.nested, name=v_attr.name),
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
            description = convert_dict_field_description(v_attr, description)
            converted =  get_conversion(type(v_attr))
            model_fields[var] = converted(required=required, default=default, description=description)

        else:
            converted = get_conversion(type(v_attr))
            model_fields[var] = converted(required=required, default=default, description=description)

    model = api.model(name, model_fields)
    return model

def convert_dict_field_description(v_attr: fields.Dict, description) -> PlusDict:
    dict_description = []
    if 'keys' in v_attr.metadata.keys():
        dict_description.append(f'keys={get_conversion(type(v_attr.metadata["keys"]))}')
    if 'values' in v_attr.metadata.keys():
        converted = get_conversion(type(v_attr.metadata["values"]))
        dict_description.append(f'values={converted}')
    if description is None:
        description = ','.join(dict_description)
    else:
        description += f'| Dict types: {",".join(dict_description)}'
    return description



def get_default(field):
    return None if isinstance(field.default, utils._Missing) else field.default


def get_conversion(m_field) -> PlusFields:
    mapping = {
        fields.Integer: PlusFields.Integer,
        fields.Int: PlusFields.Integer,
        fields.String: PlusFields.String,
        fields.Str: PlusFields.String,
        fields.Boolean: PlusFields.Boolean,
        fields.Bool: PlusFields.Boolean,
        fields.Decimal: PlusFields.Decimal,
        fields.Date: PlusFields.Date,
        fields.DateTime: PlusFields.DateTime,
        fields.List: PlusFields.List,
        fields.Nested: PlusFields.Nested,
        fields.Url: PlusFields.Url,
        fields.URL: PlusFields.Url,
        fields.Float: PlusFields.Float,
        fields.Dict: PlusDict,
        fields.Raw: PlusFields.Raw,
    }

    try:
        return mapping[m_field]
    except KeyError:
        import os
        if os.getenv('FLASK_DEBUG', False):
            print(f"Could not interpret a flask_restplus field mapping for marshmallow field type {m_field}. Defaulting to a flast_restplus Raw field type.")
        return PlusFields.Raw
