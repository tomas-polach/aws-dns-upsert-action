# AWS DNS Upsert Github Action

Updates or creates a DNS record in AWS Route53.
Supports assuming a role for cross-account access.

## Usage Example

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name:
        id: retrieve-certificate
        uses: tomas-polach/aws-dns-upsert-action@v1
        with:
          record-name: 'example.com'
          record-type: 'CNAME'
          record-value: 'foo.bar.com'
          record-ttl: '300'
          # optional: use role arn to assume role
          role-arn: 'arn:aws:iam::123456789012:role/role-name'
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```
