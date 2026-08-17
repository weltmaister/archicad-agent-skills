#!/usr/bin/env python3
"""Per-layer proof comparison of a source plan PDF vs a published plan PDF.

Classifies vector segments into building linework, dimension linework, symbols, and
text-associated marks, then diffs text/numeric/room-label counters between the two PDFs.
"""
from __future__ import annotations
import argparse, json, math, re
from pathlib import Path
from collections import Counter, defaultdict
import fitz
import cv2
import numpy as np

NUM_RE=re.compile(r'^\d+(?:[,.]\d+)?$')
# Uppercase room-label detector; includes common Latin-1 uppercase letters (given as
# escapes) so plans annotated in other Latin-script locales still match.
ROOM_RE=re.compile('[A-Z\\u00C4\\u00D6\\u00DC]{3,}')


def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])

def rect_union(rects):
    if not rects: return None
    return [min(r[0] for r in rects), min(r[1] for r in rects), max(r[2] for r in rects), max(r[3] for r in rects)]

def rect_intersects(a,b):
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

def rect_center(r): return ((r[0]+r[2])/2,(r[1]+r[3])/2)

def parse_drawings(page):
    segs=[]
    for di,d in enumerate(page.get_drawings()):
        width=float(d.get('width') or 0)
        fill=d.get('fill')
        color=d.get('color')
        for item in d.get('items',[]):
            kind=item[0]
            if kind=='l':
                p1=item[1]; p2=item[2]
                bbox=[min(p1.x,p2.x),min(p1.y,p2.y),max(p1.x,p2.x),max(p1.y,p2.y)]
                length=dist((p1.x,p1.y),(p2.x,p2.y))
                angle=math.degrees(math.atan2(p2.y-p1.y,p2.x-p1.x)) if length else 0
                cls='h' if abs(angle)<8 or abs(abs(angle)-180)<8 else 'v' if abs(abs(angle)-90)<8 else 'diag'
                segs.append({'kind':'line','bbox':bbox,'p1':[p1.x,p1.y],'p2':[p2.x,p2.y],'len':length,'angle':angle,'class':cls,'width':width,'filled':fill is not None,'draw_index':di})
            elif kind=='c':
                pts=item[1:5]
                xs=[p.x for p in pts]; ys=[p.y for p in pts]
                length=sum(dist((pts[i].x,pts[i].y),(pts[i+1].x,pts[i+1].y)) for i in range(3))
                segs.append({'kind':'curve','bbox':[min(xs),min(ys),max(xs),max(ys)],'len':length,'class':'curve','width':width,'filled':fill is not None,'draw_index':di})
            elif kind=='qu':
                q=item[1]
                # PyMuPDF quad has ul/ur/ll/lr points.
                pts=[q.ul,q.ur,q.lr,q.ll]
                xs=[p.x for p in pts]; ys=[p.y for p in pts]
                length=sum(dist((pts[i].x,pts[i].y),(pts[(i+1)%4].x,pts[(i+1)%4].y)) for i in range(4))
                segs.append({'kind':'quad','bbox':[min(xs),min(ys),max(xs),max(ys)],'len':length,'class':'quad','width':width,'filled':fill is not None,'draw_index':di})
            elif kind=='re':
                r=item[1]
                segs.append({'kind':'rect','bbox':[r.x0,r.y0,r.x1,r.y1],'len':2*((r.x1-r.x0)+(r.y1-r.y0)),'class':'rect','width':width,'filled':fill is not None,'draw_index':di})
    return segs

def parse_text(page):
    out=[]
    for b in page.get_text('dict').get('blocks',[]):
        if b.get('type')!=0: continue
        for line in b.get('lines',[]):
            txt=''.join(span.get('text','') for span in line.get('spans',[])).strip()
            if not txt: continue
            bbox=[float(v) for v in line['bbox']]
            out.append({'text':txt,'bbox':bbox,'center':rect_center(bbox),'dir':line.get('dir'),'is_numeric':bool(NUM_RE.match(txt)),'is_roomlike':bool(ROOM_RE.search(txt))})
    return out

def detect_body_bbox(segs):
    # Building body is the dense central linework, not outer dimension strings. Prefer long h/v linework.
    long=[s for s in segs if s['kind']=='line' and s['class'] in ('h','v') and s['len']>30]
    if not long: long=[s for s in segs if s['len']>20]
    # Trim extreme dimension chains by taking central-percentile centers.
    centers=np.array([rect_center(s['bbox']) for s in long], dtype=float)
    if len(centers)<5:
        return rect_union([s['bbox'] for s in long]) or [0,0,1,1]
    xlo,xhi=np.percentile(centers[:,0],[15,85]); ylo,yhi=np.percentile(centers[:,1],[15,85])
    central=[s for s in long if xlo<=rect_center(s['bbox'])[0]<=xhi and ylo<=rect_center(s['bbox'])[1]<=yhi]
    box=rect_union([s['bbox'] for s in central]) or rect_union([s['bbox'] for s in long])
    pad=8
    return [box[0]-pad,box[1]-pad,box[2]+pad,box[3]+pad]

