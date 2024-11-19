import logging
import os

from django.conf import settings
from django.utils.module_loading import import_string as get_storage_class
from django.utils.translation import gettext_lazy as _

from .utils.loader import load_object
from .utils.recursive_dictionary import RecursiveDictionaryWithExcludes


logger = logging.getLogger(__name__)

# FILER_IMAGE_MODEL setting is used to swap Image model.
# If such global setting does not exist, it will be created at this point (with default model name).
# This is needed especially when using this setting in migrations.
if not hasattr(settings, 'FILER_IMAGE_MODEL'):
    setattr(settings, 'FILER_IMAGE_MODEL', 'filer.Image')
FILER_IMAGE_MODEL = settings.FILER_IMAGE_MODEL

FILER_DEBUG = getattr(settings, 'FILER_DEBUG', False)  # When True makes
FILER_SUBJECT_LOCATION_IMAGE_DEBUG = getattr(settings, 'FILER_SUBJECT_LOCATION_IMAGE_DEBUG', False)
FILER_WHITESPACE_COLOR = getattr(settings, 'FILER_WHITESPACE_COLOR', '#FFFFFF')

FILER_0_8_COMPATIBILITY_MODE = getattr(settings, 'FILER_0_8_COMPATIBILITY_MODE', False)

FILER_ENABLE_LOGGING = getattr(settings, 'FILER_ENABLE_LOGGING', False)
if FILER_ENABLE_LOGGING:
    FILER_ENABLE_LOGGING = (
        FILER_ENABLE_LOGGING and (getattr(settings, 'LOGGING')
                             and ('' in settings.LOGGING['loggers']
                             or 'filer' in settings.LOGGING['loggers'])))

FILER_ENABLE_PERMISSIONS = getattr(settings, 'FILER_ENABLE_PERMISSIONS', False)
FILER_ALLOW_REGULAR_USERS_TO_ADD_ROOT_FOLDERS = getattr(settings, 'FILER_ALLOW_REGULAR_USERS_TO_ADD_ROOT_FOLDERS', False)
FILER_IS_PUBLIC_DEFAULT = getattr(settings, 'FILER_IS_PUBLIC_DEFAULT', True)

FILER_PAGINATE_BY = getattr(settings, 'FILER_PAGINATE_BY', 100)

if hasattr(settings, "FILER_ADMIN_ICON_SIZES"):
    logger.warning("FILER_ADMIN_ICON_SIZES is deprecated and will be removed in the future.")

_ICON_SIZES = getattr(settings, 'FILER_ADMIN_ICON_SIZES', ('16', '32', '48', '64'))
# Reliably sort by integer value, but keep icon size as string.
# (There is some code in the wild that depends on this being strings.)
FILER_ADMIN_ICON_SIZES = [str(i) for i in sorted([int(s) for s in _ICON_SIZES])]

# Currently, these two icon sizes are hard-coded into the admin and admin templates
FILER_TABLE_ICON_SIZE = getattr(settings, "FILER_TABLE_ICON_SIZE", 40)
FILER_THUMBNAIL_ICON_SIZE = getattr(settings, "FILER_THUMBNAIL_ICON_SIZE", 120)
DEFERRED_THUMBNAIL_SIZES = (
    FILER_TABLE_ICON_SIZE,
    2 * FILER_TABLE_ICON_SIZE,
    FILER_THUMBNAIL_ICON_SIZE,
    2 * FILER_THUMBNAIL_ICON_SIZE,
)


# This is an ordered iterable that describes a list of
# classes that I should check for when adding files
FILER_FILE_MODELS = getattr(
    settings, 'FILER_FILE_MODELS',
    (FILER_IMAGE_MODEL, 'filer.File'))

if hasattr(settings, "STORAGES") and 'default' in settings.STORAGES:
    DEFAULT_FILE_STORAGE = settings.STORAGES['default'].get('BACKEND', 'django.core.files.storage.FileSystemStorage')
else:
    DEFAULT_FILE_STORAGE = getattr(settings, 'DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')

