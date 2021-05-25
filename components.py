import tkinter as tk
import sqlQuery as sql


# A Statusbar
class StatusBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.variable = tk.StringVar()
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                              textvariable=self.variable,
                              font=('arial', 16, 'normal'))
        self.variable.set('Status Bar')
        self.label.pack(fill=tk.X)
        self.pack(expand=tk.YES)

    def settext(self, atext):
        self.variable.set(atext)

    def clear(self):
        self.variable.set('')


# Lijst die maakt dat in lijst namen gebruikt kunnen worden ipv indices
class LookupList(list):
    def lookup(self, aString):
        found = False
        for item in self:
            if item.objName:
                if item.objName == aString:
                    found = True
                    return item
        if not found:
            return None

class dbEdit(tk.Entry):


    def __init__(self, aQuery, aFieldNm, master=None, cnf={}, **kw ):
        super().__init__(master, cnf, **kw)
        self.theQuery = aQuery
        self.do_Update = sql.Observer(self.theQuery.on_Browse, self.reFreshEntry)
        self.fieldName = aFieldNm
        self.reFreshEntry()


    def clearEntry(self):
        self.delete(0, tk.END)

    # Dummy parameter to satisfy Observer (not elegant)
    def reFreshEntry(self, dummy=None):
        if self.theQuery.QueryStatus.SET in self.theQuery.QueryState:
            self.clearEntry()
            self.insert(0, self.theQuery.FieldObjects.lookup(self.fieldName).FieldValue)