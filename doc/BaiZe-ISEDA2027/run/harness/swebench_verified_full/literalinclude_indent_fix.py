"""
Sphinx extension to fix literalinclude prepend/append leading whitespace issue.

Fixes two problems:
1. Preserves leading whitespace in prepend/append option values
2. Applies dedent only to the included content, not to prepend/append
"""
from docutils.parsers.rst import directives
from sphinx.directives.code import LiteralInclude as BaseLiteralInclude

class LiteralInclude(BaseLiteralInclude):
    def run(self):
        # Save original prepend/append values before docutils strips them
        # Workaround: we parse the raw directive text to get the full prepend/append with leading whitespace
        prepend = None
        append = None
        for line in self.block_text.split('\n'):
            line = line.strip()
            if line.startswith(':prepend:'):
                prepend = line[len(':prepend:'):]
                # Remove leading whitespace separator after option
                prepend = prepend[next(i for i, c in enumerate(prepend) if not c.isspace()):]
            elif line.startswith(':append:'):
                append = line[len(':append:'):]
                append = append[next(i for i, c in enumerate(append) if not c.isspace()):]
        
        # Get the original content first
        original_content = self.content
        original_dedent = self.options.get('dedent', 0)
        
        # Temporarily remove dedent option so parent class doesn't apply it to everything
        if 'dedent' in self.options:
            del self.options['dedent']
        
        # Run parent class to get the content without prepend/append? Wait no, let's do it step by step
        # Alternative approach: get the included lines first, apply dedent, then add prepend/append
        from sphinx.util import get_file_content
        
        source = self.get_source_info()[0]
        filename = self.arguments[0]
        rel_filename, filename = self.env.relfn2path(filename)
        self.env.note_dependency(rel_filename)
        
        lines = get_file_content(filename, source=source)
        
        # Apply start-at/end-at filtering
        if 'start-at' in self.options:
            start = self.options['start-at']
            for i, line in enumerate(lines):
                if start in line:
                    lines = lines[i:]
                    break
        if 'end-at' in self.options:
            end = self.options['end-at']
            for i, line in enumerate(lines):
                if end in line:
                    lines = lines[:i+1]
                    break
        if 'end-before' in self.options:
            end_before = self.options['end-before']
            for i, line in enumerate(lines):
                if end_before in line:
                    lines = lines[:i]
                    break
        
        # Apply dedent only to the included lines
        if original_dedent > 0:
            lines = [line[original_dedent:] if len(line) >= original_dedent else line for line in lines]
        
        # Add prepend and append with their original leading whitespace
        if prepend is not None:
            lines.insert(0, prepend + '\n')
        if append is not None:
            lines.append(append + '\n')
        
        # Now set the content to our modified lines
        self.content = [line.rstrip('\n') for line in lines]
        
        # Run the parent class with our modified content
        return super().run()

def setup(app):
    # Override the existing literalinclude directive
    app.add_directive('literalinclude', LiteralInclude, override=True)
    return {'version': '0.1', 'parallel_read_safe': True}
