"""IR -> AWS CDK (TypeScript). Roadmap item: currently emits the VPC + S3 constructs."""
def compile_ir_to_cdk(ir: dict) -> dict[str, str]:
    lines = ["import * as cdk from 'aws-cdk-lib';", "import * as ec2 from 'aws-cdk-lib/aws-ec2';",
             "import * as s3 from 'aws-cdk-lib/aws-s3';", "",
             "export class SecureVibeStack extends cdk.Stack {",
             "  constructor(scope: cdk.App, id: string) {", "    super(scope, id);"]
    for r in ir["resources"]:
        if r["type"] == "AWS::VPC":
            lines.append(f"    new ec2.Vpc(this, '{r['id']}', {{ ipAddresses: ec2.IpAddresses.cidr('{r['cidr']}'), maxAzs: {r['maxAzs']}, flowLogs: {{ all: {{}} }} }});")
        if r["type"] == "AWS::S3":
            lines.append(f"    new s3.Bucket(this, '{r['id']}', {{ blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL, encryption: s3.BucketEncryption.KMS, versioned: true, enforceSSL: true }});")
    lines += ["  }", "}"]
    return {"lib/securevibe-stack.ts": "\n".join(lines) + "\n"}
