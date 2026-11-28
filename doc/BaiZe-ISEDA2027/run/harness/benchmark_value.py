import timeit

setup = """
from django.db.models import Value
x = Value('test')
"""

stmt = "x._resolve_output_field()"

# Run benchmark
time = timeit.timeit(stmt, setup=setup, number=100000)
print(f"Time for 100k runs: {time:.3f}s")
print(f"Average per run: {time*1000/100000:.3f}µs")
