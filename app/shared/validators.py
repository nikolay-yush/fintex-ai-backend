def validate_password_strength(value: str) -> str:
    has_letter = False
    has_digit = False

    for ch in value:
        if ch.isalpha():
            has_letter = True
        elif ch.isdigit():
            has_digit = True

        if has_letter and has_digit:
            break

    if not has_letter:
        raise ValueError(
            "Password must contain at least one letter."
        )

    if not has_digit:
        raise ValueError(
            "Password must contain at least one digit."
        )

    return value