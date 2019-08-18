"""

Project: swagger-resful

File Name: conftest

Author: Zachary Romer, zach@scharp.org

Creation Date: 8/18/19

Version: 1.0

Purpose:

Special Notes:

"""
from flask import Flask
from flask_restplus import Api
import pytest

@pytest.fixture
def api_fixture():
    app = Flask(__name__)
    return Api(app, version='1', title='Tester')