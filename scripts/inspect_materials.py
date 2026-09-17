"""Read-only file inventory and physical PDF-page checks; never changes inputs."""
import argparse
import hashlib
import json
import os
import re
import stat
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

def is_link(path):
    st=path.lstat()
    return path.is_symlink() or bool(getattr(st,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',1024))

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def pdf_pages(path):
    try:from pypdf import PdfReader
    except ImportError as e:raise RuntimeError('PDF metadata requires pypdf; install in the selected runtime') from e
    r=PdfReader(path)
    if r.is_encrypted and r.decrypt('')==0:raise ValueError('Encrypted PDF requires a password')
    return len(r.pages)

def metadata(path):
    ext=path.suffix.lower()
    if ext=='.pdf':return {'pdf_pages':pdf_pages(path),'content_read':False}
    if ext in {'.docx','.xlsx'}:
        with zipfile.ZipFile(path) as z:
            names=z.namelist()
            media=sum(n.startswith(('word/media/','xl/media/')) and not n.endswith('/') for n in names)
            if ext=='.docx':
                t=ET.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                return {'paragraphs':len(t.findall('.//w:p',ns)),'tables':len(t.findall('.//w:tbl',ns)),'media':media,'content_read':False}
            ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            t=ET.fromstring(z.read('xl/workbook.xml'))
            return {'sheet_names':[s.get('name') for s in t.findall('s:sheets/s:sheet',ns)],'media':media,'content_read':False}
    return {'metadata_status':'not_inspected','content_read':False}

def inventory(root):
    root=Path(root).absolute()
    if is_link(root):raise ValueError('Refuse linked/reparse-point root')
    if not root.is_dir():raise ValueError('Inventory root must be a directory')
    items=[];skipped=[];walk_errors=[]
    def onerror(e):walk_errors.append(str(e))
    for folder,dirs,files in os.walk(root,followlinks=False,onerror=onerror):
        base=Path(folder)
        for name in list(dirs):
            d=base/name
            if is_link(d):dirs.remove(name);skipped.append(d.relative_to(root).as_posix())
        for name in sorted(files):
            p=base/name;rel=p.relative_to(root).as_posix()
            try:
                if is_link(p):skipped.append(rel);continue
                start=p.stat();item={'path':rel,'bytes':start.st_size,'sha256':sha256(p),'metadata':metadata(p)}
                end=p.stat()
                if (start.st_size,start.st_mtime_ns)!=(end.st_size,end.st_mtime_ns):raise RuntimeError('Input changed while being read; rerun after saving/closing')
                items.append(item)
            except Exception as e:items.append({'path':rel,'error':str(e),'content_read':False})
    by_hash=defaultdict(list);by_id=defaultdict(list)
    for item in items:
        if 'sha256' in item:by_hash[item['sha256']].append(item['path'])
        m=re.match(r'^(\d{4})-',Path(item['path']).name)
        if m:by_id[m.group(1)].append(item['path'])
    collisions={k:v for k,v in by_id.items() if len({str(Path(p).with_suffix('')) for p in v})>1}
    return {'root':str(root),'files':sorted(items,key=lambda i:i['path']),'exact_duplicates':[v for v in by_hash.values() if len(v)>1],
            'number_collisions':collisions,'skipped_links':sorted(skipped),'walk_errors':walk_errors,
            'limitation':'Hashes detect byte duplicates only. Metadata is not full reading, signature verification or compliance review.'}

def page_check(path,pages):
    path=Path(path).absolute()
    if is_link(path):raise ValueError('Refuse linked/reparse-point file')
    if path.suffix.lower()!='.pdf':raise ValueError('page-check accepts PDF only')
    if not pages or any(not isinstance(p,int) or p<1 for p in pages):raise ValueError('Physical page numbers must be positive integers')
    count=pdf_pages(path)
    return {'file':str(path),'pdf_pages':count,'requested_physical_pages':pages,'out_of_range':[p for p in pages if p>count],
            'limitation':'Does not validate printed page labels or evidence content.'}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='command',required=True)
    i=subs.add_parser('inventory');i.add_argument('directory')
    c=subs.add_parser('page-check');c.add_argument('pdf');c.add_argument('--pages',required=True,help='1-based physical pages, comma separated')
    args=p.parse_args(argv)
    try:
        if args.command=='inventory':
            result=inventory(args.directory);failed=bool(result['walk_errors'] or any('error' in f for f in result['files']))
        else:
            result=page_check(args.pdf,[int(v.strip()) for v in args.pages.split(',')]);failed=bool(result['out_of_range'])
        print(json.dumps(result,ensure_ascii=False,indent=2));return 2 if failed else 0
    except Exception as e:print(json.dumps({'error':str(e)},ensure_ascii=False));return 2

if __name__=='__main__':sys.exit(main())
