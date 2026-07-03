# PII Severity Reference

Use these tiers to classify every PII finding, whether it came from a deep
read or a scan script. Severity describes the harm if the value leaks, not
the confidence that the detection is correct.

## Critical — enables identity theft or carries legal exposure on its own

- Government-issued personal identifiers:
  - US Social Security number
  - CN resident identity card number (18 digits; the last digit is an
    ISO 7064 MOD 11-2 checksum)
  - JP My Number / Individual Number (12 digits with a check digit)
  - UK National Insurance number
  - passport numbers, driver's licence numbers, taxpayer IDs of any country
- Payment instruments: full card numbers (worse with expiry or CVV), bank
  account numbers, IBANs
- Biometric identifiers and medical record numbers
- A person's name combined with two or more other identifiers from any tier

## High — directly reaches or identifies a person

- Email addresses and phone numbers
- Full home or work addresses
- Complete dates of birth
- Login credentials (username and password together)
- IP addresses attributable to an individual

## Medium — sensitive in combination or by context

- A full name on its own
- Precise geolocation (GPS coordinates)
- Ethnic or racial origin, religious or political affiliation, sexual
  orientation, gender identity
- Health conditions, employment and education history
- CN Unified Social Credit Code (identifies an organization, not a person;
  treat as sensitive in business contexts, not as personal PII)

## Low — identifying only in aggregate

- Job title or department, age range, broad geographic region, nationality,
  publicly listed affiliations

## Applying the tiers

- **Combination raises severity.** Several Medium items describing the same
  person (birth date + postcode + gender) can jointly identify them; report
  the combination at the higher tier.
- **Checksum validity raises confidence.** An identifier that passes its
  national check-digit algorithm (Luhn, MOD 11-2, My Number check digit) is
  very unlikely to be an accidental digit run; treat such findings as
  high-confidence unless context proves otherwise.
- **Context can lower severity.** Clearly pseudonymized, synthetic, or
  documentation data is not a leak — but verify the claim; a real export
  labeled "sample" is still a finding.
