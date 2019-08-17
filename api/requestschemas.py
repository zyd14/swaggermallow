from marshmallow import Schema, fields

class TestSchema(Schema):
    david = fields.String()
    bowie = fields.String(default='lala')
    age = fields.Integer()
