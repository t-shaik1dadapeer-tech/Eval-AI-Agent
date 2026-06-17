use fraud_engine::{calculate_risk_score, ScoreInput};

fn input(amount: f64, merchant: &str, country: &str) -> ScoreInput {
    ScoreInput {
        amount,
        merchant: merchant.to_string(),
        country: country.to_string(),
    }
}

#[test]
fn low_risk_score() {
    let result = calculate_risk_score(&input(500.0, "grocery", "IN"));
    assert_eq!(result.risk_score, 0);
    assert_eq!(result.risk_level, "LOW");
}

#[test]
fn medium_risk_score() {
    let result = calculate_risk_score(&input(11_000.0, "grocery", "IN"));
    assert_eq!(result.risk_score, 50);
    assert_eq!(result.risk_level, "MEDIUM");
}

#[test]
fn high_risk_score() {
    let result = calculate_risk_score(&input(15_000.0, "electronics", "IN"));
    assert_eq!(result.risk_score, 82);
    assert_eq!(result.risk_level, "HIGH");
}
