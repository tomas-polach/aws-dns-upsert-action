import sys
import os
from time import sleep
import boto3


class Route53DnsManager:
    def __init__(
            self,
            role_arn: str | None = None,
    ):
        if role_arn is None:
            self.route53_client = boto3.client('route53')
        else:
            # if domain is registered in another aws account, assume role
            access_key_id, secret_access_key, session_token = self._assume_role(role_arn)
            self.route53_client = boto3.client(
                'route53',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                aws_session_token=session_token,
            )

    @staticmethod
    def _assume_role(role_arn: str) -> tuple[str, str, str]:
        sts_client = boto3.client('sts')
        assumed_role = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="DNSUpdateSession"
        )
        return (
            assumed_role['Credentials']['AccessKeyId'],
            assumed_role['Credentials']['SecretAccessKey'],
            assumed_role['Credentials']['SessionToken'],
        )

    def _get_hosted_zone_id(self, subdomain):
        # List all hosted zones
        hosted_zones = self.route53_client.list_hosted_zones_by_name()

        # Find the hosted zone ID for the given subdomain
        for zone in hosted_zones['HostedZones']:
            if subdomain.rstrip('.').endswith(zone['Name'].rstrip('.')):
                return zone['Id'].split('/')[-1]

        raise Exception(f"No hosted zone found for subdomain: {subdomain}")

    def upsert_cname_record(self, name: str, record_type: str, value: str, ttl: int) -> None:
        # Retrieve hosted zone ID
        hosted_zone_id = self._get_hosted_zone_id(record_name)
        # Upsert record
        change_batch = {
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": name,
                        "Type": record_type,
                        "TTL": ttl,
                        "ResourceRecords": [
                            {
                                "Value": value,
                            }
                        ]
                    }
                }
            ]
        }
        self.route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )


if __name__ == "__main__":
    # retrieve inputs
    record_name = os.getenv('RECORD_NAME')
    record_type = os.getenv('RECORD_TYPE')
    record_value = os.getenv('RECORD_VALUE')
    record_ttl = int(os.getenv('RECORD_TTL', 300))
    role_arn = os.getenv('ROLE_ARN')

    # check required inputs
    if record_name is None or record_type is None or record_value is None:
        print("Missing required env vars: RECORD_NAME, RECORD_TYPE, RECORD_VALUE")
        sys.exit(1)

    m = Route53DnsManager(role_arn = role_arn)
    m.upsert_cname_record(
        name=record_name,
        record_type=record_type,
        value=record_value,
        ttl=record_ttl,
    )
