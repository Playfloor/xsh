$FOREIGN_ALIASES_SUPPRESS_SKIP_MESSAGE = True

import xpg.conn
import xpg.xtable

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

# Run sql, print result table.
def _sql(args): 
	global xpg_db
	if xpg_db == None:
		xpg_db = xpg.conn.Conn()

	tt = xpg.xtable.fromSQL(xpg_db, args[0])
	return tt.show(tablefmt='simple') + '\n'

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
		return xpg_db.getxt(xtn).show(tablefmt='simple') + '\n'
	else:
		if xtn[0] == '+':
			xtn = xtn[1:]
		qry = args[1]
		xpg.xtable.fromQuery(xpg_db, qry, alias=xtn)

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
aliases['pgxtplot'] = _pgxtplot
aliases['pgxtexp'] = _pgxtexp

