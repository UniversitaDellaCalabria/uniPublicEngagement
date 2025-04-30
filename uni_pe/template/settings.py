from django.conf import settings
from django.utils.translation import gettext as _


PDF_FILETYPE = getattr(settings,
                       "PDF_FILETYPE",
                       ['application/pdf']
                )
DATA_FILETYPE = getattr(settings,
                        "DATA_FILETYPE",
                        ['text/csv', 'application/json',
                         'application/vnd.ms-excel',
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         'application/vnd.oasis.opendocument.spreadsheet',
                         'application/wps-office.xls']
                        )
TEXT_FILETYPE = getattr(settings,
                        "TEXT_FILETYPE",
                        ['text/plain',
                         'application/vnd.oasis.opendocument.text',
                         'application/msword',
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document'])
IMG_FILETYPE = getattr(settings, "IMG_FILETYPE", ['image/jpeg', 'image/png', 'image/gif', 'image/x-ms-bmp'])
P7M_FILETYPE = getattr(settings, "P7M_FILETYPE", ['application/pkcs7-mime'])

PERMITTED_UPLOAD_FILETYPE = PDF_FILETYPE + TEXT_FILETYPE + DATA_FILETYPE + IMG_FILETYPE + P7M_FILETYPE

# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_UPLOAD_SIZE = getattr(settings, "MAX_UPLOAD_SIZE", 10485760)

ATTACH_NAME_MAX_LEN = 200

# E-mail messages
MSG_HEADER = getattr(
    settings,
    "MSG_HEADER",
    _(
        """Dear user,
this message was sent by {}.
Please do not reply to this email.

-------------------

"""
    ).format(settings.DEFAULT_HOST),
)

MSG_FOOTER = getattr(
    settings,
    "MSG_FOOTER",
    _(
        """

-------------------

For technical problems contact our staff.
Best regards.
"""
    ),
)