MINIMAL_FILER_STORAGES = {
    'public': {
        'main': {
            'ENGINE': None,
            'OPTIONS': {},
        },
        'thumbnails': {
            'ENGINE': None,
            'OPTIONS': {},
        }
    },
    'private': {
        'main': {
            'ENGINE': None,
            'OPTIONS': {},
        },
        'thumbnails': {
            'ENGINE': None,
            'OPTIONS': {},
        },
    },
}


DEFAULT_FILER_STORAGES = {
    'public': {
        'main': {
            'ENGINE': DEFAULT_FILE_STORAGE,
            'OPTIONS': {},
            'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
            'UPLOAD_TO_PREFIX': 'filer_public',
        },
        'thumbnails': {
            'ENGINE': DEFAULT_FILE_STORAGE,
            'OPTIONS': {},
            'THUMBNAIL_OPTIONS': {
                'base_dir': 'filer_public_thumbnails',
            },
        },
    },
    'private': {
        'main': {
            'ENGINE': 'filer.storage.PrivateFileSystemStorage',
            'OPTIONS': {
                'location': os.path.abspath(os.path.join(settings.MEDIA_ROOT, '../smedia/filer_private')),
                'base_url': '/smedia/filer_private/',
            },
            'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
            'UPLOAD_TO_PREFIX': '',
        },
        'thumbnails': {
            'ENGINE': 'filer.storage.PrivateFileSystemStorage',
            'OPTIONS': {
                'location': os.path.abspath(os.path.join(settings.MEDIA_ROOT, '../smedia/filer_private_thumbnails')),
                'base_url': '/smedia/filer_private_thumbnails/',
            },
            'THUMBNAIL_OPTIONS': {},
        },
    },
}

MINIMAL_FILER_SERVERS = {
    'private': {
        'main': {
            'ENGINE': None,
            'OPTIONS': {},
        },
        'thumbnails': {
            'ENGINE': None,
            'OPTIONS': {},
        },
    },
}

DEFAULT_FILER_SERVERS = {
    'private': {
        'main': {
            'ENGINE': 'filer.server.backends.default.DefaultServer',
            'OPTIONS': {},
        },
        'thumbnails': {
            'ENGINE': 'filer.server.backends.default.DefaultServer',
            'OPTIONS': {},
        },
    },
}

FILER_STORAGES = RecursiveDictionaryWithExcludes(MINIMAL_FILER_STORAGES, rec_excluded_keys=('OPTIONS', 'THUMBNAIL_OPTIONS'))
if FILER_0_8_COMPATIBILITY_MODE:
    user_filer_storages = {
        'public': {
            'main': {
                'ENGINE': DEFAULT_FILE_STORAGE,
                'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
                'UPLOAD_TO_PREFIX': getattr(settings, 'FILER_PUBLICMEDIA_PREFIX', 'filer_public'),
            },
            'thumbnails': {
                'ENGINE': DEFAULT_FILE_STORAGE,
                'OPTIONS': {},
                'THUMBNAIL_OPTIONS': {
                    'base_dir': 'filer_public_thumbnails',
                },
            },
        },
        'private': {
            'main': {
                'ENGINE': DEFAULT_FILE_STORAGE,
                'UPLOAD_TO': 'filer.utils.generate_filename.randomized',
                'UPLOAD_TO_PREFIX': getattr(settings, 'FILER_PRIVATEMEDIA_PREFIX', 'filer_private'),
            },
            'thumbnails': {
                'ENGINE': DEFAULT_FILE_STORAGE,
                'OPTIONS': {},
                'THUMBNAIL_OPTIONS': {
                    'base_dir': 'filer_private_thumbnails',
                },
            },
        },
    }
else:
    user_filer_storages = getattr(settings, 'FILER_STORAGES', {})

FILER_STORAGES.rec_update(user_filer_storages)


def update_storage_settings(user_settings, defaults, s, t):
    if not user_settings[s][t]['ENGINE']:
        user_settings[s][t]['ENGINE'] = defaults[s][t]['ENGINE']
        user_settings[s][t]['OPTIONS'] = defaults[s][t]['OPTIONS']
    if t == 'main':
        if 'UPLOAD_TO' not in user_settings[s][t]:
            user_settings[s][t]['UPLOAD_TO'] = defaults[s][t]['UPLOAD_TO']
        if 'UPLOAD_TO_PREFIX' not in user_settings[s][t]:
            user_settings[s][t]['UPLOAD_TO_PREFIX'] = defaults[s][t]['UPLOAD_TO_PREFIX']
    if t == 'thumbnails':
        if 'THUMBNAIL_OPTIONS' not in user_settings[s][t]:
            user_settings[s][t]['THUMBNAIL_OPTIONS'] = defaults[s][t]['THUMBNAIL_OPTIONS']
    return user_settings


