import datetime

from django.db import connection

from .models import Bill_number_generator


def bill_number_generator():
    # For Bill Number
    today = datetime.date.today()
    year = today.strftime("%Y")
    month = today.strftime("%m")

    # Last Bill Number
    last_bill = Bill_number_generator.objects.all().first()

    if last_bill:
        last_bill_number = str(last_bill.bill_number)[-4:]
        new_bill_number = str(int(last_bill_number) + 1).zfill(4)
    else:
        new_bill_number = "0001"
        bill_number = Bill_number_generator.objects.create(bill_number=f"{year}{month}{new_bill_number}")
        bill_number.save()

    return f"{year}{month}{new_bill_number}"


def get_dynamic_entries(customer_id, from_date, to_date, table_name):
    if not table_name.startswith("DailyEntry_"):
        raise ValueError("Invalid table name format")

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT id, customer_id, cooler, date_added, addedby, updatedby, original_entry_id
            FROM {table_name}
            WHERE customer_id = %s AND date_added BETWEEN %s AND %s
        """,
            [str(customer_id), from_date, to_date],
        )
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return rows
