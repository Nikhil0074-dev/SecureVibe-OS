use hcl::{Body, Expression};
use serde_json::{json, Value};

fn attr_bool(b: &hcl::Block, key: &str) -> Option<bool> {
    b.body().attributes().find(|a| a.key() == key).and_then(|a| match a.expr() {
        Expression::Bool(v) => Some(*v),
        _ => None,
    })
}
fn attr_str(b: &hcl::Block, key: &str) -> Option<String> {
    b.body().attributes().find(|a| a.key() == key).and_then(|a| match a.expr() {
        Expression::String(s) => Some(s.clone()),
        _ => None,
    })
}

/// Convert parsed Terraform into SecureVibe IR. Values found in the source are kept AS-IS
/// (insecure settings stay insecure) so the security scanner can flag them; "Auto Secure" then fixes the IR.
pub fn convert(body: &Body) -> Value {
    let mut resources: Vec<Value> = vec![];
    for blk in body.blocks().filter(|b| b.identifier() == "resource") {
        let labels: Vec<&str> = blk.labels().iter().map(|l| l.as_str()).collect();
        if labels.len() != 2 { continue; }
        let (rtype, name) = (labels[0], labels[1]);
        let id = name.to_lowercase();
        match rtype {
            "aws_vpc" => resources.push(json!({"id": id, "type": "AWS::VPC",
                "cidr": attr_str(blk, "cidr_block").unwrap_or("10.0.0.0/16".into()),
                "maxAzs": 2, "enableFlowLogs": false, "secure": false, "tags": {}, "dependencies": []})),
            "aws_s3_bucket" => resources.push(json!({"id": id, "type": "AWS::S3",
                "blockPublicAcls": false, "encryption": "none", "versioning": false,
                "containsPii": false, "dataClassification": "INTERNAL", "tags": {}, "dependencies": []})),
            "aws_db_instance" => resources.push(json!({"id": id, "type": "AWS::RDS",
                "engine": attr_str(blk, "engine").unwrap_or("postgres".into()),
                "instanceClass": attr_str(blk, "instance_class").unwrap_or("db.t3.medium".into()),
                "private": !attr_bool(blk, "publicly_accessible").unwrap_or(false),
                "encrypted": attr_bool(blk, "storage_encrypted").unwrap_or(false),
                "multiAz": attr_bool(blk, "multi_az").unwrap_or(false),
                "deletionProtection": attr_bool(blk, "deletion_protection").unwrap_or(false),
                "subnetGroup": "private", "tags": {}, "dependencies": []})),
            "aws_instance" => resources.push(json!({"id": id, "type": "AWS::EC2",
                "instanceType": attr_str(blk, "instance_type").unwrap_or("t3.micro".into()),
                "associatePublicIp": attr_bool(blk, "associate_public_ip_address").unwrap_or(false),
                "requireImdsV2": false, "encryptedRoot": false, "subnetGroup": "private",
                "tags": {}, "dependencies": []})),
            _ => {}
        }
    }
    json!({"version": "v2.0",
           "metadata": {"compliance": ["CIS-1.5"], "env": "prod", "region": "eu-west-1"},
           "resources": resources, "connections": []})
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser::hcl_parser::parse;

    const INSECURE: &str = r#"
resource "aws_db_instance" "Legacy_DB" {
  engine              = "mysql"
  publicly_accessible = true
  storage_encrypted   = false
}
resource "aws_s3_bucket" "logs" {
  bucket = "my-logs"
}
resource "aws_instance" "web" {
  instance_type               = "t3.large"
  associate_public_ip_address = true
}
resource "aws_vpc" "main" {
  cidr_block = "172.16.0.0/16"
}
resource "aws_route53_zone" "ignored" {
  name = "example.com"
}
"#;

    fn res<'a>(ir: &'a Value, id: &str) -> &'a Value {
        ir["resources"].as_array().unwrap().iter().find(|r| r["id"] == id).unwrap()
    }

    #[test]
    fn insecure_settings_are_preserved_for_the_scanner() {
        let ir = convert(&parse(INSECURE).unwrap());
        let db = res(&ir, "legacy_db");
        assert_eq!(db["type"], "AWS::RDS");
        assert_eq!(db["private"], false);
        assert_eq!(db["encrypted"], false);
        assert_eq!(db["engine"], "mysql");
        assert_eq!(res(&ir, "logs")["blockPublicAcls"], false);
        assert_eq!(res(&ir, "web")["associatePublicIp"], true);
        assert_eq!(res(&ir, "main")["cidr"], "172.16.0.0/16");
    }

    #[test]
    fn unknown_resource_types_are_skipped() {
        let ir = convert(&parse(INSECURE).unwrap());
        assert_eq!(ir["resources"].as_array().unwrap().len(), 4);
    }

    #[test]
    fn secure_rds_roundtrip() {
        let src = r#"resource "aws_db_instance" "rds_main" {
  publicly_accessible = false
  storage_encrypted   = true
  deletion_protection = true
  multi_az            = true
}"#;
        let ir = convert(&parse(src).unwrap());
        let db = res(&ir, "rds_main");
        assert_eq!((db["private"].as_bool(), db["encrypted"].as_bool(), db["multiAz"].as_bool()), (Some(true), Some(true), Some(true)));
        assert_eq!(db["deletionProtection"], true);
    }

    #[test]
    fn compiler_output_is_parseable() {
        // Output of the compiler service (written by scripts/e2e.py); skipped if not generated yet.
        let p = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../generated/demo/main.tf");
        let Ok(src) = std::fs::read_to_string(p) else { return };
        let ir = convert(&parse(&src).expect("generated Terraform must parse"));
        let ids: Vec<_> = ir["resources"].as_array().unwrap().iter().map(|r| r["id"].as_str().unwrap().to_string()).collect();
        for want in ["vpc_main", "s3_app", "rds_main", "ec2_app"] {
            assert!(ids.contains(&want.to_string()), "missing {want} in {ids:?}");
        }
    }

    #[test]
    fn invalid_hcl_is_an_error() {
        assert!(parse("resource \"x\" {{{ nope").is_err());
    }

    #[test]
    fn output_has_ir_envelope() {
        let ir = convert(&parse("").unwrap());
        assert_eq!(ir["version"], "v2.0");
        assert!(ir["resources"].as_array().unwrap().is_empty());
    }
}