update_storage_settings(FILER_STORAGES, DEFAULT_FILER_STORAGES, 'public', 'main')
update_storage_settings(FILER_STORAGES, DEFAULT_FILER_STORAGES, 'public', 'thumbnails')
update_storage_settings(FILER_STORAGES, DEFAULT_FILER_STORAGES, 'private', 'main')
update_storage_settings(FILER_STORAGES, DEFAULT_FILER_STORAGES, 'private', 'thumbnails')

FILER_SERVERS = RecursiveDictionaryWithExcludes(MINIMAL_FILER_SERVERS, rec_excluded_keys=('OPTIONS',))
FILER_SERVERS.rec_update(getattr(settings, 'FILER_SERVERS', {}))


def update_server_settings(settings, defaults, s, t):
    if not settings[s][t]['ENGINE']:
        settings[s][t]['ENGINE'] = defaults[s][t]['ENGINE']
        settings[s][t]['OPTIONS'] = defaults[s][t]['OPTIONS']
    return settings


update_server_settings(FILER_SERVERS, DEFAULT_FILER_SERVERS, 'private', 'main')
update_server_settings(FILER_SERVERS, DEFAULT_FILER_SERVERS, 'private', 'thumbnails')


# Public media (media accessible without any permission checks)
FILER_PUBLICMEDIA_STORAGE = get_storage_class(FILER_STORAGES['public']['main']['ENGINE'])(**FILER_STORAGES['public']['main']['OPTIONS'])
FILER_PUBLICMEDIA_UPLOAD_TO = load_object(FILER_STORAGES['public']['main']['UPLOAD_TO'])
if 'UPLOAD_TO_PREFIX' in FILER_STORAGES['public']['main']:
    FILER_PUBLICMEDIA_UPLOAD_TO = load_object('filer.utils.generate_filename.prefixed_factory')(FILER_PUBLICMEDIA_UPLOAD_TO, FILER_STORAGES['public']['main']['UPLOAD_TO_PREFIX'])
FILER_PUBLICMEDIA_THUMBNAIL_STORAGE = get_storage_class(FILER_STORAGES['public']['thumbnails']['ENGINE'])(**FILER_STORAGES['public']['thumbnails']['OPTIONS'])
FILER_PUBLICMEDIA_THUMBNAIL_OPTIONS = FILER_STORAGES['public']['thumbnails']['THUMBNAIL_OPTIONS']


# Private media (media accessible through permissions checks)
FILER_PRIVATEMEDIA_STORAGE = get_storage_class(FILER_STORAGES['private']['main']['ENGINE'])(**FILER_STORAGES['private']['main']['OPTIONS'])
FILER_PRIVATEMEDIA_UPLOAD_TO = load_object(FILER_STORAGES['private']['main']['UPLOAD_TO'])
if 'UPLOAD_TO_PREFIX' in FILER_STORAGES['private']['main']:
    FILER_PRIVATEMEDIA_UPLOAD_TO = load_object('filer.utils.generate_filename.prefixed_factory')(FILER_PRIVATEMEDIA_UPLOAD_TO, FILER_STORAGES['private']['main']['UPLOAD_TO_PREFIX'])
FILER_PRIVATEMEDIA_THUMBNAIL_STORAGE = get_storage_class(FILER_STORAGES['private']['thumbnails']['ENGINE'])(**FILER_STORAGES['private']['thumbnails']['OPTIONS'])
FILER_PRIVATEMEDIA_THUMBNAIL_OPTIONS = FILER_STORAGES['private']['thumbnails']['THUMBNAIL_OPTIONS']
FILER_PRIVATEMEDIA_SERVER = load_object(FILER_SERVERS['private']['main']['ENGINE'])(**FILER_SERVERS['private']['main']['OPTIONS'])
FILER_PRIVATEMEDIA_THUMBNAIL_SERVER = load_object(FILER_SERVERS['private']['thumbnails']['ENGINE'])(**FILER_SERVERS['private']['thumbnails']['OPTIONS'])

