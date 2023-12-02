from django.core.exceptions import ValidationError


def validate_file(value):
    # Validate that only PDB files are uploaded
    value= str(value)
    if value.endswith(".pdb") != True: 
        raise ValidationError("Only PDB Files can be uploaded. If unfamiliar with that file type check out our User Guide.")
    else:
        return value

