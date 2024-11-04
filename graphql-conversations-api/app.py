#!/usr/bin/env python3
import os

import aws_cdk as cdk

from app.graphql_api_stack import GraphqlLabStack


app = cdk.App()
GraphqlLabStack(
    app,
    "GraphqlLabStack",
)

app.synth()
