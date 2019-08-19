from flask import Flask
from flask_restplus import Api
import pytest

@pytest.fixture
def api_fixture():
    app = Flask(__name__)
    return Api(app, version='1', title='Tester')