#!/usr/bin/env python3

import aws_cdk as cdk

from src.stacks.tasks_cdk_stack import TasksCdkStack


app = cdk.App()
TasksCdkStack(app, "TasksCdkStack")

app.synth()
