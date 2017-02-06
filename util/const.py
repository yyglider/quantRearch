# -*- coding: utf-8 -*-

from enum import Enum


POSISION_STRATEGY = Enum("POSISION_STRATEGY", [
    "EQUAL",
    "BY_MKT_CAP",
    "USER_DEFINED",
])

INTEREST_TYPE = Enum("INTEREST_TYPE", [
    "COMPOUND",
    "SIMPLE",
])