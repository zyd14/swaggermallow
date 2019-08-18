"""

Project: swagger-resful

File Name: example_api

Author: Zachary Romer, zach@scharp.org

Creation Date: 8/18/19

Version: 1.0

Purpose:

Special Notes:

"""
import attr
from flask import Flask
from flask_restplus import Api, Model
from flask_restplus import Resource as PlusResource
from flask_restplus import fields as PlusFields
from marshmallow import fields, Schema, utils

from app.app2 import convert_schema_to_model

app = Flask(__name__)
app.config.from_object('app.conf.config-dev')
#app.wsgi_app = ProxyFix(app.wsgi_app)
###################################
# Wrap the Api with swagger.docs. It is a thin wrapper around the Api class that adds some swagger smarts
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

modelInputSchema = convert_schema_to_model(api, ModelInputSchema(), 'ModelInputSchema')
modelOutputSchema = convert_schema_to_model(api, ModelOutputSchema(), 'ModelOutputSchema')
modelRsponse = convert_schema_to_model(api, ResponseSchema(), 'ModelResponse')
badResponseModel = convert_schema_to_model(api, BadResponse(), 'BadResponse')

class Swagg(PlusResource):


    __schema__ = ModelInputSchema

    @api.expect(modelOutputSchema)
    @api.response(201, 'Success Response', model=modelRsponse)
    @api.response(400, 'Bad Request', model=badResponseModel)
    def post(self):
        """ Some info here"""
        return {200, 'Success'}

class Another(PlusResource):

    __schema__ = ModelInputSchema

    @api.expect(convert_schema_to_model(api, ModelOutputSchema(), 'ModelOutputSchema'))

    def post(self):
        """ This info comes from the docstring"""
        return {201, "Party"}

ns_batch.add_resource(Swagg, '/swagg')
ns_user.add_resource(Another, '/another')

if __name__ == '__main__':
    api.app.run(debug=True)