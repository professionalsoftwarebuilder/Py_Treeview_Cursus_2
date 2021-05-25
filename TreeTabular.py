import tkinter as tk
from tkinter import ttk
import sqlQuery as sql
import components as cmp
import sqlite3

SQL_SELECT_ALL = 'select rowid, VoorNm, AchterNm, Geslacht from klanten'
# Create table
SQL_KLANTENTABLE = '''
            CREATE TABLE if not exists klanten (
            VoorNm TEXT, 
            AchterNm TEXT,
            Geslacht TEXT
            )
        '''
DATABASENAME = 'mijnDb.db'


sqlQuery = None

def setupApp():

    theDataBase = sql.DataBase(DATABASENAME, SQL_KLANTENTABLE)

    global sqlQuery
    sqlQuery = sql.SqlQuery(theDataBase)
    sqlQuery.SelectSql = SQL_SELECT_ALL


setupApp()


# Haal records op uit database
def query_database(sqlcmd):
    # Connect to database (or create it)
    conn = sqlite3.connect(DATABASENAME)

    # Create a cursor instance
    curs = conn.cursor()

    curs.execute(sqlcmd)
    recs = curs.fetchall()

    # Commit changes
    conn.commit()

    # Close connection
    conn.close()

    return recs


def exec_comnd(sqlcommand, dict):
    # Connecten met een database
    # (wordt aangemaakt indien deze niet bestaat)
    conn = sqlite3.connect(DATABASENAME)

    # Maak een cursor aan
    curs = conn.cursor()

    # Voor de sql commando uit in de database
    curs.execute(sqlcommand, dict)

    # Wijzigingen commiten
    conn.commit()

    # Connectie sluiten
    conn.close()


# Functie om te inserten
def exec_insert(sqlcommand, dict):
    # Connecten met een database
    # (wordt aangemaakt indien deze niet bestaat)
    conn = sqlite3.connect(DATABASENAME)

    # Maak een cursor aan
    curs = conn.cursor()

    # Voor de sql commando uit in de database
    curs.execute(sqlcommand, dict)

    # Wijzigingen commiten
    conn.commit()

    curs.execute('SELECT LAST_INSERT_ROWID();')
    recs = curs.fetchall()
    iid = recs[0][0]

    # Connectie sluiten
    conn.close()

    return iid


def fillTree():

    tree.delete(*tree.get_children())

    for rec in sqlQuery.theRecords:
        tree.insert(parent='', index='end', iid=rec[0], values=(rec[0], rec[1], rec[2], rec[3]))

    return sqlQuery.NrOfRecords


def refreshData():
    ledigEntryBoxen()

    # Record nummer ophalen
    selected = tree.focus()
    sqlQuery.listRecs()
    fillTree()
    tree.focus(selected)
    tree.selection_set(selected)
    selectRec()



root = tk.Tk()
root.title('Treeview demo')
root.geometry('800x800')

columns = ('Id', 'Voornaam', 'Achternaam', 'Geslacht')

top_frame = tk.Frame(root, bg='yellow')
top_frame.pack(side=tk.TOP)

tree_frame = tk.Frame(root)
tree_frame.pack(pady=40)

# Create tree scrollbar
tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=tree_scroll.set, selectmode='extended' )

# Configure the scrollbar
tree_scroll.config(command=tree.yview)

# Kolom formatten
tree.column('Id', width=35, anchor='e')
tree.column('Voornaam', width=120, anchor='w')
tree.column('Achternaam', width=130, anchor='w')
tree.column('Geslacht', width=60, anchor='w')

# Header formatten
tree.heading('Id', text='Id', anchor='w')
tree.heading('Voornaam', text='Voornamen', anchor='w')
tree.heading('Achternaam', text='Achternamen', anchor='w')
tree.heading('Geslacht', text='Man/Vrouw', anchor='w')

# Create striped row tags
#tree.tag_configure('oddrow', 'white')
#tree.tag_configure('evenrow', 'lightblue')

# Data invoegen
#tree.insert(parent='', index='end', iid=0, values=('John', 'Smith', 'Man'))
#tree.insert(parent='', index='end', iid=1, values=('Betsie', 'Jansen', 'Vrouw'))

tree.pack()


# Add record entry boxes
data_frame = tk.LabelFrame(root, text='Record')
data_frame.pack(fill='x', expand='yes', padx=20)

lblFirstNm = tk.Label(data_frame, text='Voornaam:')
lblFirstNm.grid(row=0, column=0, padx=10, pady=10)
edtFirstNm = cmp.dbEdit(sqlQuery, 'VoorNm', data_frame)
edtFirstNm.grid(row=0, column=1, padx=10, pady=10)

