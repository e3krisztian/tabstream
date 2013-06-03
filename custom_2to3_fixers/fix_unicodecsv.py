"""Fixer that changes unicodecsv to csv.

"""

from lib2to3.pgen2 import token
from lib2to3 import fixer_base


class FixUnicodecsv(fixer_base.BaseFix):

    _accept_type = token.NAME

    def match(self, node):
        return node.value == 'unicodecsv'

    def transform(self, node, results):
        node.value = 'csv'
        node.changed()
