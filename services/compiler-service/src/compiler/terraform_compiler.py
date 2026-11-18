"""IR -> Terraform. Every resource is rendered from a vetted, secure-by-default template."""
from __future__ import annotations
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

TEMPLATES_DIR = Path(os.environ.get(
    "TEMPLATES_DIR",
    Path(__file__).resolve().parents[4] / "packages" / "tf-secure-templates" / "aws",
))

TYPE_TO_TEMPLATE = {
    "AWS::VPC": "vpc", "AWS::SG": "sg", "AWS::S3": "s3-secure",
    "AWS::RDS": "rds-private", "AWS::EC2": "ec2",
}
# Render order guarantees VPC objects are declared before consumers (purely cosmetic in TF).
ORDER = ["AWS::VPC", "AWS::SG", "AWS::S3", "AWS::RDS", "AWS::EC2"]

_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), undefined=StrictUndefined,
                   trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)


class CompileError(Exception):
    pass


def _resolve_vpc(res: dict, ir: dict) -> str | None:
    if res.get("vpc"):
        return res["vpc"]
    for d in res.get("dependencies", []):
        for r in ir["resources"]:
            if r["id"] == d and r["type"] == "AWS::VPC":
                return d
    vpcs = [r["id"] for r in ir["resources"] if r["type"] == "AWS::VPC"]
    return vpcs[0] if vpcs else None


def compile_ir_to_terraform(ir: dict) -> dict[str, str]:
    """Return {relative_path: file_content}. Pure function: no disk writes."""
    files: dict[str, str] = {}
    region = ir.get("metadata", {}).get("region", "eu-west-1")
    files["providers.tf"] = (
        'terraform {\n  required_version = ">= 1.6"\n  required_providers {\n'
        '    aws = { source = "hashicorp/aws", version = "~> 5.0" }\n  }\n}\n\n'
        f'provider "aws" {{\n  region = "{region}"\n}}\n'
    )
    main_parts, out_parts = [], []
    for t in ORDER:
        for res in [r for r in ir["resources"] if r["type"] == t]:
            tpl_dir = TYPE_TO_TEMPLATE.get(t)
            if not tpl_dir:
                raise CompileError(f"no template for {t}")
            ctx = dict(res)
            if t in ("AWS::SG", "AWS::RDS", "AWS::EC2"):
                ctx["vpc"] = _resolve_vpc(res, ir)
                if not ctx["vpc"]:
                    raise CompileError(f"{res['id']} requires a VPC in the IR")
            ctx.setdefault("tags", {})
            main_parts.append(_env.get_template(f"{tpl_dir}/main.tf.j2").render(**ctx))
            try:
                out_parts.append(_env.get_template(f"{tpl_dir}/outputs.tf.j2").render(**ctx))
            except Exception:
                pass
    files["main.tf"] = "\n".join(main_parts)
    files["outputs.tf"] = "\n".join(out_parts) or "# no outputs\n"
    return files


def write_project(files: dict[str, str], out_dir: str) -> None:
    root = Path(out_dir).resolve()
    for rel, content in files.items():
        dest = (root / rel).resolve()
        if root not in dest.parents:          # path-traversal guard
            raise CompileError(f"unsafe path {rel}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
