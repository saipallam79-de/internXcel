import secrets


def make_intern_id(year: int, sequence: int) -> str:
    return f"INTX/{year}/{sequence:06d}"


def make_unique_intern_id(year: int) -> str:
    return make_intern_id(year, secrets.randbelow(999999) + 1)


def make_certificate_id(year: int, sequence: int) -> str:
    return f"INTX-CERT-{year}-{sequence:06d}"


def make_lor_id(year: int, sequence: int) -> str:
    return f"INTX-LOR-{year}-{sequence:06d}"
