#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from app.views import descarga_automatica, Series

if __name__ == '__main__':
    if len(sys.argv) != 1:
        descarga_automatica.main()
    else:
        Series.main()
