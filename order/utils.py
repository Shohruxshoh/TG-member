# from django.db import connection
#
#
# def explain_analyze(queryset, label=None):
#     sql, params = queryset.query.sql_with_params()  # SQL va parametrlarni olish
#     vendor = connection.vendor  # 'postgresql', 'sqlite', 'mysql' ...
#
#     if vendor == "postgresql":
#         explain_sql = "EXPLAIN ANALYZE " + sql
#     elif vendor == "sqlite":
#         explain_sql = "EXPLAIN QUERY PLAN " + sql
#     else:
#         raise NotImplementedError(f"EXPLAIN ANALYZE {vendor} uchun hali qo‘shilmagan")
#
#     with connection.cursor() as cursor:
#         cursor.execute(explain_sql, params)  # paramlarni to‘g‘ri bog‘lab yuborish
#         result = "\n".join(str(row) for row in cursor.fetchall())
#
#     if label:
#         print(f"\n--- {label} ---")
#     print(result)
#     return result
