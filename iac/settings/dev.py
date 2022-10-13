"""Settings for development environments"""
import os

from aws_cdk import Environment

from iac.settings.settings import DatabaseSettings, ProjectSettings, DjangoSettings

DEV_ENV_ID = "dev"
DEV_SETTINGS = ProjectSettings(
    
    env_id=DEV_ENV_ID,
    database=DatabaseSettings(name=f"mermaid-dev", port="5432"),
    api=DjangoSettings(
        container_cpu=1024,
        container_memory=2048,
        container_count=1,
        default_domain_api="dev-api.datamermaid.org",
        default_domain_collect="dev-collect.datamermaid.org",
        mermaid_api_audience="https://dev-api.datamermaid.org",
        
        # Secrets
        dev_emails_name="dev/mermaid-api/dev-emails-mUnSDl"

    ),
)
