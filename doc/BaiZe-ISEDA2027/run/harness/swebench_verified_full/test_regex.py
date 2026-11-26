import re

original_re = re.compile(
    r'^'
    r'(?:(?P<days>-?\d+) (days?, )?)?'
    r'((?:(?P<hours>-?\d+):)(?=\d+:\d+))?'
    r'(?:(?P<minutes>-?\d+):)?'
    r'(?P<seconds>-?\d+)'
    r'(?:\.(?P<microseconds>\d{1,6})\d{0,6})?'
    r'$'
)

fixed_re = re.compile(
    r'^'
    r'(?:(?P<days>-?\d+) (days?, )?)?'
    r'((?:(?P<hours>-?\d+):)(?=-?\d+:-?\d+))?'
    r'(?:(?P<minutes>-?\d+):)?'
    r'(?P<seconds>-?\d+)'
    r'(?:\.(?P<microseconds>\d{1,6})\d{0,6})?'
    r'$'
)

test_str = "-1:30:45"
print(f"Testing '{test_str}':")
print(f"Original regex match: {original_re.match(test_str)}")
print(f"Fixed regex match: {fixed_re.match(test_str)}")
if fixed_re.match(test_str):
    print(f"Groups: {fixed_re.match(test_str).groupdict()}")
