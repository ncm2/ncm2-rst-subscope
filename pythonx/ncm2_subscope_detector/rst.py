# -*- coding: utf-8 -*-
import re
import logging
import copy
from ncm2 import Ncm2Base, getLogger

logger = getLogger(__name__)

block_pat = re.compile(
    r':: [ \t]* (\S+)?  [ \t]*  \n'
    r'(?:(?:[ \t]+ [^\n]* $ \n)+)?'
    r' [ \t]* \n'
    r'((( [ \t]+ [^\n]* $  )? \n)+)', re.M | re.X)


class SubscopeDetector(Ncm2Base):

    scope = ['rst']

    def detect(self, lnum, ccol, src):

        scope = None
        pos = self.lccol2pos(lnum, ccol, src)

        for m in block_pat.finditer(src):
            if m.start() > pos:
                break
            if m.group(1) and m.start(2) <= pos and m.end(2) > pos:
                scope = dict(src=m.group(2),
                             pos=pos-m.start(2),
                             scope_offset=m.start(2),
                             scope=m.group(1))
                break

        if not scope:
            return None

        new_pos = scope['pos']
        new_src = scope['src']
        p = 0
        for idx, line in enumerate(new_src.split("\n")):
            if (p <= new_pos) and (p+len(line)+1 > new_pos):
                subctx = {}
                subctx['scope'] = scope['scope']
                subctx['lnum'] = idx+1
                subctx['ccol'] = new_pos-p+1
                subctx['scope_offset'] = scope['scope_offset']
                subctx['scope_len'] = len(new_src)
                lccol = self.pos2lccol(scope['scope_offset'], src)
                subctx['scope_lnum'] = lccol[0]
                subctx['scope_ccol'] = lccol[1]
                return subctx
            else:
                p += len(line)+1

        return None
