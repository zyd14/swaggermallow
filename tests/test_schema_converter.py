from flask_restplus import fields as PlusFields
from marshmallow import Schema, fields

from converter.schema2model import convert_schema_to_model, get_conversion, PlusDict


def test_nominal_model_conversion(api_fixture):
    class ModelInputSchema(Schema):
        a = fields.Integer(required=True)
        b = fields.String(default='asdf', metadata={'restplus_field': PlusFields.String(required=True)})

    model = convert_schema_to_model(api_fixture, ModelInputSchema(), name='Something')
    assert set(model.keys()) == set(ModelInputSchema().fields.keys())
    assert set(model.__schema__['properties'].keys()) == set(ModelInputSchema().fields.keys())

def test_nested_model_conversion(api_fixture):

    class InnerSchema(Schema):
        meow = fields.Integer(required=True)
        wolf = fields.String(required=True)

    class NestedSchema(Schema):

        a = fields.String(required=True, description='Yada Yada')
        b = fields.Nested(InnerSchema(), required=True)

    model = convert_schema_to_model(api_fixture, NestedSchema(), name='Nested')
    assert set(model.keys()) == set(NestedSchema().fields.keys())
    assert set(model.__schema__['properties'].keys()) == set(NestedSchema().fields.keys())

    assert set(model['b'].nested.keys()) == InnerSchema().fields.keys()

def test_complex_schema_conversion(api_fixture):

    class InnerSchema(Schema):
        meow = fields.Integer(required=True)
        wolf = fields.String(required=True)

    class ModelOutputSchema(Schema):
        a = fields.Integer(required=True, desription='something special')
        b = fields.String(default='asdf')
        c = fields.Nested(InnerSchema())
        d = fields.List(fields.String())
        e = fields.Dict(keys=fields.String(), values=fields.Integer())

    model = convert_schema_to_model(api_fixture, ModelOutputSchema(), name='Complex')
    assert set(model.keys()) == set(ModelOutputSchema().fields.keys())
    assert set(model.__schema__['properties'].keys()) == set(ModelOutputSchema().fields.keys())

    # Test container field conversions
    assert set(model['c'].nested.keys()) == InnerSchema().fields.keys()

    # Test List conversion
    assert isinstance(model['d'], PlusFields.List)
    assert isinstance(model['d'].container, PlusFields.String)

    # Test Dict conversion
    assert isinstance(model['e'], PlusDict)
    assert model['e'].description.lower() == """keys=<class 'flask_restplus.fields.string'>,values=<class 'flask_restplus.fields.integer'>"""

def test_unknown_type_default_to_raw_field(api_fixture):

    unsupported_types = [fields.Email,
                         fields.Function,
                         fields.ValidatedField,
                         fields.Method,
                         fields.LocalDateTime,
                         ]

    for unknown_type in unsupported_types:

        class BlackberryPie(Schema):
            crust = unknown_type()

        if unknown_type == fields.Int:
            pass
        model = convert_schema_to_model(api_fixture, BlackberryPie(), name="Blackberry Pie")
        assert type(model['crust']) == PlusFields.Raw

def test_constant(api_fixture):

    class TestBob(Schema):
        bob = fields.Constant('a')

    import os
    os.environ['FLASK_DEBUG'] = 'True'
    model = convert_schema_to_model(api_fixture, TestBob(), name='TestBob')
    assert isinstance(model['bob'], PlusFields.Raw)

def test_restplus_field_descriptors(api_fixture):

    class TestBob(Schema):
        bob = fields.Integer(restplus_field=PlusFields.Integer)
        tod = fields.Email(restplus_field=PlusFields.String)
        kelly = fields.LocalDateTime(restplus_field=PlusFields.DateTime)

    model = convert_schema_to_model(api_fixture, TestBob(), name='TestBob')
    assert isinstance(model['bob'], PlusFields.Integer)
    assert isinstance(model['tod'], PlusFields.String)
    assert isinstance(model['kelly'], PlusFields.DateTime)

