from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import newTable
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[2]
UPM = 1000
ASC = 800
DESC = -200
ADV = 620

# A small, original geometric prototype: squared terminals, open lowercase forms,
# and a generous rhythm. It is intentionally a design prototype, not a claim of
# final typographic completeness.
def glyph_draw(commands):
    pen = TTGlyphPen(None)
    flat = []
    for item in commands:
        if isinstance(item, list):
            flat.extend(item)
        else:
            flat.append(item)
    for cmd in flat:
        op, pts = cmd
        if op == 'closePath':
            getattr(pen, op)()
        else:
            getattr(pen, op)(pts)
    return pen.glyph()

def rect(x0, y0, x1, y1):
    return [('moveTo', (x0,y0)), ('lineTo',(x1,y0)), ('lineTo',(x1,y1)), ('lineTo',(x0,y1)), ('closePath',())]

def poly(points):
    return [('moveTo', points[0])] + [('lineTo', p) for p in points[1:]] + [('closePath',())]

def ring(cx, cy, ro, ri, n=16):
    outer=[]; inner=[]
    for i in range(n):
        a=2*math.pi*i/n; outer.append((cx+ro*math.cos(a), cy+ro*math.sin(a)))
    for i in range(n-1,-1,-1):
        a=2*math.pi*i/n; inner.append((cx+ri*math.cos(a), cy+ri*math.sin(a)))
    return poly(outer)+poly(inner)

def seg(x0,y0,x1,y1,t=90):
    if x0==x1:
        return rect(x0-t/2,y0,x1+t/2,y1)
    return rect(x0,y0-t/2,x1,y1+t/2)

def base(commands=None): return glyph_draw(commands or [])

def scaled_glyph(glyph, sx=0.74, sy=0.70):
    pen = TTGlyphPen(None)
    transform = TransformPen(pen, (sx, 0, 0, sy, 0, 0))
    glyph.draw(transform, None)
    return pen.glyph()

def upper(ch):
    m={'A': [poly([(90,0),(205,700),(315,700),(500,0),(390,0),(350,180),(205,180),(165,0)]), rect(165,290,390,385)],
       'B': rect(90,0,180,700)+rect(160,610,360,700)+rect(160,300,360,390)+rect(160,0,360,90)+rect(330,90,430,300)+rect(330,390,430,610),
       'C': rect(100,0,180,700)+rect(170,610,450,700)+rect(170,0,450,90),
       'D': rect(90,0,180,700)+rect(160,610,400,700)+rect(160,0,400,90)+rect(380,90,470,610),
       'E': rect(90,0,180,700)+rect(170,610,470,700)+rect(170,300,420,390)+rect(170,0,470,90),
       'F': rect(90,0,180,700)+rect(170,610,470,700)+rect(170,300,420,390),
       'G': rect(100,0,180,700)+rect(170,610,450,700)+rect(170,0,450,90)+rect(370,90,450,330)+rect(300,290,450,380),
       'H': rect(90,0,180,700)+rect(400,0,490,700)+rect(180,300,400,390),
       'I': rect(130,610,450,700)+rect(250,0,330,700)+rect(130,0,450,90),
       'J': rect(130,610,450,700)+rect(250,90,330,700)+rect(100,0,330,90)+rect(90,90,180,250),
       'K': rect(90,0,180,700)+poly([(180,360),(450,700),(540,700),(300,360),(540,0),(450,0)]),
       'L': rect(90,0,180,700)+rect(170,0,470,90),
       'M': rect(80,0,170,700)+rect(450,0,540,700)+poly([(170,700),(260,700),(320,400),(380,700),(450,700),(340,0),(300,0)]),
       'N': rect(90,0,180,700)+rect(440,0,530,700)+poly([(170,700),(260,700),(440,0),(350,0)]),
       'O': ring(290,350,285,195),
       'P': rect(90,0,180,700)+rect(160,610,400,700)+rect(350,390,440,610)+rect(160,300,400,390),
       'Q': ring(285,370,270,180)+poly([(340,160),(420,80),(530,0),(450,0)]),
       'R': rect(90,0,180,700)+rect(160,610,390,700)+rect(350,390,440,610)+rect(160,300,390,390)+poly([(300,300),(390,300),(540,0),(430,0)]),
       'S': rect(160,610,450,700)+rect(100,390,180,610)+rect(160,300,420,390)+rect(400,90,480,300)+rect(120,0,440,90),
       'T': rect(90,610,510,700)+rect(255,0,345,700),
       'U': rect(90,90,180,700)+rect(400,90,490,700)+rect(160,0,420,90),
       'V': poly([(80,700),(180,700),(290,120),(400,700),(500,700),(340,0),(240,0)]),
       'W': poly([(50,700),(145,700),(220,120),(280,700),(370,700),(430,120),(505,700),(600,700),(500,0),(380,0),(325,500),(270,0),(150,0)]),
       'X': poly([(90,700),(200,700),(290,450),(380,700),(490,700),(350,350),(500,0),(390,0),(290,250),(190,0),(80,0),(230,350)]),
       'Y': poly([(80,700),(190,700),(290,430),(390,700),(500,700),(340,330),(340,0),(240,0),(240,330)]),
       'Z': rect(90,610,500,700)+rect(90,0,500,90)+poly([(110,610),(230,610),(480,90),(360,90)])}
    return base(m.get(ch, rect(100,0,200,700)))

