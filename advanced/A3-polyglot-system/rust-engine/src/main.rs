use fraud_engine::{calculate_risk_score, parse_input_json, score_to_json};
use std::io::{self, Read};

fn main() {
    let exit_code = run();
    std::process::exit(exit_code);
}

fn run() -> i32 {
    let input = match read_input() {
        Ok(value) => value,
        Err(message) => {
            eprintln!("{message}");
            return 1;
        }
    };

    let parsed = match parse_input_json(&input) {
        Ok(value) => value,
        Err(message) => {
            eprintln!("{message}");
            return 1;
        }
    };

    let score = calculate_risk_score(&parsed);

    match score_to_json(&score) {
        Ok(json) => {
            println!("{json}");
            0
        }
        Err(message) => {
            eprintln!("{message}");
            1
        }
    }
}

fn read_input() -> Result<String, String> {
    let mut args: Vec<String> = std::env::args().skip(1).collect();
    if args.is_empty() {
        let mut buffer = String::new();
        io::stdin()
            .read_to_string(&mut buffer)
            .map_err(|err| format!("failed to read stdin: {err}"))?;
        if buffer.trim().is_empty() {
            return Err("no input provided; pass JSON as argument or stdin".to_string());
        }
        return Ok(buffer);
    }

    if args.len() == 1 {
        return Ok(args.remove(0));
    }

    Ok(args.join(" "))
}
