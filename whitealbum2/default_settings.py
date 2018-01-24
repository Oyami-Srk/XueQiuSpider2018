# -*- coding: utf-8 -*-
# ! python3

from XueQiu import XueQiu

# 错误等级0为无关紧要, 从1~3分别为严重,重要,不重要


def exception_handler(msg: str,
                      e: Exception=None,
                      msg_type: str='GENERAL',
                      msg_level: int=0,
                      raiser_label: str='unknown',
                      XueQiuClass: XueQiu=None):
    m = "<" + raiser_label + ">"
    m = m + "[" + msg_type + "-" + str(msg_level) + "]"
    m = m + msg
    if isinstance(e, KeyboardInterrupt):
        return False
    XueQiuClass.log("Exception: " + m)
    if msg_level >= 3:
        return False
    return True
