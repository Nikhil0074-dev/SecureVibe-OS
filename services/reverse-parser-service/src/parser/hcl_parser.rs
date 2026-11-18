use hcl::Body;

/// Parse raw HCL (untrusted input: parsing only, nothing is executed).
pub fn parse(hcl_code: &str) -> Result<Body, String> {
    hcl::from_str::<Body>(hcl_code).map_err(|e| e.to_string())
}
