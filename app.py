import attr

from flask import Flask
from flask_restful import  Api, Resource
from flask_restful_swagger import swagger
from marshmallow import Schema, fields
from flask_restplus import Api as rApi
from flask_restplus import Resource as PlusResource
from flask_restplus import fields as PlusFields
import json

app = Flask(__name__)

###################################
# Wrap the Api with swagger.docs. It is a thin wrapper around the Api class that adds some swagger smarts
api = swagger.docs(Api(app), apiVersion='0.1', api_spec_url='/api/spec')
###################################

@attr.s
class ModelInput:
    a = attr.ib()  # type: int
    b = attr.ib()  # type: str

@attr.s
class ModelOutput:
    x = attr.ib()  # type: int
    y = attr.ib()  # type: str

@swagger.model
class ModelInputSchema(Schema):

    a = fields.Integer()
    b = fields.String(default='asdf')
    resource_fields = {
        'a': PlusFields.Integer(required=True, description='a field', example='blah'),
        'b': PlusFields.String(required=True),
        'c': PlusFields.Boolean(required=True)
    }
    #resource_model = api.model('ModelInputSchema', resource_fields)


@swagger.model
class ModelOutputSchema(Schema):

    a = fields.Integer()
    b = fields.String(default='asdf')
    resource_fields = {
        'a': PlusFields.Integer(required=True),
        'b': PlusFields.String(required=False),
    }

class SwaggIt(Resource):

    @swagger.operation(
        notes='some really good notes',
        responseClass=ModelOutputSchema.__name__,
        nickname='upload',
        parameters=[
            {
                "name": "body",
                "description": 'a description',
                "required": True,
                "allowMultiple": False,
                "dataType": ModelInputSchema.__name__,
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 201,
                "message": "Created. The URL of the created blueprint should be in the Location header"
            },
            {
                "code": 405,
                "message": "Invalid input"
            }
        ]
    )
    def get(self, todo_id):
        return {200, 'Success'}

api.add_resource(SwaggIt, '/swagg')

# rapi = rApi(app, version='0.1', title='Test Api')
# test_flask_model = rapi.model('FlaskModel', {
#     'a': PlusFields.Integer(required=True),
#     'num': PlusFields.String(required=False)
# })
# test_marshmallow_model = rapi.model('MarshModel', ModelInputSchema.resource_fields)

class AnotherTest(PlusResource):
    pass

if __name__ == '__main__':
    api.app.run()