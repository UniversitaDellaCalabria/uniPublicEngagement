import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from . settings import ATTACH_NAME_MAX_LEN, MAX_UPLOAD_SIZE, PERMITTED_UPLOAD_FILETYPE


def validate_file_extension(f):
    if hasattr(f.file, "content_type"):
        content_type = f.file.content_type
        if not content_type.lower() in PERMITTED_UPLOAD_FILETYPE:
            raise ValidationError(
                _('File extension not accepted: "{}". Enter {} only').format(
                    content_type,
                    PERMITTED_UPLOAD_FILETYPE,
                )
            )


def validate_file_size(f):
    if f.size > int(MAX_UPLOAD_SIZE):
        raise ValidationError(
            _("File size too large: {} bytes. Max {} bytes").format(
                f.size,
                MAX_UPLOAD_SIZE,
            )
        )


def validate_file_length(f):
    file_name = os.path.basename(f.name)
    if len(file_name) > ATTACH_NAME_MAX_LEN:
        raise ValidationError(
            _("File name length too large: {} characters. Max {} characters").format(
                len(file_name),
                ATTACH_NAME_MAX_LEN,
            )
        )