def lower(ch):
    # Open, utilitarian lowercase forms built from a consistent 90-unit stroke.
    # The first display prototype prioritizes readable small text. A later master pass
    # will replace these small-cap forms with a complete lowercase design.
    return scaled_glyph(upper(ch.upper()))
    '''
    if ch=='o': return glyph_draw(ring(290,300,210,120))
    if ch=='c': return glyph_draw(rect(120,120,200,480)+rect(180,400,430,490)+rect(180,110,430,200))
    if ch=='e': return glyph_draw(rect(110,120,190,480)+rect(170,400,430,490)+rect(170,110,430,200)+rect(170,275,390,350))
    if ch=='a': return glyph_draw(rect(110,120,190,480)+rect(170,400,420,490)+rect(170,110,420,200)+rect(350,170,430,400))
    if ch=='s': return glyph_draw(rect(170,400,420,490)+rect(110,275,190,400)+rect(170,200,390,290)+rect(350,110,430,200)+rect(120,110,370,200))
    if ch=='n': return glyph_draw(rect(110,100,190,490)+rect(170,400,420,490)+rect(350,100,430,400))
    if ch=='m': return glyph_draw(rect(80,100,160,490)+rect(140,400,280,490)+rect(240,100,320,400)+rect(300,400,440,490)+rect(400,100,480,400))
    if ch=='i': return glyph_draw(rect(170,100,250,490)+rect(170,600,250,680))
    if ch=='l': return glyph_draw(rect(170,0,260,700))
    if ch=='t': return glyph_draw(rect(170,100,260,650)+rect(100,480,360,560))
    if ch in 'bdfhkpq':
        x=170 if ch not in 'pq' else 350
        stem=rect(x,0 if ch in 'bdfh' else -200,x+80,700 if ch in 'dfh' else 490)
        bowl=ring(x+120,300 if ch not in 'pq' else 300,190,105)
        return glyph_draw(stem+bowl)
    if ch in 'gjy':
        stem=rect(170,-200,250,490)
        bowl=ring(290,300,190,105)
        return glyph_draw(stem+bowl)
    # simple single-story geometric fallback for remaining lowercase
    return glyph_draw(rect(160,100,250,490)+rect(220,400,420,490)+rect(220,100,420,190))
    '''

