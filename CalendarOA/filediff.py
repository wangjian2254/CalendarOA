#coding=utf-8
#author:u'王健'
#Date: 14-5-18
#Time: 上午11:20
__author__ = u'王健'


def reportSingleFile(srcfile, basefile):
    src1 = file(srcfile).read().split('\n')
    src=[]
    for s in src1:
        s.decode('utf-8')
        src.append(s)
    base1 = file(basefile).read().split('\n')
    base = []
    for s in base1:
        s.decode('utf-8')
        base.append(s)
    import difflib
    s = difflib.SequenceMatcher( lambda x: len(x.strip()) == 0, # ignore blank lines
                                        base, src)
    html = open('diff.html','w')
    html.write(difflib.HtmlDiff().make_file([x for x in base],[x for x in src]))
    html.close()

    lstres = []
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        print (tag, i1, i2, j1, j2)
        #print lstres
        if tag == 'equal':
            pass
        elif  tag == 'delete' :
            lstres.append('DELETE (line: %d)' % i1)
            lstres += base[i1:i2]
            lstres.append(' ')
        elif tag == 'insert' :
            lstres.append('INSERT (line: %d)' % j1)
            lstres += src[j1:j2]
            lstres.append(' ')
        elif tag == 'replace' :
            lstres.append('REPLACE:')
            lstres.append('Before (line: %d) ' % i1)
            lstres += base[i1:i2]
            lstres.append('After (line: %d) ' % j1)
            lstres += src[j1:j2]
            lstres.append(' ')
        else:
            pass
    print '\n'.join(lstres)

reportSingleFile('develop_plan2.txt','develop_plan.txt')