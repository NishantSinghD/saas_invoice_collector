from config.loader import load_vendor_aliases


def find_missing_vendors(expected_vendors, invoices):
    """Return expected vendors that were not found in the collected invoices."""

    vendor_aliases = load_vendor_aliases()

    collected_vendors = {
        invoice.vendor.strip().casefold()
        for invoice in invoices
    }

    missing_vendors = []

    for expected_vendor in expected_vendors:
        aliases = vendor_aliases.get(expected_vendor, [expected_vendor])

        normalized_aliases = {
            alias.strip().casefold()
            for alias in aliases
        }

        if not normalized_aliases.intersection(collected_vendors):
            missing_vendors.append(expected_vendor)

    return missing_vendors