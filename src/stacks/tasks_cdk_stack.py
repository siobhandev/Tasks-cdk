from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_apigateway as apigateway
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
        
        politica_lambda_access_dynamodb = iam.Policy(
            self,
            "lambda_access_dynamodb",
            statements=[
                iam.PolicyStatement(
                    resources=["*"],
                    actions=[
                        "dynamodb:*"
                    ],
                    effect=iam.Effect.ALLOW
                )
            ]
        )

        api_crud_tasks = apigateway.RestApi(self, id="CRUD TASKS",
            rest_api_name="crud_api",
            description="Esta API Contendrá los endpoints de Tasks"
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

        create_task.role.attach_inline_policy(politica_lambda_access_ssm)
        create_task.role.attach_inline_policy(politica_lambda_access_dynamodb)

        get_task = lambda_.Function(
            self,
            id="get_task_lambda",
            description="Get tasks",
            function_name='get_task',
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="get_task.lambda_handler",
            code=lambda_.Code.from_asset("src/functions/get_task"),
        )

        get_task.role.attach_inline_policy(politica_lambda_access_ssm)
        get_task.role.attach_inline_policy(politica_lambda_access_dynamodb)

        task_resource = api_crud_tasks.root.add_resource('tasks')
        task_resource.add_method('POST', 
            apigateway.LambdaIntegration(create_task),
            method_responses=[apigateway.MethodResponse(status_code="201")]
        )

        task_id_resource = task_resource.add_resource('{taskId}')
        task_id_resource.add_method('GET', 
            apigateway.LambdaIntegration(get_task),
            method_responses=[apigateway.MethodResponse(status_code="200")]
        )

