from django.template import Engine, Context, TemplateSyntaxError
from django.template.library import Library

register = Library()

@register.simple_tag
def hello(*, greeting='hello'):
    return f'{greeting} world'

@register.simple_tag
def hi(*, greeting):
    return f'{greeting} world'

@register.inclusion_tag('test.html')
def include_hello(*, greeting='hello'):
    return {'greeting': greeting}

# Test engine
engine = Engine(debug=True, libraries={'test_tags': __name__})

# Test 1: simple tag with kwonly arg with default
print("Test 1: simple tag with kwonly arg with default")
try:
    t = engine.from_string('{% load test_tags %}{% hello greeting="hi" %}')
    result = t.render(Context({}))
    print(f"Result: {result}")
    assert result == 'hi world'
    print("✓ Passed")
except TemplateSyntaxError as e:
    print(f"✗ Failed: {e}")

# Test 2: simple tag with required kwonly arg
print("\nTest 2: simple tag with required kwonly arg")
try:
    t = engine.from_string('{% load test_tags %}{% hi greeting="hi" %}')
    result = t.render(Context({}))
    print(f"Result: {result}")
    assert result == 'hi world'
    print("✓ Passed")
except TemplateSyntaxError as e:
    print(f"✗ Failed: {e}")

# Test 3: duplicate kwonly arg raises multiple values error
print("\nTest 3: duplicate kwonly arg raises multiple values error")
try:
    t = engine.from_string('{% load test_tags %}{% hi greeting="hi" greeting="hello" %}')
    result = t.render(Context({}))
    print(f"✗ Failed: No error raised, result: {result}")
except TemplateSyntaxError as e:
    print(f"Error: {e}")
    if 'multiple values' in str(e):
        print("✓ Passed")
    else:
        print(f"✗ Wrong error message")

# Test 4: inclusion tag with kwonly arg with default
print("\nTest 4: inclusion tag with kwonly arg with default")
try:
    # Create a temporary template
    from django.template import Template
    t = engine.from_string('{% load test_tags %}{% include_hello greeting="hi" %}')
    # Mock the included template
    engine.from_string('{{ greeting }} world', name='test.html')
    result = t.render(Context({}))
    print(f"Result: {result}")
    assert result == 'hi world'
    print("✓ Passed")
except TemplateSyntaxError as e:
    print(f"✗ Failed: {e}")
