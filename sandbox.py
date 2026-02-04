from pyspark import pandas as ps

psdf = ps.DataFrame({"age": [5, 5, 2, 2],
        "name": ["Bob", "Bob", "Alice", "Alice"]}).set_index("age")