import sys
import components as cmp
import sqlite3
from enum import Enum


class Observable:
    def __init__(self) -> None:
        self._observers = []

    def register_observer(self, observer) -> None:
        self._observers.append(observer)

    def notify_observers(self, *args, **kwargs) -> None:
        for observer in self._observers:
            observer.notify(*args, **kwargs)


class Observer:
    def __init__(self, observable, afunction) -> None:
        self.doFuncton = afunction
        observable.register_observer(self)

    def notify(self, *args, **kwargs) -> None:
        if callable(self.doFuncton):
            self.doFuncton(args[0])


class TheBase:
    Message = ''
    Fault = False
    on_Message = Observable()
    objName = ''

    # Geeft boodschap door uit child class
    def do_message(self, amsg=''):
        if not (amsg == ''):
            if self.Message == '':
                self.Message = amsg
            else:
                #self.Message = self.Message + '; ' + amsg
                self.Message = amsg

        print(self.Message)
        try:
            # Trigger het on_Message event
            self.on_Message.notify_observers(self.Message)
        except:
            print("An exception occurred")

    # Wordt aangeroepen als er iets fout gaat in child class
    def do_fault(self, amsg='', afault=True):
        self.Fault = afault
        if not (amsg == ''):
            self.do_message(amsg)

    def __str__(self):
        return self.objName


class Field(TheBase):
    class Status(Enum):
        NOTSET = 1
        SET = 2
        stConnected = 3
        UNCHANGED = 4
        CHANGED = 5

    ID_IDENT = ('ID', '_ID', 'ID_', 'KEY' 'KEY_', 'PK', '_PK', 'PK_', 'ROWID', 'RECNO')

    def __init__(self, fld_nm, is_key=False):
        # Let op: na de split functie zit de "," nog aan de veldnaam
        #super().__init__()
        self.FieldNm = fld_nm.replace(',', '')
        self.objName = self.FieldNm

        self.FieldParm = ':' + self.FieldNm
        self.isKey = is_key
        self.isEmpty = True
        self.isChanged = False
        self._FieldValue = {'old_value':'', 'new_value':''}
        # Status of the field
        self.fldStatus = set([self.Status.NOTSET])


        # Omdat je niet op 'id' kunt zoeken (kan te makkelijk voor komen)
        if self.FieldNm.upper() == self.ID_IDENT[0]:
            self.isKey = True

        for i in range(1, len(self.ID_IDENT)):
            if self.FieldNm.upper().count(self.ID_IDENT[i]) > 0:
                self.isKey = True


    @property
    def FieldValue(self):
        return self._FieldValue

    @FieldValue.setter
    def FieldValue(self, aValue):
        if (aValue != self._FieldValue):
            if (self.Status.NOTSET in self.fldStatus):
                # Set fieldstatus from unloaded to loaded
                self.fldStatus.discard(self.Status.NOTSET)
                self.fldStatus.add(self.Status.SET)
                self.fldStatus.add(self.Status.UNCHANGED)
            if (self.Status.SET in self.fldStatus):
                # Set fieldstatus from unloaded to loaded
                self.fldStatus.add(self.Status.CHANGED)

            self._FieldValue = aValue

            # Maybe usefull?
            self.isEmpty = self._FieldValue == ''


class DataBase(TheBase):
    MSG_NODB = 'No database name given'
    DataBaseNm = ''
    Conn = None
    Crs = None

    def __init__(self, dbName, initcode = ''):
        if not(dbName == ''):
            self.DataBaseNm = dbName
            if initcode == '':
                self.do_connect()
            else:
                self.do_init(initcode)

    def do_init(self, initcode):
        self.do_connect()
        try:
            self.Crs.execute(initcode)
            self.Conn.commit()
        except:
            self.do_message('Something went wrong initializing the database')
        finally:
            self.Conn.close()


    def do_connect(self):
        if self.DataBaseNm == '':
            self.do_message(self.MSG_NODB)
            return
        self.Conn = sqlite3.connect(self.DataBaseNm)
        self.Crs = self.Conn.cursor()

    def do_post(self):
        self.Conn.commit()
        self.Conn.close()

    def do_close(self):
        self.Conn.close()


