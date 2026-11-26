# Fix for Tuple Default Argument Parentheses Rendering Bug

## Root Cause
This bug occurs due to a known issue in **Sphinx 3.1.1** where default arguments that are tuples (e.g. `color=(1, 1, 1)`) lose their parentheses when rendered in HTML documentation, appearing as `color=1, 1, 1` instead.

This issue was tracked in Sphinx issue #7597 and **fixed in Sphinx version 3.2.0** released July 17, 2020.

## Fix
Upgrade your Sphinx dependency to version 3.2.0 or higher:

1. Open `requirements_docs.txt`
2. Change the Sphinx line from:
   ```
   sphinx==3.1.1
   ```
   to:
   ```
   sphinx>=3.2.0
   ```
   (Or use the latest stable version, e.g. `sphinx==7.1.2` as in the current PyVista main branch)

3. Reinstall the documentation dependencies:
   ```bash
   pip install -r requirements_docs.txt
   ```

4. Rebuild the documentation:
   ```bash
   cd docs && make clean && make html
   ```

## Verification
After applying the fix, the `add_lines` method signature will render correctly:
```
add_lines(lines, color=(1, 1, 1), width=5, label=None, name=None)
```

## Workaround (if you cannot upgrade Sphinx)
If upgrading Sphinx is not possible, you can explicitly document the default value in the parameter description:
```python
def add_lines(self, lines, color=(1, 1, 1), width=5, label=None, name=None):
    """Add lines.
    
    Parameters
    ----------
    color : tuple, default: (1, 1, 1)
        RGB color tuple for the lines.
    """
    pass
```
This ensures the correct default value is shown in the parameter list even if the signature rendering is broken.
