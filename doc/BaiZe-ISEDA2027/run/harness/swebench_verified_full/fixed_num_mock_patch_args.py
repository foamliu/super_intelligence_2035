def num_mock_patch_args(function):
    """ return number of arguments used up by mock arguments (if any) """
    patchings = getattr(function, "patchings", None)
    if not patchings:
        return 0
    mock_modules = [sys.modules.get("mock"), sys.modules.get("unittest.mock")]
    if any(mock_modules):
        sentinels = [m.DEFAULT for m in mock_modules if m is not None]
        # Fix: use identity check instead of 'in' to avoid numpy array comparison issues
        return len([p for p in patchings
                    if not p.attribute_name and any(p.new is s for s in sentinels)])
    return len(patchings)
