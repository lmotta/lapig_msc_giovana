#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Argpase Types
Description          : Types uses by argpase
Date                 : September, 2020
copyright            : (C) 2020 by Luiz Motta
email                : motta.luiz@gmail.com

Example:
    import argparse
    from mod_py.argparse_types import DateType
    parser = argparse.ArgumentParser(description=f"..." )
    parser.add_argument( 'ini_date', action='store', help='Initial date (YYYY-mm-DD)', type=DateType() )

Updates:
- None

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
__author__ = 'Luiz Motta'
__date__ = '2020-09-24'
__copyright__ = '(C) 2020, Luiz Motta'
__revision__ = '$Format:%H$'
 
import argparse

import re, os
from datetime import datetime


class EmailType(object):
    """
    Adaptation from https://gist.github.com/asfaltboy/79a02a2b9871501af5f00c95daaeb6e7
    Supports checking email agains different patterns. The current available patterns is:
    RFC5322 (http://www.ietf.org/rfc/rfc5322.txt)
    """
    PATTERNS = {
        'RFC5322': re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"),
    }
    def __init__(self, pattern):
        if pattern not in self.PATTERNS:
            msg = f"{pattern} is not a supported email pattern, choose from: {','.join(self.PATTERNS)}"
            raise KeyError( msg )
        self._rules = pattern
        self._pattern = self.PATTERNS[ pattern ]

    def __call__(self, value):
        if not self._pattern.match( value ):
            msg = f"'{value}' is not a valid email - does not match {self._rules} rules"
            raise argparse.ArgumentTypeError( msg )
        return value


class DateType(object):
    def __init__(self):
        pass
    def __call__(self, value):
        vdate, msg = None, None
        try:
            vdate = datetime.strptime( value, '%Y-%m-%d')
        except ValueError:
            msg = f"No valid date '{value}' (YYYY-MM-DD)"
        except:
            msg = f"Unexpected error with date '{value}' (YYYY-MM-DD)"

        if not msg is None:
            raise argparse.ArgumentTypeError( msg )
        return vdate


class FilePathType(object):
    def __init__(self):
        pass
    def __call__(self, value):
        msg = None
        if not os.path.isfile( value ):
            msg = f"Missing file '{value}'"
        if not msg is None:
            raise argparse.ArgumentTypeError( msg )
        return value
