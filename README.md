# Breaking up AWS API Gateway Resources into NestedStacks

Welcome! This is a small AWS CDK (Python) project that demonstrates how to overcome the resource limit of an API Gateway in a single CloudFormation stack by breaking it up into NestedStacks and having a non-basic default integration, compared to a simple API Gateway setup.

This repository complements my first technical blog post, where I share the story behind this setup, the problems I faced, and how I resolved them using CDK best practices and some workarounds.

> 📖 Read the full story behind this implementation in the Medium blog post:
[Breaking Up AWS API Gateway Resources into NestedStacks Using CDK](https://medium.com/@attila9778/breaking-up-aws-api-gateway-resources-into-nestedstacks-using-cdk-51f497a27bc0)

## 🗃️ File Structure

```graphql
api_gateway_poc/     
├── apigw_stack.py              # API Gateway in single stack
├── apigw_nested_root_stack.py  # Root stack for split API Gateway
└── nested                      # Parts of nested stack implementation
    ├── apigw_nested_stack.py   # API Gateway Resource definitions
    ├── apigw_deploy_stack.py   # API Gateway Deployment and Stage definitions
    ├── lambda_integration.py   # Custom Lambda Integration  
└── lambda/                     # Example Lambda function code
```

## 🧠 Motivation

Long ago, I was working on an internal project that used AWS API Gateway extensively. At some point, we hit the **CloudFormation stack resource limit** due to the large number of endpoints.

The official [AWS CDK documentation](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway-readme.html#breaking-up-methods-and-resources-across-stacks) briefly covers how to split API Gateway resources across stacks using **NestedStacks**. However, in practice, if we go with a solution closer to real-world application, I ran into several issues and edge cases not mentioned there.

## 🛠️ Key Concepts & Problems Solved

- **Default integration propagation**  
    CDK automatically propagates `default_integration` across stacks, which can cause unexpected behavior. I show how to handle it explicitly.

- **Passing RestApi between stacks**  
    To split resources, I needed to pass the `RestApi` object and certain props across stacks to maintain consistent deployment behavior.

- **Policy size overflow in Lambda integrations**  
    Adding too many endpoints caused IAM policy size to exceed limits. I demonstrate how using **custom Lambda integrations** helps reduce policy size.

- **Manual logical ID for Deployment**  
    Without a logical ID change, CDK might skip creating a new deployment. I used:
    ```python
    deployment.add_to_logical_id(str(datetime.now()))
    ```

- **Dependency handling between stacks**
    Correct Deployment and Stage setup required manually setting:
    ```python
    deployment.node.add_dependency(resource_stack)
    ```

## 🧪 How to Run
  
1. Make sure you have Python and AWS CDK installed.
2. Install requirements:
    ```python
    pip install -r requirements.txt
    ```
3. Deploy:
    ```bash
    cdk deploy
    ```

## 📚 References

* AWS CDK API Gateway Nested Stacks:
https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway-readme.html#breaking-up-methods-and-resources-across-stacks

* Deployment logical ID and dependency:
https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_apigateway/Deployment.html