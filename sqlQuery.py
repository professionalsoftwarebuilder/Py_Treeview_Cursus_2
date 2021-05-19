import sys
import sqlite3


class TheBase:
    Message = ''
    Fault = False

    def do_message(self, amsg=''):
        if not (amsg == ''):
            if self.Message == '':
                self.Message = amsg
            else:
                self.Message = self.Message + '\n' + amsg
        print(self.Message)

    def do_fault(self, afault=True, amsg=''):
        self.Fault = afault
        if not (amsg == ''):
            self.do_message(amsg)


class Field:
    ID_IDENT = ('ID', '_ID', 'KEY', '_PK')
    FieldValue = ''

    def __init__(self, fld_nm, is_key=False):
        self.FieldNm = fld_nm
        self.isKey = is_key


        # Omdat je niet op 'id' kunt zoeken (kan te makkelijk voor komen)
        if self.FieldNm.upper() == self.ID_IDENT[0]:
            self.isKey = True

        for i in range(1, len(self.ID_IDENT)):
            if self.FieldNm.upper().count(self.ID_IDENT[i]) > 0:
                self.isKey = True



class DataBase(TheBase):
    MSG_NODB = 'No database name given'
    DataBaseNm = ''
    Conn = None
    Crs = None

    def __init__(self, dbName):
        if not(dbName == ''):
            self.DataBaseNm = dbName
            self.do_connect()

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
    MSG_NODB = 'No database object given'
    MSG_NOKEYFLD = 'No key field found'
    MSG_NOTBLNM = 'No table name found'
    # Maak een tuple sql keywords aan
    SQL_KEYWORDS = ('SELECT', 'DELETE', 'FROM', 'WHERE', '=', ' ')
    SQL_FRAGMENTS = ('SELECT ', 'DELETE FROM %s WHERE %s = %s ', 'FROM ', 'WHERE %s = %s ', '= %s ', ' ')

    theDataBase = None
    FieldObjects = []
    TableName = ''
    KeyFieldObj = None

    NrOfRecords = 0
    CurrentRecNr = 0
    NrOfColumns = 0

    theRecords = None
    recordStr = ''
    DeleteSql = ''

    def __init__(self, adatabase):
        self._SelectSql = ''
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

            # Haal de veldnamen uit de lijst
            for i in range(len(sqlLst)):
                # In loop hiervoor is "from" keyword gevonden
                if is_tblnm:
                    self.TableName = sqlLst[i]
                    break

                # Na 'From' komt de table name
                if not (sqlLst[i].upper() == self.SQL_KEYWORDS[0]):
                    if sqlLst[i].upper() == self.SQL_KEYWORDS[2]:
                        is_tblnm = True
                    else:
                        self.FieldObjects.append(Field(sqlLst[i]))
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


    def listRecs(self):

        if not self.Fault:
            self.theDataBase.do_connect()

            self.theDataBase.Crs.execute(self._SelectSql)
            self.theRecords = self.theDataBase.Crs.fetchall()
            self.NrOfRecords = len(self.theRecords)
            if self.NrOfRecords > 0:
                self.NrOfColumns = len(self.theRecords[0])
            self.theDataBase.do_close()

            # Put first rec in currrec
            self.CurrentRecNr = 0
            self.fillCurrRec(0)

    def fillCurrRec(self, arecnr):
        if arecnr < self.NrOfRecords:
            for i in range(self.NrOfColumns):
                self.FieldObjects[i].FieldValue = self.theRecords[arecnr][i]

    def nextRec(self):
        self.CurrentRecNr += 1
        if self.CurrentRecNr >= self.NrOfRecords:
            self.CurrentRecNr = self.NrOfRecords -1

        self.fillCurrRec(self.CurrentRecNr)


    def prevRec(self):
        self.CurrentRecNr -= 1
        if self.CurrentRecNr < 0:
            self.CurrentRecNr = 0

        self.fillCurrRec(self.CurrentRecNr)


    def delRec(self, theId):
        if not self.Fault:
            self.theDataBase.do_connect()
            # Stel delete statement samen
            cmnd = self.SQL_FRAGMENTS[2] % (self.TableName, self.KeyFieldObj.FieldNm, self.KeyFieldObj.FieldValue)
            self.theDataBase.Crs.execute(cmnd)
            self.theDataBase.do_post()

