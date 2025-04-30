import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from template.settings import PDF_FILETYPE, IMG_FILETYPE


def validate_poster_extension(f):
    allowed_extensions = PDF_FILETYPE + IMG_FILETYPE
    if hasattr(f.file, "content_type"):
        content_type = f.file.content_type
        if not content_type.lower() in allowed_extensions:
            raise ValidationError(
                _('File extension not accepted: "{}". Enter {} only').format(
                    content_type,
                    allowed_extensions,
                )
            )
