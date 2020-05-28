# Postgresql Xonsh Python Tools

A bunch of scritps to use postgresql in xonsh.  Install 
as usual
```
python3 setup.py install --user
```

## Usage

Start xonsh, load the macros in xonshrc.   If user not doing
anyting, xpg will connection to the default database as default
user -- most likely this means $USER.   

Notice that we do not use ; to end the query.   Just press return
and xonsh will handle multiline just fine.

### Run a sql
```
sql! select i, i*2 as j from generate_series(1, 100) i
```

### Execute sql, don't care about result
```
sqlexec! create table t(i int, j int)
```

### Define an xtable
pgxt give sql query an alias.  Later you can refer to the alias
using @foo@, or @foo.column@.  

```
pgxt foo !select i, i*2 as j from generate_series(1, 100) i
pgxt bar !select i, i*2 as j from generate_series(1, 100) i
pgxt zoo !select @foo@.i, @bar@.j from @foo@, @bar@ where @foo@.i = @bar.i@
pgxt zoo # This is to print
```

### Plotting
I use kitty, icat is an alias of kitty +kitten icat.  Replace icat with
your favorite image viewer.

```
pgxtplot line zoo    # plot zoo, each column will be a line, x axias is [0-n)
pgxtplot xline zoo   # plot zoo, first column as x axis. 
pgxtplot pie zoo     # pie chart, first column is category, second is weight.
pgxtexp zoo          # explain
pgxtexp zoo analyze  # explain analyze

```
