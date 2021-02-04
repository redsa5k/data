## program to convert outer join syntax with (+) to hive compatible ansi syntax

import re
import json
from collections import defaultdict
from collections import OrderedDict

s = """FROM taba a, tabb b, tabc c, tabd d
WHERE 
a.id = b.id(+) and
(a.ic = c.ic(+) or a.icc = c.icc(+)) and
d.id = c.ic and
c.ic = 10 or a.id = 'A20' 
GROUP BY a.ic ORDER BY b.id"""

ss = str(s).replace("\n"," ")

pat=''
sus_s=''
if ('GROUP ' in ss):
   pat = "FROM(.*?)GROUP"
elif ('ORDER ' in ss):
   pat = "FROM(.*?)ORDER"
else:
   sub_s = ss

t = re.split("WHERE",sub_s)[0].strip().split(',')

c = re.split("WHERE",sub_s)[1] 

tkv = dict()

for ele in t:
	tk = ele.strip().split(' ')[1]
	tv = ele.strip()
	tkv[tk]=tv

cs=c.strip().replace(' and ', ' and~ ').replace(' or ', ' or~ ').split('~')

ckvs = []
for string in cs:
   if string.find("(+)")>string.find("="):
      cks = re.sub("[\.].*[+]", "", re.sub("[\.].*[=]", "", string.replace("+", "+~")))
   elif string.count('.')>1:
      cks=re.sub("[\.].*", "", re.sub("[\.].*[=]", "", string))
   else:
      cks = re.sub("[\.].*", "", re.sub("[\.].*[+]", "", string.replace("+", "+~")))
   ck = cks.replace("and", "").replace("or", "").strip().replace("(", "").replace(")", "").replace("=","") 
   cv = string.replace('(+)', '')
   ckvs.append((ck,cv))

dckv = defaultdict(list)
for (k, v) in  ckvs:
	dckv[k].append(v)
	

ockvs = OrderedDict()
for (k, v) in  ckvs:
   ockvs[k]=v

ckv = OrderedDict()
for (k, v) in ockvs.items():
   ckv[k]= dckv[k]


wckv = OrderedDict()
jckv = OrderedDict()
for (k, v) in ckv.items():
   if '~' in k:
      jckv[k] = v
   elif ' ' in k:
      jckv[k] = v
   else:
      wckv[k] = v

#joins
jkv = OrderedDict()
cklist=set()
for (k, v) in jckv.items():
	if '~' in k:
		if '~' in ' '.join(k.strip().split()).split(' ')[0]:
			outer = ' '.join(k.strip().split()).split(' ')[0]
			nonouter = ' '.join(k.strip().split()).split(' ')[1]
			if nonouter in cklist:
			   js = " left join " + outer + " on "
			else:			   
			   js = nonouter + " left join " + outer + " on "
			j = js.replace("~", "")
			jkv[k] = j
			cklist.add(outer.replace("~", ""))
			cklist.add(nonouter.replace("~", ""))
			
		else:
			outer = ' '.join(k.strip().split()).split(' ')[1]
			nonouter = ' '.join(k.strip().split()).split(' ')[0]
			if nonouter in cklist:
			   js = " left join " + outer + " on "
			else:			   
			   js = nonouter + " left join " + outer + " on "
			j = js.replace("~", "")
			jkv[k] = j
			cklist.add(outer.replace("~", ""))
			cklist.add(nonouter.replace("~", ""))
			
	else:
		if '~' not in k:
			ij = ' '.join(k.strip().split()).split(' ')[1]
			inn = ' '.join(k.strip().split()).split(' ')[0]
			if ij in cklist:
			   j = " inner join " + inn + " on "
			elif inn in cklist:
			   j = " inner join " + ij + " on "
			else:
			   j =  ij + " inner join " + inn + " on "
			cklist.add(ij)
			cklist.add(inn)
			jkv[k] = j

removals = "\{\}\"\:\[\]\,~"

cjkv_f = OrderedDict()
for (k, v) in jckv.items():
   v = ' '.join(v)
   for i in removals:
      v = str(v).replace(i, '')
   cjkv_f[k] = v

cjkv = OrderedDict()
for (k, v) in cjkv_f.items():
   if (cjkv_f[k].rsplit(' ', 1)[-1].upper()=='AND') or (cjkv_f[k].rsplit(' ', 1)[-1].upper()=='OR'):
      v=cjkv_f[k].rsplit(' ', 1)[0]
   else:
      v=cjkv_f[k]
   cjkv[k] = v


jcs=''
for k in jkv.keys():
   jcs = jcs+jkv[k]+cjkv[k]+' '

# filters
mwckv = OrderedDict()
for (k,v) in wckv.items():
   v = ' '.join(v)
   for i in removals:
      v = str(v).replace(i, '')
   mwckv[k] = v

fil = ''
for (k,v) in mwckv.items():
   fil = fil + mwckv[k]+' '

fil = 'WHERE '+ fil
from_c = 'FROM ' + jcs + fil

print(from_c)

if ('GROUP' in pat):
   f_s = from_c + 'GROUP '+ re.sub(pat, "", ss)
elif ('ORDER' in pat):
   f_s = from_c + 'ORDER '+ re.sub(pat, "", ss)
else:
   f_s = from_c

print(f_s)

	
	
	
		
		
		
			
			
		
		
		
	

 



