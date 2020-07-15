## schema2model

A tool to convert Marshmallow Schema objects into flask-restplus Model objects with flask-restplus field types

### Why?

Why not just use flask-restplus fields / models when designing your endpoints, and not have to deal with converting
your Marshmallow schemas into [flask-restplus](https://flask-restplus.readthedocs.io/en/stable/) Models at all?  
Quite honestly, in my case it's because I didn't know about flask-restplus Model objects and how they tied into building 
Swagger documentation until after I had already built a whole API using Marshmallow Schemas for validation and serialization.  
That being said, I do feel that Marshmallow is a bit more powerful for validation / serialization than what flask-restplus Model objects. 
If you do find yourself wanting to do schema validation using Marshmallow then this tool might help you to more easily 
convert your Schema objects into flask-restplus Models when you need them, for instance
when decorating endpoint functions with `@api.expect()` or `@api.response()` for generating Swagger documentation.

An example API can be found in app/example_api.py.  To run, type:  
`python example_api.py`  
in a terminal window from the `app` directory.  You should now be able to see the Swagger documentation
automatically generated from the use of flask-resplus decorators by visiting the following url:  
[127.0.0.1:5000](http://127.0.0.1:5000/)

This example API defines its request and response
schemas as Marshmallow Schemas, but uses the `schema2model.convert_schema_to_model()` method to create identical 
flask-restplus Model objects for use with `@api.expect` and `@api.response` calls.

This library does not seem to produce models which are compatible with `flask-restplus-swagger` `@swagger` decorators at this time. 