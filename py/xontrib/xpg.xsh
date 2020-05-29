$FOREIGN_ALIASES_SUPPRESS_SKIP_MESSAGE = True

import xpg.conn
import xpg.xtable
import tabulate

xpg_db = None

# Connect to database, with [username,dbname]
def _sqlconn(args):
	global xpg_db
	if xpg_db != None:
		xpg_db = None
	if len(args) == 0:
		xpg_db = xpg.conn.Conn()
	elif len(args) == 1:
		xpg_db = xpg.conn.Conn(database=args[0])
	else:
		xpg_db = xpg.conn.Conn(args[0], database=args[1])

# A few env variable controls how the table is printed.
# see tabulate doc.
def xt2str(tt):
	cols, res = tt.execute()
	tblfmt = ${...}.get('XPG_TBLFMT', 'psql')
	stralign = ${...}.get('XPG_STRALIGN', 'left')
	numalign = ${...}.get('XPG_NUMALIGN', 'decimal')
	xts = tabulate.tabulate(res, cols, tablefmt=tblfmt, stralign=stralign, numalign=numalign)
	# Adding EOL so that we can pipe result to wc
	return xts + '\n'

# Run sql, print result table.
def _sql(args): 
	global xpg_db
	if xpg_db == None:
		xpg_db = xpg.conn.Conn()
	tt = xpg.xtable.fromQuery(xpg_db, args[0])
	return xt2str(tt)

# Run sql, return cols and result.   This function should almost
# for sure, not be used in subproc or macro, therefore we do not
# alias it.
def xpg_sql(args):
	global xpg_db
	if xpg_db == None:
		xpg_db = xpg.conn.Conn()
	tt = xpg.xtable.fromQuery(xpg_db, args[0])
	return tt.execute()

# Run sql and do not care about result
def _sqlexec(args): 
	global xpg_db
	if xpg_db == None:
		xpg_db = xpg.conn.Conn()
	xpg_db.execute_only(args[0])

# Build a xtable (client side view)
def _pgxt(args): 
	global xpg_db
	if xpg_db == None:
		xpg_db = xpg.conn.Conn()

	if len(args) == 0:
		raise Exception("pgxt: too few args.")

	xtn = args[0]
	if xtn[0] == '-':
		xpg_db.rmxt(xtn[1:])
	elif xpg_db.getxt(xtn) != None:
		# print case.
		return xt2str(xpg_db.getxt(xtn)) 
	else:
		if xtn[0] == '+':
			xtn = xtn[1:]
		qry = args[1]
		xpg.xtable.fromQuery(xpg_db, qry, alias=xtn)

# Build a xtable from python list of tuples.
def _pgxtups(args, stdin=None, stdout=None, stderr=None, spec=None, stack=None):
	global xpg_db
	if xpg_db == None:
		xpg_db = xpg.conn.Conn()

	if len(args) != 2:
		raise Exception("pgxtups: too few args.")
	
	xtn = args[0]
	# string -- almost for sure it comes from macro, let eval.
	tups = args[1]
	if type(tups) == str:
		for frame_info in stack:
			frame = frame_info[0]
			tups = eval(tups, frame.f_globals, frame.f_locals)
			break
	xpg.xtable.fromArray(xpg_db, tups, alias=xtn)

import matplotlib.pyplot as plt
from xonsh.tools import unthreadable

@unthreadable
def _pgxtplot(args): 
	global xpg_db
	if xpg_db == None:
		xpg_db = xpg.conn.Conn()

	mthd = args[0]
	xtn = args[1]

	if len(args) != 2:
		raise Exception('pgxtplot method xtablename')

	xt = xpg_db.getxt(xtn)
	if mthd == 'line':
		xt.linechart()
	elif mthd == 'xline':
		xt.xlinechart()
	elif mthd == 'pie':
		xt.piechart()
	else:
		raise Exception('pgxtplot does not support', mthd, 'method')

	plt.savefig('/tmp/xonsh.kitty.plt.png')
	icat /tmp/xonsh.kitty.plt.png

@unthreadable
def _pgxtexp(args): 
	global xpg_db
	if xpg_db == None:
		xpg_db = xpg.conn.Conn()

	xtn = args[0]
	xt = xpg_db.getxt(xtn)
	if len(args) == 2 and args[1] == 'analyze':
		exp = xt.dotplan('/tmp/xonsh.kitty.plt', analyze=True)
	else:
		exp = xt.dotplan('/tmp/xonsh.kitty.plt')
	icat /tmp/xonsh.kitty.plt.png
	
aliases['pgconn'] = _sqlconn
aliases['sql'] = _sql
aliases['sqlexec'] = _sqlexec
aliases['pgxt'] = _pgxt 
aliases['pgxtups'] = _pgxtups
aliases['pgxtplot'] = _pgxtplot
aliases['pgxtexp'] = _pgxtexp