def glyph_for(cp):
    ch=chr(cp)
    if 'A'<=ch<='Z': return (upper(ch), ADV)
    if 'a'<=ch<='z': return (lower(ch), ADV)
    if ch.isdigit():
        return (glyph_draw(ring(290,350,250,160) if ch=='0' else rect(140,80,440,160)+rect(140,620,440,700)+rect(140,80,220,700)), ADV)
    specials={
      ' ': (None,310), '.': (rect(250,0,340,90),620), ',': (rect(250,0,340,90)+rect(220,-80,280,0),620), '-': (rect(150,300,430,390),620), '_': (rect(80,-20,520,50),620), '!': (rect(250,120,340,700)+rect(250,0,340,80),620), '?': (rect(150,610,430,700)+rect(380,400,470,610)+rect(150,300,380,390)+rect(250,0,340,90),620), ':': (rect(250,400,340,490)+rect(250,0,340,90),620), ';': (rect(250,400,340,490)+rect(250,0,340,90)+rect(220,-80,280,0),620), '/': (poly([(120,0),(210,0),(500,700),(410,700)]),620), '+': (rect(250,120,340,580)+rect(100,300,490,390),620), '=': (rect(100,400,490,490)+rect(100,200,490,290),620), '(':(rect(220,0,300,700),620), ')':(rect(300,0,380,700),620), '@':(ring(290,350,250,160)+ring(310,350,80,35),620), '#':(rect(170,0,240,700)+rect(340,0,410,700)+rect(100,240,480,320)+rect(100,380,480,460),620), '%':(ring(180,520,75,35)+ring(400,180,75,35)+poly([(120,0),(200,0),(470,700),(390,700)]),620), '&':(rect(160,0,240,700)+rect(220,610,400,700)+rect(350,390,440,610)+rect(220,300,400,390)+rect(200,0,430,90),620)}
    if ch in specials:
        cmds,w=specials[ch]; return (base(cmds or []),w)
    return (glyph_for(cp) if False else base(rect(100,0,200,700)), ADV)

chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,:;!?-_/+=()@#%&'
glyphs={'.notdef': base(rect(80,0,500,700)+rect(160,100,420,180)+rect(160,260,420,340)+rect(160,420,420,500))}
metrics={'.notdef': ADV}
for ch in chars:
    if ch==' ': glyphs[ch]=base([]); metrics[ch]=310
    elif ch.isalpha(): glyphs[ch]=upper(ch) if ch.isupper() else lower(ch); metrics[ch]=ADV
    else:
        g,w=glyph_for(ord(ch)); glyphs[ch]=g; metrics[ch]=w

fb=FontBuilder(UPM, isTTF=True)
fb.setupGlyphOrder(list(glyphs))
fb.setupCharacterMap({ord(ch):ch for ch in chars})
fb.setupGlyf(glyphs)
fb.setupHorizontalMetrics({g:(metrics.get(g,ADV),0) for g in glyphs})
fb.setupHorizontalHeader(ascent=ASC, descent=DESC)
fb.setupOS2(sTypoAscender=ASC, sTypoDescender=DESC, usWinAscent=ASC, usWinDescent=abs(DESC), sxHeight=500, sCapHeight=700)
fb.setupPost()
fb.setupNameTable({
  'familyName':'Ani Xeno', 'styleName':'Regular', 'fullName':'Ani Xeno Regular',
  'psName':'AniXeno-Regular', 'version':'Version 0.1.0',
  'uniqueFontIdentifier':'Aniruddha Salve: Ani Xeno Regular: 0.1.0',
  'manufacturer':'Aniruddha Salve', 'designer':'Aniruddha Salve',
  'designerURL':'https://github.com/aniruddhasalve/ani-xeno',
  'copyright':'Copyright © 2026 Aniruddha Salve'
})
fb.setupPost(keepGlyphNames=True)
fb.setupMaxp()
out=ROOT/'fonts'/'ttf'/'AniXeno-Regular.ttf'; out.parent.mkdir(parents=True,exist_ok=True); fb.save(out)
# Make OpenType and WOFF variants from the same valid TrueType outlines.
font=FontBuilder(UPM,isTTF=True)
font.font=TTFont(str(out)) if False else None
from fontTools.ttLib import TTFont
src=TTFont(str(out))
for suffix in ['otf','woff']:
    clone=TTFont(str(out)); clone.flavor='woff' if suffix=='woff' else None; clone.save(ROOT/'fonts'/('otf' if suffix=='otf' else 'webfonts')/f'AniXeno-Regular.{suffix}')
try:
    clone=TTFont(str(out)); clone.flavor='woff2'; clone.save(ROOT/'fonts'/'webfonts'/'AniXeno-Regular.woff2')
except Exception as e:
    print('WOFF2 skipped:', e)
print('Generated Ani Xeno prototype binaries')
