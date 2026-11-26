
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'django'))

# Mock a connection for PostgreSQL
class MockPostgreSQLConnection:
    vendor = 'postgresql'

# Mock a compiler
class MockCompiler:
    def compile(self, child):
        # Child is a tuple like ('id = %s', [37])
        return child

from django.db.models.query_utils import Q
from django.db.models.sql.where import WhereNode

print("Testing XOR fix...")

# Test 1: Q(id=37) ^ Q(id=37)
q1 = Q(id=37)
q2 = Q(id=37)
q_xor_2 = q1 ^ q2
print(f"\nQ(id=37) ^ Q(id=37): {q_xor_2}")

# Convert to WhereNode
where_node = WhereNode([q_xor_2.children[0], q_xor_2.children[1]], connector=q_xor_2.connector, negated=q_xor_2.negated)
sql, params = where_node.as_sql(MockCompiler(), MockPostgreSQLConnection())
print(f"Generated SQL (PostgreSQL): {sql}")
print(f"Params: {params}")
# Should be ((CASE WHEN id = %s THEN 1 ELSE 0 END + CASE WHEN id = %s THEN 1 ELSE 0 END) % 2 = 1)
# Which for values 37,37 gives (1+1) %2 = 0 → 0=1 → false, correct.

# Test 2: Q(id=37) ^ Q(id=37) ^ Q(id=37)
q_xor_3 = q1 ^ q2 ^ q1
print(f"\nQ(id=37) ^ Q(id=37) ^ Q(id=37): {q_xor_3}")

where_node_3 = WhereNode(q_xor_3.children, connector=q_xor_3.connector, negated=q_xor_3.negated)
sql_3, params_3 = where_node_3.as_sql(MockCompiler(), MockPostgreSQLConnection())
print(f"Generated SQL (PostgreSQL): {sql_3}")
print(f"Params: {params_3}")
# Should be ((CASE WHEN id = %s THEN 1 ELSE 0 END + CASE WHEN id = %s THEN 1 ELSE 0 END + CASE WHEN id = %s THEN 1 ELSE 0 END) % 2 = 1)
# Which for 37,37,37 gives 1+1+1=3 → 3%2=1 → true, correct.

# Test 3: 4 XORs
q_xor_4 = q1 ^ q2 ^ q1 ^ q2
where_node_4 = WhereNode(q_xor_4.children, connector=q_xor_4.connector, negated=q_xor_4.negated)
sql_4, params_4 = where_node_4.as_sql(MockCompiler(), MockPostgreSQLConnection())
print(f"\n4 XORs SQL: {sql_4}")
# Sum 1+1+1+1=4 → 4%2=0 → false, correct.

# Test MySQL
class MockMySQLConnection:
    vendor = 'mysql'

sql_mysql, params_mysql = where_node_3.as_sql(MockCompiler(), MockMySQLConnection())
print(f"\n3 XORs SQL (MySQL): {sql_mysql}")
# Should be (id = %s XOR id = %s XOR id = %s)