lblLastNm = tk.Label(data_frame, text='Achternaam:')
lblLastNm.grid(row=0, column=2, padx=10, pady=10)
edtLastNm = cmp.dbEdit(sqlQuery, 'AchterNm', data_frame)
edtLastNm.grid(row=0, column=3, padx=10, pady=10)

lblGeslacht = tk.Label(data_frame, text='Geslacht:')
lblGeslacht.grid(row=1, column=0, padx=10, pady=10)
edtGeslacht = cmp.dbEdit(sqlQuery, 'Geslacht', data_frame)
edtGeslacht.grid(row=1, column=1, padx=10, pady=10)


def goToFirstRec():

    recindex = sqlQuery.goToFirstRec()
    recid = sqlQuery.recIndexToRecId(recindex)
    tree.focus(recid)
    tree.selection_set(recid)


btnFirstRow = tk.Button(top_frame, text='First', command=goToFirstRec)
btnFirstRow.pack(side=tk.LEFT)


def goToLastRec():
    sqlQuery.goToLastRec()


btnLastRow = tk.Button(top_frame, text='Last', command=goToLastRec)
btnLastRow.pack(side=tk.LEFT)


def ledigEntryBoxen():
    edtGeslacht.delete(0, tk.END)
    edtLastNm.delete(0, tk.END)
    edtFirstNm.delete(0, 'end')


btnLedigBoxen = tk.Button(data_frame, text='Empty', command=ledigEntryBoxen)
btnLedigBoxen.grid(row=2, column=0, padx=10, pady=10)


# Add button toevoegen
def toevoegenRec():

    # Record aan database toevoegen
    # sqlcmnd = '''insert into klanten
    #    (VoorNm,
    #    AchterNm,
    #    Geslacht)
    #    Values
    #    (:voor,
    #    :achter,
    #    :geslacht)
    #    '''
    sqlQuery.setToInsert()
    btnToevoeg.configure(text='ConFirm')
    btnToevoeg.configure(command=conFirm)

def conFirm():

    dict = {'VoorNm': edtFirstNm.get(),
            'AchterNm': edtLastNm.get(),
            'Geslacht': edtGeslacht.get()}

    iid = sqlQuery.insertRec(dict)

    tree.insert(parent='', index='end', iid=iid, values=(iid, edtFirstNm.get(), edtLastNm.get(), edtGeslacht.get()))

    btnToevoeg.configure(text='Add')
    btnToevoeg.configure(command=toevoegenRec)


btnToevoeg = tk.Button(top_frame, text='Add', command=toevoegenRec)
btnToevoeg.pack(side=tk.LEFT)


# Een rec wissen
def wisGeselecteerde():
    # Als er ubhaubt een rec is geselecteerd
    if len(tree.selection()) != 0:
        rec = tree.selection()[0]
        tree.delete(rec)

        # Record ook in database deleten
        sqlQuery.delRec(rec)


btnWisEen = tk.Button(top_frame, text='Delete', command=wisGeselecteerde)
btnWisEen.pack(side=tk.LEFT)


# Record wijzigen
def selecteerRec(e):
    selectRec()


def selectRec():
    # Record _id ophalen
    selected = tree.focus()
    # Let op: CurrentRecId is anders dan CurrentRecNr
    sqlQuery.CurrentRecId = int(selected)


# Treeview en Entryboxen binden
# Hieronder wordt het loslaten van de rechtermuisknop   verbonden met functie selecteerRec
tree.bind('<ButtonRelease-1>', selecteerRec)

btnRefresh = tk.Button(top_frame, text='Refresh', command=refreshData)
btnRefresh.pack(side=tk.LEFT)


def updateRec():
    # Record nummer ophalen
    selected = tree.focus()
    # Record opslaan
    values = tree.item(selected, text='', values=(selected, edtFirstNm.get(), edtLastNm.get(), edtGeslacht.get()))

    dict = {'VoorNm': edtFirstNm.get(),
            'AchterNm': edtLastNm.get(),
            'Geslacht': edtGeslacht.get(),
            'rowid': selected}

    sqlQuery.updateRec(dict)


btnUpdateRec = tk.Button(top_frame, text='Update', command=updateRec)
btnUpdateRec.pack(side=tk.LEFT)

stBrMessages = cmp.StatusBar(root)


def setStatusBarText(aText):
    stBrMessages.settext(aText)

on_Message = sql.Observer(sqlQuery.on_Message, setStatusBarText)


def initApp():
    reccount = fillTree()
    goToFirstRec()


initApp()

root.mainloop()
