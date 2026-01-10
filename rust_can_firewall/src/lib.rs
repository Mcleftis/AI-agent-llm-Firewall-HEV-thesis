use pyo3::prelude::*;
use std::collections::HashSet;

// Βοηθητική συνάρτηση (ίδια με πριν)
fn get_allowed_ids() -> HashSet<u32> {
    let mut ids = HashSet::new();
    ids.insert(0x100); 
    ids.insert(0x200); 
    ids.insert(0x300); 
    ids.insert(0x400); 
    ids
}

// Η συνάρτηση που θα καλεί η Python
#[pyfunction]
fn inspect_packet(packet_id: u32, payload: &str) -> bool {
    let allowed_ids = get_allowed_ids();
    if !allowed_ids.contains(&packet_id) {
        return false;
    }

    let attack_patterns = vec![
        "DROP TABLE",
        "xxA1", 
        "OVERRIDE", 
        "ADMIN"
    ];

    for pattern in attack_patterns {
        if payload.contains(pattern) {
            return false;
        }
    }

    if payload.len() > 64 {
        return false; 
    }

    true
}

// ΕΔΩ ΕΙΝΑΙ Η ΑΛΛΑΓΗ (Bound API)
#[pymodule]
fn rust_can_firewall(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(inspect_packet, m)?)?;
    Ok(())
}