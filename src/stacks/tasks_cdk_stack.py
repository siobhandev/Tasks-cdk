from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb
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

        dynamodb.Table(self,
            id="TasksTable",
            table_name="TasksTable",
            partition_key=dynamodb.Attribute(
                name="taskId",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=BillingMode.PAY_PER_REQUEST
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

        update_task = lambda_.Function(
            self,
            id="update_task_lambda",
            description="Update task",
            function_name='update_task',
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="put_task.lambda_handler",
            code=lambda_.Code.from_asset("src/functions/put_task"),
        )

        update_task.role.attach_inline_policy(politica_lambda_access_ssm)
        update_task.role.attach_inline_policy(politica_lambda_access_dynamodb)
        
        delete_task = lambda_.Function(
            self,
            id="delete_task_lambda",
            description="Delete task",
            function_name='delete_task',
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="delete_task.lambda_handler",
            code=lambda_.Code.from_asset("src/functions/delete_task"),
        )

        delete_task.role.attach_inline_policy(politica_lambda_access_ssm)
        delete_task.role.attach_inline_policy(politica_lambda_access_dynamodb)

        api_crud_tasks.root.add_resource('POST').add_resource('tasks').add_method('POST', 
            apigateway.LambdaIntegration(create_task),
            method_responses=[apigateway.MethodResponse(status_code="201")]
        )

        api_crud_tasks.root.add_resource('GET').add_resource('tasks').add_resource('{taskId}').add_method('GET', 
            apigateway.LambdaIntegration(get_task),
            method_responses=[apigateway.MethodResponse(status_code="200")]
        )

        api_crud_tasks.root.add_resource('PUT').add_resource('tasks').add_resource('{taskId}').add_method('PUT', 
            apigateway.LambdaIntegration(update_task),
            method_responses=[apigateway.MethodResponse(status_code="200")]
        )

        api_crud_tasks.root.add_resource('DELETE').add_resource('tasks').add_resource('{taskId}').add_method('DELETE', 
            apigateway.LambdaIntegration(delete_task),
            method_responses=[apigateway.MethodResponse(status_code="204")]
        )


