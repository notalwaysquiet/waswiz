# Cameron Simpson's cs.wini module backported for Jython cs@zip.com.au
# HM updated 3 May 2022 for wasv9 (python 2.7)

import sys
# HM added
import re
# HM commented out: import org.python.modules.re as re
##import org.python.modules.string as string

# regexp to recognise a clause opening line
clausehdr_re=re.compile(r'^\[\s*([^\s\]]+)\s*\]')

# regexp to recognise an assignment
assign_re   =re.compile(r'^\s*([^\s=]+)\s*=\s*(.*)')

# regexp to recognise non-negative integers
int_re      =re.compile(r'^(0|[1-9][0-9]*)$')

# read a win.ini file, return a dictionary of dictionaries
def load(fp):
  contents={}	# empty clause dictionary
  clause=None	# no current clause

  for line in fp.readlines():
    # skip blank lines and comments
    nw=0
    while nw<len(line) and (line[nw] in ' \t\n\r\f\v'):
      # HM added \r\f\v to list of white space chars
      nw+=1
    line=line[nw:]
    ##line=string.strip(line)
    if len(line) == 0 or line[0] == '#': continue

    # look for [foo]
    match=clausehdr_re.match(line)
    if match is not None:
      clausename=match.group(1)
      if clausename not in contents.keys():
      	contents[clausename]={}
        clause=contents[clausename]
        continue

    # not inside a clause? complain
    if clause is None:
      print >>sys.stderr, `fp`+": unexpected data outside of [clause]: "+line
      # HM added another print line to make it more clear in the case of
      #  a blank line
      print "at line: '" + line + "'"
      continue

    # look for var=value
    match=assign_re.match(line)
    if match is not None:
      value=match.group(2)
      valmatch=int_re.match(value)
      if valmatch is not None: value=int(value)
      clause[match.group(1)]=value
      continue

    print >>sys.stderr, `fp`+": non-assignment inside clause \""+clausename+"\": "+line
    # HM added another print line to make it more clear in the case of
    #  a blank line
    print "at line: '" + line + "'"


  return contents

def getPrefixedClauses(cfg,pfx):
  d={}
  for clname in cfg.keys():
    if clname[0:len(pfx)] == pfx:
      d[clname[len(pfx):]]=cfg[clname]
  return d
