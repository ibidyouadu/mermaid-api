import os

from aws_cdk import App, Environment
from iac.stacks.common import CommonStack
from iac.stacks.api import ApiStack
from iac.settings.dev import DEV_SETTINGS

tags = {
    "Owner": "sysadmin@datamermaid.org",
    # "Environment": PROJECT_SETTINGS.env_id,
    # "Git Branch": PROJECT_SETTINGS.branch_name,
}


app = App()

cdk_env=Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT", None),
    region=os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
)

common_stack = CommonStack(
    app,
    f"mermaid-api-infra-common",
    env=cdk_env,
    tags=tags,
)

dev_api_stack = ApiStack(
    app,
    "dev-mermaid-api-django",
    env=cdk_env,
    tags=tags,
    config=DEV_SETTINGS,
    cluster=common_stack.cluster,
    database=common_stack.database,
    backup_bucket=common_stack.backup_bucket,
    load_balancer=common_stack.load_balancer,
    container_security_group=common_stack.ecs_sg,
)


app.synth()
