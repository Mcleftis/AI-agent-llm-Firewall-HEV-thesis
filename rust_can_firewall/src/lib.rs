use pyo3::prelude::*;
use std::sync::atomic::{AtomicUsize, Ordering};

// Παγκόσμιος Μετρητής (Global Counter)
static BLOCKED_COUNT: AtomicUsize = AtomicUsize::new(0);

/// 1. ΠΑΛΙΑ ΣΥΝΑΡΤΗΣΗ: Ελέγχει πακέτα (Passive Monitor)
/// Επιστρέφει True/False, αλλά δεν αλλάζει τα δεδομένα.
#[pyfunction]
fn inspect_packet(packet_id: u32, payload: String) -> bool {
    if payload.contains("DROP") || payload.contains("DELETE") || payload.contains("fuzz") {
        BLOCKED_COUNT.fetch_add(1, Ordering::Relaxed);
        return false;
    }
    if packet_id == 0x666 || packet_id > 0x7FF {
        BLOCKED_COUNT.fetch_add(1, Ordering::Relaxed);
        return false;
    }
    true
}

/// 2. ΝΕΑ ΣΥΝΑΡΤΗΣΗ: Φιλτράρει Εντολές (Active Safety) 🛡️
/// Αυτή μπαίνει "σφήνα" πριν εκτελεστεί η εντολή.
/// Αν είναι επικίνδυνη, επιστρέφει None (null).
/// Αν είναι ασφαλής, επιστρέφει την εντολή (Some).
#[pyfunction]
fn sanitize_command(command: String) -> Option<String> {
    // Λίστα απαγορευμένων εντολών (Safety Rules)
    // 1. Κόβουμε τέρμα γκάζι (Safety)
    // 2. Κόβουμε SQL Injection (Security)
    if command.contains("MAX_THROTTLE") || command.contains("DROP") || command.contains("fuzz") {
        // Καταγράφουμε την επίθεση
        BLOCKED_COUNT.fetch_add(1, Ordering::Relaxed);
        // Επιστρέφουμε ΤΙΠΟΤΑ (μπλοκάρισμα)
        return None; 
    }
    
    // Αν όλα είναι καθαρά, αφήνουμε την εντολή να περάσει
    Some(command)
}

/// 3. ΣΥΝΑΡΤΗΣΗ ΣΤΑΤΙΣΤΙΚΩΝ
#[pyfunction]
fn get_firewall_stats() -> usize {
    BLOCKED_COUNT.load(Ordering::Relaxed)
}

/// ΤΟ MODULE ΠΟΥ ΒΛΕΠΕΙ Η PYTHON
#[pymodule]
fn rust_can_firewall(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(inspect_packet, m)?)?;
    m.add_function(wrap_pyfunction!(get_firewall_stats, m)?)?;
    
    // ΠΡΟΣΟΧΗ: Προσθέσαμε και την καινούργια εδώ!
    m.add_function(wrap_pyfunction!(sanitize_command, m)?)?; 
    
    Ok(())
}