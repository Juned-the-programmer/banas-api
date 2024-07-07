from .models import Bill_number_generator
import datetime

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
        bill_number = Bill_number_generator.objects.create(
            bill_number = f"{year}{month}{new_bill_number}"
        )
        bill_number.save()

    return f"{year}{month}{new_bill_number}"