def classify_segments(segs, texts):
    body=detect_body_bbox(segs)
    # text boxes expanded to mark text-associated paths if a PDF outlines text as vectors.
    text_union_boxes=[]
    for t in texts:
        r=t['bbox']; text_union_boxes.append([r[0]-2,r[1]-2,r[2]+2,r[3]+2])
    layers=defaultdict(list)
    for s in segs:
        bbox=s['bbox']; c=rect_center(bbox)
        in_body=rect_intersects(bbox, body)
        near_text=any(rect_intersects(bbox,tb) for tb in text_union_boxes)
        if near_text and s['len']<50:
            layer='text_outline_or_marker'
        elif not in_body:
            layer='dimension_linework'
        elif s['kind'] in ('curve','quad') or s['class']=='diag' or s['len']<18:
            layer='symbols_openings_fixtures'
        else:
            layer='building_linework'
        layers[layer].append(s)
    return body,layers

def summarize(pdf: Path):
    doc=fitz.open(pdf); page=doc[0]
    segs=parse_drawings(page); texts=parse_text(page)
    body,layers=classify_segments(segs,texts)
    text_counter=Counter(t['text'] for t in texts)
    numeric_counter=Counter(t['text'] for t in texts if t['is_numeric'])
    room_counter=Counter(t['text'] for t in texts if t['is_roomlike'] and not t['is_numeric'])
    layer_summary={}
    for name,items in layers.items():
        layer_summary[name]={'count':len(items),'length_sum':round(sum(s['len'] for s in items),2),'kinds':dict(Counter(s['kind'] for s in items)),'classes':dict(Counter(s.get('class','') for s in items))}
    return {'pdf':str(pdf),'page_rect':[page.rect.x0,page.rect.y0,page.rect.x1,page.rect.y1],'body_bbox':body,'segment_total':len(segs),'text_total':len(texts),'text_counter':dict(text_counter),'numeric_counter':dict(numeric_counter),'room_counter':dict(room_counter),'layers':layer_summary,'top_segments':sorted(segs,key=lambda s:-s['len'])[:40],'texts':texts}

def counter_diff(a,b):
    ca=Counter(a); cb=Counter(b)
    return {'missing':dict(ca-cb),'extra':dict(cb-ca),'common':dict(ca & cb)}

def compare(src,pub):
    layers=sorted(set(src['layers'])|set(pub['layers']))
    layer_diffs={}
    for l in layers:
        s=src['layers'].get(l,{'count':0,'length_sum':0,'kinds':{},'classes':{}})
        p=pub['layers'].get(l,{'count':0,'length_sum':0,'kinds':{},'classes':{}})
        layer_diffs[l]={'source_count':s['count'],'published_count':p['count'],'count_delta':p['count']-s['count'],'source_length':s['length_sum'],'published_length':p['length_sum'],'length_delta':round(p['length_sum']-s['length_sum'],2)}
    return {'layer_diffs':layer_diffs,'text_diff':counter_diff(src['text_counter'],pub['text_counter']),'numeric_text_diff':counter_diff(src['numeric_counter'],pub['numeric_counter']),'room_text_diff':counter_diff(src['room_counter'],pub['room_counter'])}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-pdf',required=True,type=Path)
    ap.add_argument('--published-pdf',required=True,type=Path)
    ap.add_argument('--out-dir',required=True,type=Path)
    args=ap.parse_args(); args.out_dir.mkdir(parents=True,exist_ok=True)
    src=summarize(args.source_pdf); pub=summarize(args.published_pdf); comp=compare(src,pub)
    report={'source':src,'published':pub,'comparison':comp}
    out=args.out_dir/'proof-layer-report.json'
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'report':str(out),'source_segments':src['segment_total'],'published_segments':pub['segment_total'],'source_texts':src['text_total'],'published_texts':pub['text_total'],'layer_diffs':comp['layer_diffs'],'missing_room_texts':comp['room_text_diff']['missing'],'extra_room_texts':comp['room_text_diff']['extra'],'missing_numeric_texts':comp['numeric_text_diff']['missing'],'extra_numeric_texts':comp['numeric_text_diff']['extra']},indent=2,ensure_ascii=False))
if __name__=='__main__': main()
