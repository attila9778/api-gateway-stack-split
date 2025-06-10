from aws_cdk import Stack
from aws_cdk import NestedStack
from aws_cdk import aws_apigateway

from datetime import datetime


class ApiGatewayDeployStack(NestedStack):

    def __init__(
        self,
        *,
        scope: Stack,
        rest_api_name: str,
        rest_api_id: str,
        root_resource_id: str,
        resource_methods: list = []
    ):
        super().__init__(
            scope=scope,
            id=f"{rest_api_name}-deploy-stack"
        )

        rest_api = aws_apigateway.RestApi.from_rest_api_attributes(
            scope=self,
            id=rest_api_name,
            rest_api_id=rest_api_id,
            root_resource_id=root_resource_id,
        )

        deployment = aws_apigateway.Deployment(
            scope=self,
            id=f"{rest_api_name}-deployment",
            api=rest_api,
        )

        for method in resource_methods:
            deployment.node.add_dependency(method)

        # Note: required to update API when changes happen
        deployment.add_to_logical_id(str(datetime.now()))

        self.stage = aws_apigateway.Stage(
            scope=self,
            id=f"{rest_api_name}-stage",
            deployment=deployment,
            stage_name="v0",
        )
