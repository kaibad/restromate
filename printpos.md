# RestroMate – Receipt Printing Documentation

## 1. Overview

RestroMate uses python-escpos to print restaurant bills and receipts.

For development and testing, we use an ESC/POS virtual network printer instead of a physical receipt printer.

The virtual printer receives ESC/POS commands over TCP and converts them into HTML receipts that can be viewed in a browser.

Technologies used
Technology Purpose
Python Application programming language
Django Backend framework
python-escpos ESC/POS receipt printing
Docker Runs the virtual printer
ESC/POS Network Printer Emulator Simulates a thermal receipt printer
TCP Port 9100 Receives print jobs
Port 80 Displays printed receipts
Printing workflow
Billing staff opens a table.
Billing staff confirms payment.
Django creates a Bill record.
The bill is associated with its orders.
Billing staff clicks Print bill.
Django sends ESC/POS commands to the printer.
The printer processes the commands.
The emulator generates an HTML receipt.
The receipt can be viewed in the browser.

## 2. Install python-escpos

Official GitHub repository:

https://github.com/python-escpos/python-escpos

Documentation:

https://python-escpos.readthedocs.io/

## 3. Set up the virtual network printer

We use:

https://github.com/gilbertfl/escpos-netprinter

This project provides an ESC/POS network printer emulator.

It simulates an 80mm thermal receipt printer and converts received print jobs into HTML receipts.

Run using Docker

Install Docker if it is not already installed.

Run:

```bash
docker run -d \
 --name restromate-printer \
 -p 515:515/tcp \
 -p 8080:80/tcp \
 -p 9100:9100/tcp \
 --mount source=receiptVolume,target=/home/escpos-emu/web \
 gilbertfl/escpos-netprinter:3.3
```

We map the container's port 80 to host port 8080 to avoid conflicting with other applications.

Port configuration
Port Purpose
8080 Receipt viewer
9100 ESC/POS printing
515 LPD printing
Open the receipt viewer

Visit:

http://localhost:8080

All received receipts can be viewed through this interface.

Docker commands

Check whether the container is running:

bash
docker ps

View printer logs:

bash
docker logs restromate-printer

Stop the printer:

bash
docker stop restromate-printer

Start it again:

bash
docker start restromate-printer

Remove the container:

bash
docker rm -f restromate-printer

Note: The named Docker volume receiptVolume stores receipt history. Removing the container does not automatically remove this volume.

## 4. Configure Django settings

Open:

restromate/settings.py

Add the following configuration:

python

```
# RESTAURANT INFORMATION


RESTAURANT_NAME = "RestroMate"

RESTAURANT_ADDRESS = "Kathmandu, Nepal"

RESTAURANT_PAN = "YOUR-PAN-NUMBER"

RESTAURANT_VAT = "YOUR-VAT-NUMBER"

# ======================================

# ESC/POS PRINTER CONFIGURATION

# ======================================

PRINTER_MODE = "network"

PRINTER_IP = "127.0.0.1"

PRINTER_PORT = 9100

PRINTER_TIMEOUT = 10
```

Important:

PRINTER_IP is the address of the printer from Django's point of view.
PRINTER_PORT is the printer's TCP port.
PRINTER_TIMEOUT controls the connection timeout.
The restaurant details are printed on the receipt.

If Django runs inside Docker, 127.0.0.1 will refer to the Django container itself, not the printer container. In that case, use the printer container's reachable service name or network address.

## 5. Create the receipt printer utility

Create this file:

orders/receipt_printer.py

This file handles all communication with the ESC/POS printer.

It is responsible for:

Connecting to the printer.
Printing restaurant information.
Printing PAN and VAT numbers.
Printing bill information.
Retrieving order items.
Combining duplicate menu items.
Formatting item names and prices.
Printing the grand total.
Cutting the receipt.

The receipt uses a compact layout suitable for an 80mm printer.

The complete printing implementation is maintained in:

orders/receipt_printer.py

Use the latest version of the receipt printing function in that file.

Important formatting details

The receipt uses:

python
WIDTH = 32

NAME_WIDTH = 12
QTY_WIDTH = 3
PRICE_WIDTH = 8
TOTAL_WIDTH = 9

These widths are conservative formatting settings, not a guaranteed physical printer width.

The printer uses:

python
printer.set(
font="b",
bold=False,
width=1,
height=1,
align="left",
)

Font B is smaller than Font A on supported printers.

Long item names are wrapped using Python's textwrap module.

Receipt height is not fixed. The printer advances the paper as required.

## 6. Integrate printing into Django views

Open:

orders/views.py

Import the printing utility:

python
from orders.receipt_printer import print_bill_receipt

The bill printing function should receive an existing Bill object.

For example:

python
def print_existing_bill(request, bill_id):

    bill = get_object_or_404(
        Bill.objects.select_related(
            "table",
            "billed_by",
        ),
        pk=bill_id,
    )

    try:
        print_bill_receipt(bill)

        messages.success(
            request,
            "Receipt sent to printer successfully.",
        )

    except Exception as error:

        messages.error(
            request,
            f"Printer error: {error}",
        )

    return redirect(
        "billing_view_url",
        table_id=bill.table_id,
    )

