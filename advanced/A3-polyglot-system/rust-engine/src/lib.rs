use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct ScoreInput {
    pub amount: f64,
    pub merchant: String,
    pub country: String,
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub struct ScoreOutput {
    pub risk_score: u32,
    pub risk_level: String,
}

/// Home country for domestic vs foreign risk classification.
pub const HOME_COUNTRY: &str = "IN";

pub fn calculate_risk_score(input: &ScoreInput) -> ScoreOutput {
    let mut score: u32 = 0;

    if input.amount > 10_000.0 {
        score += 50;
    }
    if input.merchant.eq_ignore_ascii_case("electronics") {
        score += 20;
    }
    if !input.country.eq_ignore_ascii_case(HOME_COUNTRY) {
        score += 30;
    }
    if input.amount >= 15_000.0 {
        score += 12;
    }

    let risk_level = classify_risk_level(score);

    ScoreOutput {
        risk_score: score,
        risk_level: risk_level.to_string(),
    }
}

pub fn classify_risk_level(score: u32) -> &'static str {
    if score <= 30 {
        "LOW"
    } else if score <= 70 {
        "MEDIUM"
    } else {
        "HIGH"
    }
}

pub fn parse_input_json(raw: &str) -> Result<ScoreInput, String> {
    serde_json::from_str(raw).map_err(|err| format!("invalid JSON input: {err}"))
}

pub fn score_to_json(output: &ScoreOutput) -> Result<String, String> {
    serde_json::to_string(output).map_err(|err| format!("failed to serialize score: {err}"))
}
