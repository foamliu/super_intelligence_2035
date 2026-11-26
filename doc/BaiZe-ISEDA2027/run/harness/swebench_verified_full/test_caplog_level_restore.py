def test_foo(caplog):
    caplog.set_level(42)

def test_bar(caplog):
    print(f"caplog.handler.level = {caplog.handler.level}")
    assert caplog.handler.level == 0, f"Expected level 0, got {caplog.handler.level}"