Protect this view with the billing role decorator:

python
@role_required([User.ROLES_CHOICES.BILLING])

This endpoint should only print an existing bill. It must never create another bill or process another payment.

Add a URL in:

orders/urls.py

python
path(
"billing/print/<uuid:bill_id>/",
views.print_existing_bill,
name="print_existing_bill_url",
),

## 7. Update billing.html

Open:

orders/templates/orders/billing.html

Find the existing print button.

Replace:

HTML
<button
type="button"
onclick="window.print()"

>

    Print bill

</button>

With:

HTML
<a
href="{% url 'print_existing_bill_url' bill.id %}"
class="block w-full text-center bg-orange-600 text-white px-5 py-3 rounded-lg font-semibold hover:bg-orange-700"

>

    Print bill

</a>

This sends the existing bill to the ESC/POS printer instead of relying on browser printing.

The printer generates the receipt independently of the browser's print dialog.

8. Test the printer connection

Before testing a real bill, verify the connection.

Open the Django shell:

bash
python manage.py shell

Run:

python
from escpos.printer import Network

printer = Network(
"127.0.0.1",
port=9100,
timeout=10,
)

printer.text("RestroMate Printer Test\n")
printer.text("Connection successful!\n")

printer.cut()
printer.close()

Expected result:

The virtual printer should receive the test receipt.

Visit:

http://localhost:8080

You should see the newly received receipt.

9. Test an actual bill
   Start Docker.
   Start Django.
   Log in as billing staff.
   Open a table with a completed bill.
   Open its billing page.
   Click Print bill.
   Open the virtual printer viewer.

Verify the following:

Restaurant name.
Restaurant address.
PAN number.
VAT number.
Bill number.
Table name.
Payment method.
Date and time.
Item names.
Item quantities.
Individual item prices.
Item totals.
Grand total.

The printing process should not create another bill or modify payment records.

10. Troubleshooting
    Printer connection refused

Check the Docker container:

bash
docker ps

Check port availability:

bash
nc -vz 127.0.0.1 9100

Check Docker logs:

bash
docker logs restromate-printer

Settings attribute error

For example:

text
'Settings' object has no attribute 'RESTAURANT_NAME'

Check that the setting exists in the active Django settings file.

Use consistent spelling:

python
settings.RESTAURANT_NAME

Not:

python
settings.RESTUARANT_NAME

Receipt text overflows

Check the following:

Use Font B if supported.
Avoid enlarged font settings.
Reduce the column widths.
Reduce the receipt's character width.
Wrap long item names.
Check the printer profile.

Remember that actual printable character width depends on the printer font and profile.

Receipt viewer is unavailable

Visit:

http://localhost:8080

If unavailable, check:

bash
docker logs restromate-printer

Make sure port 8080 is not occupied by another application.

11. Switching to a physical network printer

When a physical ESC/POS-compatible network printer becomes available, the same printing implementation can be reused.

Change:

python
PRINTER_IP = "127.0.0.1"

To the actual printer's LAN IP address, for example:

python
PRINTER_IP = "192.168.1.100"

Keep:

python
PRINTER_PORT = 9100

If the physical printer uses a different port, update the setting accordingly.

The physical printer must support the ESC/POS commands used by the application and an appropriate printer profile should be configured when necessary.

No changes to the bill calculation or payment logic should be required.

12. Project file structure

The relevant project structure is:

text
restromate/
│
├── manage.py
│
├── requirements.txt
│
├── RECEIPT_PRINTING.md
│
├── restromate/
│ ├── settings.py
│ ├── urls.py
│ └── ...
│
└── orders/
│
├── models.py
├── views.py
├── urls.py
│
├── receipt_printer.py
│
└── templates/
└── orders/
└── billing.html

13. Security considerations
    Do not expose the virtual printer emulator to a public network.
    Keep the printer on a trusted local network.
    Restrict printing endpoints to authorized billing staff.
    Do not allow printing requests to create or modify payment records.
    Validate bill ownership and table relationships.
    Keep PAN and VAT information in Django settings rather than hardcoding it in multiple files.
    Protect the printer's network interface from unauthorized access.
14. References
    Python ESC/POS

https://github.com/python-escpos/python-escpos

Python ESC/POS Documentation

https://python-escpos.readthedocs.io/

ESC/POS Virtual Network Printer

https://github.com/gilbertfl/escpos-netprinter

Docker Hub Image

https://hub.docker.com/r/gilbertfl/escpos-netprinter

Conclusion

RestroMate currently uses python-escpos with an ESC/POS virtual network printer for receipt printing and development testing.

The virtual printer replaces a physical thermal printer during development.

When a physical network printer is purchased, the printer IP and, if necessary, printer profile can be updated without redesigning the billing system.

The receipt printing utility is kept separate from billing and payment logic to make future printer changes easier.
