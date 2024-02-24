import random

def generate_saudi_vat_number():
    # Generate a random 10-digit core VAT identification
    core_vat_identification = ''.join([str(random.randint(0, 9)) for _ in range(10)])

    # Fixed prefix for Saudi Arabian VAT numbers
    prefix = "030"

    # Combine core identification, prefix, and calculate check digits
    vat_number_without_check_digits = core_vat_identification + prefix
    check_digits = calculate_check_digits(vat_number_without_check_digits)

    # Combine to form the complete VAT number
    saudi_vat_number = vat_number_without_check_digits + check_digits

    return saudi_vat_number

def calculate_check_digits(vat_number_without_check_digits):
    # Convert the 13-digit number to an integer
    num = int(vat_number_without_check_digits)

    # Perform the Modulus 97-10 calculation
    remainder = num % 97
    check_digits = str(97 - remainder)

    # Ensure the check digits are two digits (pad with leading zero if needed)
    return check_digits.zfill(2)

# Example usage
generated_vat_number = generate_saudi_vat_number()
print(f"Hypothetical Saudi Arabian VAT Number: {generated_vat_number}")