class SqlQuery(TheBase):

    class QueryStatus(Enum):
        NOTSET = 1
        SET = 2
        UNCHANGED = 4
        CHANGED = 5

    on_Browse = Observable()


    MSG_NODB = 'No database object given'
    MSG_NOKEYFLD = 'No key field found'
    MSG_NOTBLNM = 'No table name found'
    # Maak een tuple sql keywords aan
    SQL_KEYWORDS = ('SELECT', 'FROM', 'DELETE', 'UPDATE', 'INSERT INTO', 'FROM', 'WHERE', '=', ' ')
    SQL_FRAGMENTS = ('SELECT ', 'DELETE FROM %s WHERE %s = %s ', 'UPDATE %s SET ', ' WHERE %s = %s ',
                     'INSERT INTO %s ', ') VALUES ','= %s ', 'FROM ', ' ')

    theDataBase = None
    TableName = ''
    KeyFieldObj = None

    NrOfRecords = 0
    NrOfColumns = 0


    recordStr = ''
    DeleteSql = ''

    def __init__(self, adatabase):
        self._SelectSql = ''
        self._NrOfRecords = 0
        self._CurrRecLstIndex = 0
        self._CurrentRecId = 1
        self.theRecords = []
        self.FieldObjects = cmp.LookupList()
        self.QueryState = set([self.QueryStatus.NOTSET])

        if not (adatabase is None):
            if type(adatabase) is str:
                self.theDataBase = DataBase(adatabase)
            else:
                self.theDataBase = adatabase
        else:
            self.do_fault(self.MSG_NODB)


    @property
    def SelectSql(self):
        return self._SelectSql

    @SelectSql.setter
    def SelectSql(self, sqlStr):
        if not(sqlStr == self._SelectSql):
            is_tblnm = False
            sqlLst = sqlStr.split()

            for i in range(len(sqlLst)):
                sqlLst[i] = sqlLst[i].replace(',', '')

            # Haal de veldnamen uit de lijst
            for i in range(len(sqlLst)):
                # In loop hiervoor is "from" keyword gevonden
                if is_tblnm:
                    self.TableName = sqlLst[i]
                    break

                # Na 'From' komt de table name
                if not (sqlLst[i].upper() == self.SQL_KEYWORDS[0]):
                    if sqlLst[i].upper() == self.SQL_KEYWORDS[1]:
                        is_tblnm = True
                    else:
                        self.FieldObjects.append(Field(sqlLst[i]))
                        #self.FieldObjects[sqlLst[i]] = Field(sqlLst[i])
                        # Check of de laatst toegevoegde (-1) een key is
                        if self.FieldObjects[-1].isKey:
                            self.KeyFieldObj = self.FieldObjects[-1]

            # Check of er wel een table name is gevonden
            if self.TableName == '':
                self.do_fault(self.MSG_NOTBLNM)

            # Check of er wel een key field is gevonden
            if self.KeyFieldObj is None:
                self.do_fault(self.MSG_NOKEYFLD)

            if not self.Fault:
                self._SelectSql = sqlStr
                self.listRecs()


    @property
    def CurrRecLstIndex(self):
        return self._CurrRecLstIndex

    @CurrRecLstIndex.setter
    def CurrRecLstIndex(self, recno):
        if self._CurrRecLstIndex != recno:
            if self.QueryStatus.SET in self.QueryState:
                self.fillCurrRecLstIndex(recno)


    @property
    def CurrentRecId(self):
        return self._CurrentRecId

    @CurrentRecId.setter
    def CurrentRecId(self, recid):
        if self._CurrentRecId != recid:
            self.fillCurrRecId(recid)



    def listRecs(self):

        if not self.Fault:
            self.theDataBase.do_connect()

            self.theDataBase.Crs.execute(self._SelectSql)
            self.theRecords = self.theDataBase.Crs.fetchall()
            self.NrOfRecords = len(self.theRecords)
            if self.NrOfRecords > 0:
                self.NrOfColumns = len(self.theRecords[0])
                # Put first rec in currrec
                self.CurrentRecNr = 0
                self.fillCurrRecLstIndex(0)

            self.theDataBase.do_close()
            # Put status right
            self.QueryState.discard(self.QueryStatus.NOTSET)
            self.QueryState.add(self.QueryStatus.SET)
            self.do_message('Data refreshed')


    # Fills the list of fieldobjects with values from selected "recordrow"
    def fillCurrRecLstIndex(self, arecnr):

        self._CurrRecLstIndex = arecnr
        self._CurrentRecId = self.theRecords[arecnr][0]
        # Fill the fieldobjects (sort of (current)record)
        for i in range(self.NrOfColumns):
            self.FieldObjects[i].FieldValue = self.theRecords[arecnr][i]
        # Activate Browse event
        self.on_Browse.notify_observers(None)

    # Fills the list of fieldobjects with values from "recordrow" with corresponding id value
    def fillCurrRecId(self, arecid):
        # Dit met count niet elegant, iets beters voor verzinnen
        # Positioneren omdat recid en rownr niet overeen komen (1 verschil)
        count = 0
        for rec in self.theRecords:
            if int(rec[0]) == arecid:
                break
            count += 1

        self._CurrentRecId = arecid
        self._CurrRecLstIndex = count
        # Fill the fieldobjects (sort of (current)record)
        for i in range(self.NrOfColumns):
            self.FieldObjects[i].FieldValue = self.theRecords[count][i]
        # Activate Browse event
        self.on_Browse.notify_observers(None)


    def nextRec(self):
        self.CurrRecLstIndex += 1
        if self.CurrRecLstIndex >= self.NrOfRecords:
            self.CurrRecLstIndex = self.NrOfRecords -1

        self.fillCurrRecLstIndex(self.CurrRecLstIndex)


    def prevRec(self):
        self.CurrRecLstIndex -= 1
        if self.CurrRecLstIndex < 0:
            self.CurrRecLstIndex = 0

        self.fillCurrRecLstIndex(self.CurrRecLstIndex)

    def goToLastRec(self):
        self.CurrRecLstIndex = self.theRecords.index(self.theRecords[-1])

    def goToFirstRec(self):
        self.CurrRecLstIndex = 0

    def delRec(self, theId):
        if not self.Fault:
            self.theDataBase.do_connect()
            # Stel delete statement samen
            cmnd = self.SQL_FRAGMENTS[1] % (self.TableName, self.KeyFieldObj.FieldNm, self.KeyFieldObj.FieldValue)
            self.theDataBase.Crs.execute(cmnd)
            self.theDataBase.do_post()


    def updateRec(self, dictValues):
        if not self.Fault:
            self.theDataBase.do_connect()
            # Stel update statement samen
            cmnd = self.SQL_FRAGMENTS[2]
            first = False
            for i in range(self.NrOfColumns):
                if not self.FieldObjects[i].isKey:
                    if first:
                        cmnd += ', '
                    else:
                        first = True
                    cmnd += self.FieldObjects[i].FieldNm + ' = ' + self.FieldObjects[i].FieldParm

            cmnd += self.SQL_FRAGMENTS[3]

            cmnd = cmnd % (self.TableName, self.KeyFieldObj.FieldNm, self.KeyFieldObj.FieldParm)

            self.theDataBase.Crs.execute(cmnd, dictValues)
            self.theDataBase.do_post()
            self.do_message('Record updated')


    def insertRec(self, dictValues):
        if not self.Fault:
            self.theDataBase.do_connect()
            # Stel update statement samen
            cmnd = self.SQL_FRAGMENTS[4]
            first = False
            for i in range(self.NrOfColumns):
                if not self.FieldObjects[i].isKey:
                    if first:
                        cmnd += ', '
                    else:
                        cmnd += ' ('
                        first = True
                    cmnd += self.FieldObjects[i].FieldNm

            cmnd += self.SQL_FRAGMENTS[5]

            first = False
            for i in range(self.NrOfColumns):
                if not self.FieldObjects[i].isKey:
                    if first:
                        cmnd += ', '
                    else:
                        cmnd += ' ('
                        first = True
                    cmnd += self.FieldObjects[i].FieldParm

            cmnd += ')'

            cmnd = cmnd % (self.TableName)

            self.theDataBase.Crs.execute(cmnd, dictValues)

            self.theDataBase.Crs.execute('SELECT LAST_INSERT_ROWID();')
            recs = self.theDataBase.Crs.fetchall()
            iid = recs[0][0]

            self.theDataBase.do_post()

            return iid
