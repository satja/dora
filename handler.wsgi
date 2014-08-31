#!/usr/bin/env python
import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dora.settings")

application = get_wsgi_application()
