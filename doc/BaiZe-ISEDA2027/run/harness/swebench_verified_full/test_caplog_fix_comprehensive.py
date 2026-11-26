import logging

def test_caplog_clear_and_new_records(caplog) -> None:
    # Initial state: both empty
    assert caplog.get_records("call") == []
    assert caplog.records == []
    
    # Add a record
    logging.warning("test1")
    assert len(caplog.get_records("call")) == 1
    assert len(caplog.records) == 1
    assert caplog.get_records("call")[0].getMessage() == "test1"
    assert caplog.records[0].getMessage() == "test1"
    
    # Clear
    caplog.clear()
    assert caplog.get_records("call") == []
    assert caplog.records == []
    
    # Add another record after clear
    logging.warning("test2")
    assert len(caplog.get_records("call")) == 1
    assert len(caplog.records) == 1
    assert caplog.get_records("call")[0].getMessage() == "test2"
    assert caplog.records[0].getMessage() == "test2"
    
    # Clear again
    caplog.clear()
    assert caplog.get_records("call") == []
    assert caplog.records == []
    
    print("All tests passed!")
