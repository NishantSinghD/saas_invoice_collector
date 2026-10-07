def find_missing_vendors(expected_vendors, invoices):
    """Return expected vendors for which no invoice was collected."""

    collected_vendors = {
        invoice.vendor.strip().casefold()
        for invoice in invoices
    }

    return [
        vendor
        for vendor in expected_vendors
        if vendor.strip().casefold() not in collected_vendors
    ]