from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam
)


class TasksCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        politica_lambda_access_ssm = iam.Policy(
            self, 
            "lambda_access_ssm",
            statements=[
                iam.PolicyStatement(
                    resources=["*"],
                    actions=[
                        "ssm:Describe*",
                        "ssm:Get*",
                        "ssm:List*"
                    ],
                    effect=iam.Effect.ALLOW
                )
            ]
        )

        create_task = lambda_.Function(
            self,
            id="create_task_lambda",
            description="Create tasks",
            function_name='create_task',
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="create_task.lambda_handler",
            code=lambda_.Code.from_asset("src/functions/create_task"),
        )
