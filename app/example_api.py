from flask import Flask
from flask_restplus import Api
from flask_restplus import Resource as PlusResource
from marshmallow import fields, Schema

from converter.schema2model import convert_schema_to_model, patch_api

app = Flask(__name__)
app.config.from_object('app.conf.config-dev')
api = Api(app, version='1.0', title='RestPlus Docs')

ns_batch = api.namespace('batch', description='batch operations')
ns_user = api.namespace('user', description='user operations')


class ResponseSchema(Schema):
    code = fields.String(required=True)
    body = fields.Dict(default=None)
    message = fields.String(default='Success')


class BadResponse(Schema):
    code = fields.String(required=True, default=400)
    body = fields.Dict(keys=fields.String(), values=fields.String())
    message = fields.String(required=True, default="Bad Request")


class ModelInputSchema(Schema):
    a = fields.Integer(required=True)
    b = fields.String(default='asdf')


class InnerSchema(Schema):
    meow = fields.Integer(required=True)
    wolf = fields.String(required=True)


class ModelOutputSchema(Schema):
    a = fields.Integer(required=True, desription='something special')
    b = fields.String(default='asdf')
    c = fields.Nested(InnerSchema())
    d = fields.List(fields.String())
    e = fields.Dict(keys=fields.String(), values=fields.Integer())


api = patch_api(api)


class Swagg(PlusResource):
    __schema__ = ModelInputSchema

    @api.expect(ModelOutputSchema)
    @api.response(201, 'Success Response', model=ResponseSchema)
    @api.response(400, 'Bad Request', model=BadResponse)
    def post(self):
        """ Some info here"""
        return {200, 'Success'}


class Another(PlusResource):
    __schema__ = ModelInputSchema

    @api.expect(ModelOutputSchema())
    def post(self):
        """ This info comes from the docstring"""
        return {201, "Party"}


ns_batch.add_resource(Swagg, '/swagg')
ns_user.add_resource(Another, '/another')

if __name__ == '__main__':
    pass
    api.app.run(debug=True)
    pass
