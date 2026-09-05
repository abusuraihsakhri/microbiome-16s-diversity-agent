"""
Automated Pytest Test Suite for Microbiome 16S Diversity Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import csv
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    text = "Contact patient MRN-12345678 for follow-up"
    redacted = PHIGuard.redact_phi(text)
    assert "MRN" not in redacted or "REDACTED" in redacted
    assert "12345678" not in redacted


def test_phi_guard_detects_ssn():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient SSN 123-45-6789 registered")


def test_phi_guard_detects_email():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Send results to doctor@hospital.org")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_integrity_tampering():
    """Verify that tampering with the audit trail is detected."""
    trail = AuditTrail(secret_key="test-key-for-integrity")
    trail.log("test-actor", "tester", "TEST_EVENT", {"data": "value1"})
    trail.log("test-actor", "tester", "TEST_EVENT", {"data": "value2"})
    assert trail.verify_integrity() is True

    # Tamper with an entry
    if trail.logs:
        trail.logs[0]["payload_hash"] = "tampered_hash"
    assert trail.verify_integrity() is False


def test_batch_processing_with_valid_csv():
    """Test batch processing handles valid CSV correctly."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "target_identifier", "primary_metric", "secondary_metric", "is_critical_flag", "status_descriptor"])
        writer.writeheader()
        # Row 1: critical flag + discordant status => CRITICAL_STAT_PANIC
        writer.writerow({
            "task_id": "BATCH-001",
            "target_identifier": "TARGET-B1",
            "primary_metric": "28.4",
            "secondary_metric": "14.2",
            "is_critical_flag": "True",
            "status_descriptor": "DISCORDANT"
        })
        # Row 2: nominal values => ROUTINE
        writer.writerow({
            "task_id": "BATCH-002",
            "target_identifier": "TARGET-B2",
            "primary_metric": "12.0",
            "secondary_metric": "4.1",
            "is_critical_flag": "False",
            "status_descriptor": "NOMINAL"
        })
        input_path = f.name

    output_path = input_path + "_output.csv"
    try:
        result = main(["batch", "-i", input_path, "-o", output_path])
        assert result == 0
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            # Critical flag triggers CRITICAL_STAT_PANIC
            assert rows[0]["overall_urgency"] == "CRITICAL_STAT_PANIC"
            assert rows[1]["overall_urgency"] == "ROUTINE"
    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_batch_processing_with_missing_file():
    """Test batch processing handles missing input file gracefully."""
    result = main(["batch", "-i", "/nonexistent/path/file.csv"])
    assert result == 1


def test_batch_processing_with_malformed_csv():
    """Test batch processing skips malformed rows gracefully."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "target_identifier", "primary_metric", "secondary_metric", "is_critical_flag", "status_descriptor"])
        writer.writeheader()
        writer.writerow({
            "task_id": "BATCH-001",
            "target_identifier": "TARGET-B1",
            "primary_metric": "28.4",
            "secondary_metric": "14.2",
            "is_critical_flag": "True",
            "status_descriptor": "DISCORDANT"
        })
        # Malformed row with invalid numeric value
        writer.writerow({
            "task_id": "BATCH-002",
            "target_identifier": "TARGET-B2",
            "primary_metric": "not_a_number",
            "secondary_metric": "4.1",
            "is_critical_flag": "False",
            "status_descriptor": "NOMINAL"
        })
        input_path = f.name

    output_path = input_path + "_output.csv"
    try:
        result = main(["batch", "-i", input_path, "-o", output_path])
        assert result == 0
        with open(output_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Only the valid row should be processed
            assert len(rows) == 1
            assert rows[0]["task_id"] == "BATCH-001"
    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_supervisor_blocks_phi_in_task_id():
    """Test that supervisor rejects PHI-containing task IDs."""
    supervisor = SystemSupervisor(model_provider="mock")
    with pytest.raises(SecurityException):
        payload = SystemTaskPayload(
            task_id="Patient MRN-12345678",
            target_identifier="KEY-01",
            primary_metric=12.0,
        )
        supervisor.process_task(payload)
