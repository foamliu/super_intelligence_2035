import logging

def test_caplog_clear_consistency(caplog) -> None:
    def verify_consistency() -> None:
        assert caplog.get_records("call") == caplog.records

    verify_consistency()
    logging.warning("test")
    verify_consistency()
    assert len(caplog.records) == 1
    assert len(caplog.get_records("call")) == 1
    
    caplog.clear()
    
    verify_consistency()
    assert len(caplog.records) == 0
    assert len(caplog.get_records("call")) == 0
    
    # Test that new records are captured after clear
    logging.warning("test2")
    verify_consistency()
    assert len(caplog.records) == 1
    assert len(caplog.get_records("call")) == 1
    assert caplog.records[0].message == "test2"
