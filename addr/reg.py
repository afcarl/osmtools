#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

FULLWIDTH = u"　！”＃＄％＆’（）＊＋，\uff0d\u2212．／０１２３４５６７８９：；＜＝＞？" \
            u"＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿" \
            u"‘ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ｛｜｝"
HALFWIDTH = u" !\"#$%&'()*+,--./0123456789:;<=>?" \
            u"@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_" \
            u"`abcdefghijklmnopqrstuvwxyz{|}"
Z2HMAP = dict( (ord(zc), ord(hc)) for (zc,hc) in zip(FULLWIDTH, HALFWIDTH) )
def zen2han(s):
    return s.translate(Z2HMAP)

KANDIGIT = {
    u'〇':0, u'一':1, u'二':2, u'三':3, u'四':4,
    u'五':5, u'六':6, u'七':7, u'八':8, u'九':9,
    u'十':10, u'百':100, u'千':1000
}
def intkan(s):
    d1 = d2 = 0
    for c in s:
        if c in KANDIGIT:
            i = KANDIGIT[c]
            if i < 10:
                d1 = d1*10+i
            else:
                if d1 == 0:
                    d1 = 1
                d2 += d1*i
                d1 = 0
    return d1+d2

DIGIT = re.compile(u'[〇一二三四五六七八九十]+')
ALT = dict( (ord(v[0]),v[1]) for v in
            (u'ヶケ', u'ッツ',
             u'澤沢', u'淵渕',
             u'槇槙', u'嶋島',
             u'萬万', u'斎斉',
             u'藪薮', u'阪坂',
             u'櫻桜', u'冶治',
             u'曽曾', u'狹挟',
             u'狭挟'
             ))
AZA = re.compile(u'大?字(.)')
NO = re.compile(u'[ノの]')
SPC = re.compile(u'\s', re.U)
PAREN = re.compile(u'\([^\)]+\)')
