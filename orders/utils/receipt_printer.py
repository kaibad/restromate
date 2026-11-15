
from django.conf import settings
from escpos.printer import Network

from orders.models import OrderItem

import textwrap


def print_bill_receipt(bill):

    printer = None

    try:
        # ---------------------------------
        # CONNECT TO NETWORK PRINTER
        # ---------------------------------

        printer = Network(
            settings.PRINTER_IP,
            port=settings.PRINTER_PORT,
            timeout=settings.PRINTER_TIMEOUT,
        )

        # ---------------------------------
        # RECEIPT CONFIGURATION
        # ---------------------------------

        WIDTH = 32

        NAME_WIDTH = 12
        QTY_WIDTH = 3
        PRICE_WIDTH = 8
        TOTAL_WIDTH = 9

        # Use smaller font
        printer.set(
            font="b",
            bold=False,
            width=1,
            height=1,
            align="left",
        )

        # ---------------------------------
        # HELPER FUNCTIONS
        # ---------------------------------

        def separator():
            printer.text("-" * WIDTH + "\n")

        def center(text):
            printer.set(align="center")
            printer.text(str(text) + "\n")
            printer.set(align="left")

        def print_wrapped(text, width=WIDTH):
            lines = textwrap.wrap(
                str(text),
                width=width,
                break_long_words=True,
                break_on_hyphens=False,
            ) or [""]

            for line in lines:
                printer.text(line + "\n")

        # ---------------------------------
        # RESTAURANT HEADER
        # ---------------------------------

        printer.set(bold=True)
        center(settings.RESTAURANT_NAME)
        printer.set(bold=False)

        print_wrapped(settings.RESTAURANT_ADDRESS)

        printer.text("\n")

        print_wrapped(
            f"PAN: {settings.RESTAURANT_PAN}"
        )

        print_wrapped(
            f"VAT: {settings.RESTAURANT_VAT}"
        )

        separator()

        # ---------------------------------
        # BILL INFORMATION
        # ---------------------------------

        printer.set(bold=True)
        center("SALES RECEIPT")
        printer.set(bold=False)

        print_wrapped(
            f"Bill No: {str(bill.pk).upper()}"
        )

        print_wrapped(
            f"Table: {bill.table.name}"
        )

        print_wrapped(
            f"Date: {bill.paid_at.strftime('%d/%m/%Y %I:%M %p')}"
        )

        print_wrapped(
            f"Payment: {bill.get_method_display()}"
        )

        billed_by = (
            bill.billed_by.get_full_name()
            or bill.billed_by.username
        )

        print_wrapped(
            f"Billed by: {billed_by}"
        )

        separator()

        # ---------------------------------
        # FETCH ORDER ITEMS
        # ---------------------------------

        items = OrderItem.objects.filter(
            order__bill=bill
        ).select_related(
            "menu_item",
            "order",
        )

        combined_lines = {}

        for item in items:

            key = (
                item.menu_item.pk,
                item.price,
            )

            if key not in combined_lines:

                combined_lines[key] = {
                    "name": item.menu_item.name,
                    "quantity": 0,
                    "price": item.price,
                    "total": 0,
                }

            combined_lines[key]["quantity"] += item.quantity

            combined_lines[key]["total"] += item.line_total

        # ---------------------------------
        # ITEM TABLE
        # ---------------------------------

        printer.set(bold=True)

        printer.text(
            f"{'Item':<{NAME_WIDTH}}"
            f"{'Qty':>{QTY_WIDTH}}"
            f"{'Price':>{PRICE_WIDTH}}"
            f"{'Total':>{TOTAL_WIDTH}}\n"
        )

        printer.set(bold=False)

        separator()

        # ---------------------------------
        # PRINT EACH ITEM
        # ---------------------------------

        for line in combined_lines.values():

            name = line["name"]
            quantity = line["quantity"]
            price = line["price"]
            total = line["total"]

            # Wrap long item names
            name_lines = textwrap.wrap(
                name,
                width=NAME_WIDTH,
                break_long_words=True,
                break_on_hyphens=False,
            ) or [""]

            # First line with all columns
            first_line = (
                f"{name_lines[0]:<{NAME_WIDTH}}"
                f"{quantity:>{QTY_WIDTH}}"
                f"{price:>{PRICE_WIDTH},}"
                f"{total:>{TOTAL_WIDTH},}"
            )

            printer.text(first_line + "\n")

            # Remaining item name lines
            for extra_line in name_lines[1:]:
                printer.text(extra_line + "\n")

        separator()

        # ---------------------------------
        # GRAND TOTAL
        # ---------------------------------

        printer.set(bold=True)

        printer.text("GRAND TOTAL\n")

        print_wrapped(
            f"NRS {bill.total:,}"
        )

        printer.set(bold=False)

        separator()

        # ---------------------------------
        # FOOTER
        # ---------------------------------

        printer.text("\n")

        center("Thank you for visiting!")
        center("Please visit again!")

        printer.text("\n\n")

        # Cut receipt
        printer.cut()

        return True

    except Exception:
        raise

    finally:

        if printer is not None:
            printer.close()
