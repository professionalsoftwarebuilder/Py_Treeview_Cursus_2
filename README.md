# Py_Treeview_Cursus_2
treeview - sqlite3 app cursus 14 - 21 mei 2021

**TreeTabular-org.py:**  
Basic (one module) python program using Tkinter treeview populated by sqlite3.  
Contains functionallity to execute crud operations on the table displayed in the treeview.

Is not fully developed needs some clearing of debris to knit all the way around zoiets.  
(But works)

**TreeTabular.py:**  
Is Altered TreeTabular-org where functionallity to execute crud operations in put into a separate DAL (data access layer).  

All is very simplistic since the object of this project is to teach oo programming.    
The DAL is code is in sqlQuery.py, and is somewhat inspired by TSqlQuery from the free pascal dbSql package.  

**sqlQuery.py**  
The DAL has a dataBase class and a sqlQuery Class.  
The dataBase Class takes a path to de sqlite file to init.  
The sqlQuery takes a dataBase object to init.  
The sqlQuery also must be supplied a select statement in whitch you must name the fields you want to use.  
The Other Crud statments are created by de sqlQuery class.  
Also te primary key must be the fist field in the select statement (only to comply with the Treeview).  

The sqlQuery has a (symplistic) "homemade" event system based on the "Observer pattern", hence the Observable and Observer classes.  
The callback in observer.notify gets his parameter through the \*args of Observable.notify_observers.  
(Hope that makes sence)  
The event system is used to propagate messages from the sqlQuery class to a (sort of) statusbar in the root-window.  

**components.py**  
Contains a "dataAware Entry" component.  
The data aware Entry is a subclass of tkinter.Entry made to cooperate with the sqlQuery object.
The init of the dbEdit (name of data Aware Entry class) (will be renamend to dbEntry in future) takes a sqlQuery object, a fieldname and "master" (positioning parent/container object).
