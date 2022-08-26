use std::collections::HashMap;
use rand::seq::SliceRandom;


use pyo3::{
    pymodule,
    types::{PyModule, PyString, PyDict},
    PyResult, Python,
};


#[pymodule]
fn markov(_py: Python, m: &PyModule) -> PyResult<()> {


    fn predict(
        markov_chain: HashMap<Vec<String>, Vec<String>>, n_words: i32, prompt: String
    ) -> String {
        let short_chain = short_prefix_chain(&markov_chain);
        let words: Vec<String> = short_chain.keys().map(|s| s.to_string()).collect();
        let n_prefix = markov_chain.keys().nth(0).expect("prefixes are not formed").len();
        let mut output: Vec<String> = prompt.split_whitespace().map(|s| s.to_string()).collect();


        for _ in 0..n_words {
            if output.len() >= n_prefix {
                let prefix: Vec<String> = output.as_slice()[output.len() - n_prefix..].to_vec();
                if markov_chain.contains_key(&prefix) {
                    output.push(markov_chain[&prefix]
                        .choose(&mut rand::thread_rng())
                        .unwrap()
                        .clone());
                }
                else {
                    let prefix = output.iter().last().unwrap().clone();
                    output.push(match short_chain.get(&prefix) {
                        Some(pred) => pred.choose(&mut rand::thread_rng()).unwrap().clone(),
                        None => words.choose(&mut rand::thread_rng()).unwrap().clone()
                    }
                )
                }
            }
            else {
                output.push(words.choose(&mut rand::thread_rng()).unwrap().clone())
            }


        }
        output.join(" ")
    }

    fn update_chain(line: String, mut chain: HashMap<Vec<String>, Vec<String>>, n_prefix: usize) -> HashMap<Vec<String>, Vec<String>> {
        let words: Vec<String> = line.split_whitespace().map(|s| s.to_string()).collect();
        if words.len() < (n_prefix + 1) {
            return chain
        }
        for i in n_prefix..words.len() {
            let prefix = Vec::from(&words[(i - n_prefix)..i]);
            let prediction = &words[i];
            chain.entry(prefix).and_modify(|pred| pred.push(prediction.to_string())).or_insert(vec![prediction.to_string()]);
        }
        chain
    }


    // wrapper
    #[pyfn(m)]
    #[pyo3(name = "predict")]
    fn predict_py<'py>(
        _py: Python<'py>,
        markov_chain: &PyDict,
        n_words: i32,
        prompt: &PyString,
    ) -> PyResult<String>{
        let markov_chain = markov_chain.extract()?;
        let prompt = prompt.extract()?;

        let output = predict(markov_chain, n_words, prompt);
        Ok(output)
    }

    Ok(())
}

/// Generate a chain from the last element in the prefix to the list of possibilities.
fn short_prefix_chain(chain: &HashMap<Vec<String>, Vec<String>>) -> HashMap<String, Vec<String>> {
    let mut short_prefix: HashMap<String,Vec<String>> = HashMap::new();
    for (prefix, postfix) in chain.iter() {
        let last = prefix.iter().last().expect("Missing prefix").to_string();
        short_prefix.entry(last)
            .and_modify(|pred| pred.extend(postfix.iter().cloned()))
            .or_insert(postfix.to_vec());
    }
    short_prefix
}
