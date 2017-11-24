# -*- coding: utf-8 -*-
import MeCab
m = MeCab.Tagger(' -d /usr/lib/mecab/dic/mecab-ipadic-neologd')

text = '''
『アイドルマスター シンデレラガールズ』（THE IDOLM@STER CINDERELLA GIRLS）は、バンダイナムコエンターテインメント（旧バンダイナムコゲームス）とCygamesが開発・運営する『THE IDOLM@STER』の世界観をモチーフとする携帯端末専用のソーシャルゲーム。
'''
print(m.parse(text))