# By default limit number of simultaneous uploads if we are using SQLite
if settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
    _uploader_connections = 1
else:
    _uploader_connections = 3
FILER_UPLOADER_CONNECTIONS = getattr(
    settings, 'FILER_UPLOADER_CONNECTIONS', _uploader_connections)
FILER_UPLOADER_MAX_FILES = getattr(
    settings, 'FILER_UPLOADER_MAX_FILES', 100)
FILER_UPLOADER_MAX_FILE_SIZE = getattr(
    settings, 'FILER_UPLOADER_MAX_FILE_SIZE', None)


FILER_DUMP_PAYLOAD = getattr(settings, 'FILER_DUMP_PAYLOAD', False)  # Whether the filer shall dump the files payload

FILER_CANONICAL_URL = getattr(settings, 'FILER_CANONICAL_URL', 'canonical/')

TABLE_LIST_TYPE = 'tb'
THUMBNAIL_LIST_TYPE = 'th'
FILER_FOLDER_ADMIN_LIST_TYPE_CHOICES = (
    TABLE_LIST_TYPE,
    THUMBNAIL_LIST_TYPE,
)
FILER_FOLDER_ADMIN_DEFAULT_LIST_TYPE = getattr(settings, 'FILER_FOLDER_ADMIN_DEFAULT_LIST_TYPE', TABLE_LIST_TYPE)
if FILER_FOLDER_ADMIN_DEFAULT_LIST_TYPE not in FILER_FOLDER_ADMIN_LIST_TYPE_CHOICES:
    FILER_FOLDER_ADMIN_DEFAULT_LIST_TYPE = TABLE_LIST_TYPE

FILER_FOLDER_ADMIN_LIST_TYPE_SWITCHER_SETTINGS = {
    TABLE_LIST_TYPE: {
        'icon': 'th-list',
        'tooltip_text': _('Show table view'),
        'template': 'admin/filer/folder/directory_table_list.html',
    },
    THUMBNAIL_LIST_TYPE: {
        'icon': 'th-large',
        'tooltip_text': _('Show thumbnail view'),
        'template': 'admin/filer/folder/directory_thumbnail_list.html',
    },
}

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
IMAGE_MIME_TYPES = ['gif', 'jpeg', 'png', 'x-png', 'svg+xml', 'webp']

FILE_VALIDATORS = {
    "text/html": ["filer.validation.deny_html"],
    "image/svg+xml": ["filer.validation.validate_svg"],
    "application/octet-stream": ["filer.validation.deny"],
}

remove_mime_types = getattr(settings, "FILER_REMOVE_FILE_VALIDATORS", [])
for mime_type in remove_mime_types:  # pragma: no cover
    if mime_type in FILE_VALIDATORS:
        del FILE_VALIDATORS[mime_type]

for mime_type, validators in getattr(settings, "FILER_ADD_FILE_VALIDATORS", {}).items():  # pragma: no cover
    if mime_type in FILE_VALIDATORS:
        FILE_VALIDATORS[mime_type] += list(validators)
    else:
        FILE_VALIDATORS[mime_type] = list(validators)

FILER_MIME_TYPE_WHITELIST = getattr(settings, "FILER_MIME_TYPE_WHITELIST", [])


# Determine if django CMS is installed and if it comes with its own iconset

ICON_CSS_LIB = ("filer/css/admin_filer.fa.icons.css",)
if "cms" in settings.INSTALLED_APPS:  # pragma: no cover
    try:
        from cms import __version__
        from cms.utils.urlutils import static_with_version

        if __version__ >= "4":
            ICON_CSS_LIB = (
                static_with_version("cms/css/cms.admin.css"),
                "filer/css/admin_filer.cms.icons.css",
            )
    except (ModuleNotFoundError, ImportError):
        # Import error? No django CMS used: stay with own icons
        pass


# SVG are their own thumbnails if their size is below this limit
FILER_MAX_SVG_THUMBNAIL_SIZE = getattr(settings, "FILER_MAX_SVG_THUMBNAIL_SIZE", 1024 * 1024)  # 1MB default
