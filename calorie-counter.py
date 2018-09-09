from MainWindow import Ui_MainWindow

import sys
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib
from datetime import date, datetime, timedelta
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

class MainCalorieWindow(Ui_MainWindow):
    def __init__(self):
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.horizontalSlider.valueChanged.connect(self.slider_value_changed)
        self.submit_button.clicked.connect(self.submitButtonClicked)
        self.checkBox.stateChanged.connect(self.checkbox_changed)
        self.get_entries_button.clicked.connect(self.getEntriesButtonClicked)
        self.graph_button.clicked.connect(self.graphEntriesButtonClicked)
        self.delete_entries_button.clicked.connect(self.deleteEntries)
        self.sliderValue = self.horizontalSlider.value()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Food", "Calories", "Date/Time"])
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnWidth(0, 40)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        return
    
    def check_daily_limit(self):
        try:
            self.tot_cals = self.totalCals
        except:
            return
            
            
        print("%s, %s" % (self.tot_cals, self.totalCals))
        if self.sliderValue < self.tot_cals:
            self.label_7.show()
        else:
            self.label_7.hide()

    def slider_value_changed(self):
        self.sliderValue = self.horizontalSlider.value() * 50
        self.label_6.setText(str("%s Cal" % (self.sliderValue)))
        self.check_daily_limit()
        
        
        
    def showErrorMsgBox(self):
        self.result = QMessageBox.question(self, 'Come on man!', "Please enter a food name (as text) and the ammount of calories (as a digit).", QMessageBox.Ok , QMessageBox.Ok)
            
    def showSubmitMsgBox(self, food_name, food_calories):
         self.result = QMessageBox.question(self, 'Submit food?', "Are you sure you want to submit the food: %s cotaining %s calories?" % (food_name, food_calories), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

         if self.result == QMessageBox.Yes:
             return True
         else:
             return False
             
    def showDeleteMsgBox(self, number_of_elements):
         if number_of_elements < 1:
            self.result = QMessageBox.question(self, 'Come on!?', "You have to select at least one row!", QMessageBox.Ok, QMessageBox.Ok)
            return False
         if number_of_elements == 1:
            self.result = QMessageBox.question(self, 'Permanently delete entry?', "Are you sure you want to permanently delete this %i selected item?" % (number_of_elements), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
         else:
            self.result = QMessageBox.question(self, 'Permanently delete entries?', "Are you sure you want to permanently delete these %i selected items?" % (number_of_elements), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

         if self.result == QMessageBox.Yes:
            return True
         else:
            return False
             
             
    def generate_graph(self, date):
        
        self.dateString = str(date)
		
        matplotlib.rcParams['toolbar'] = 'None'
        plt.ylabel('Calories')
        plt.xlabel('Time of day')
    
        
        x_list = []
        y_list = []
        
        
        self.cur = self.connection.cursor()
        self.result = self.cur.execute("select * from entries where strftime('%Y-%m-%d', datetime) = ? ORDER BY datetime(datetime) ASC", (self.dateString,))
        data = self.result.fetchall()
        
        for row in data:
            x_dateTimeString = datetime.strftime(row[3], "%Y-%m-%d %H:%M:%S")
            x_datetime = datetime.strptime(x_dateTimeString, "%Y-%m-%d %H:%M:%S")
            y_list.append(int(row[2]))
            #x_list.append("%s:%s" % (x_datetime.hour, x_datetime.minute))
            #x_list.append(datetime.time(x_datetime))
            x_list.append(x_datetime)

        try:
            x_min = min(x_list)
            x_max = max(x_list)
            y_min = min(y_list)
            y_max = max(y_list)
        except:
            return
    
        plt.axis([x_min, x_max, y_min, y_max])
        plt.gca().xaxis.set_major_formatter(md.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(md.MinuteLocator(byminute=[0,30]))
        plt.ylim(y_min-100, y_max+100)
        plt.xlim(x_min - timedelta(minutes=30), x_max + timedelta(minutes=30))
        plt.plot(x_list, y_list, '--bo')
        plt.gcf().autofmt_xdate()
        plt.gcf().canvas.set_window_title(x_dateTimeString[:-8])
        plt.show() 
    
    def checkbox_changed(self):
        if self.checkBox.isChecked():
            self.timeEdit.setEnabled(False)
            return
        else:
            self.timeEdit.setEnabled(True)
            return      
             
    def get_rows_by_date(self, date):
        self.dateString = str(date)
        
        #self.rows = self.cur.fetchall()
        self.cur = self.connection.cursor()
        self.result = self.cur.execute("select * from entries where strftime('%Y-%m-%d', datetime) = ? ORDER BY datetime(datetime) ASC", (self.dateString,))
        
        self.tableWidget.setRowCount(0)
        
        self.tot_cals = [0]
        
        for row_number, row_data in enumerate(self.result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                if column_number == 3:
                    data = data.strftime('%Y-%m-%d %H:%M')
                    item = QtWidgets.QTableWidgetItem(str(data))
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(item))
                    #self.tableWidget.resizeColumnsToContents()
                else:
                    item = QtWidgets.QTableWidgetItem(str(data))	
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(item))
                    #self.tableWidget.resizeColumnsToContents()
                    if column_number == 2:
                        self.tot_cals.append(data)
						
        else:
            pass
        
        self.totalCals = sum(self.tot_cals)
        self.label_4.setText("Total: %s Calories" % (self.totalCals))
        self.check_daily_limit()
        
    def submitButtonClicked(self):
        self.food = self.textEdit.toPlainText()
        self.calories = self.textEdit_2.toPlainText()
        
        if len(self.food) <= 0 or self.calories.isdigit() == False:
            self.showErrorMsgBox()
            return
        
        if self.showSubmitMsgBox(self.food, self.calories):
            self.submitFoodToDb(self.food, self.calories)
    
    def graphEntriesButtonClicked(self):
        self.theDate = self.calendarWidget.selectedDate()
        self.generate_graph(self.theDate.toPyDate())
            
    def getEntriesButtonClicked(self):
        self.theDate = self.calendarWidget.selectedDate()
        self.get_rows_by_date(self.theDate.toPyDate())
        
    def submitFoodToDb(self, food_text, calories_text):
        if self.checkBox.isChecked():
            self.curr_datetime = datetime.now()
        else:
            self.curr_datetime = datetime.now().replace(hour=self.timeEdit.time().hour(), minute=self.timeEdit.time().minute())

        self.connection.execute("INSERT INTO entries(food_name, calories, datetime) values (?, ?, ?)", (food_text, calories_text, self.curr_datetime))
        self.connection.commit()

    def connectToDB(self):
        # Create database connection object   
        self.connection = sqlite3.connect('sqlite3.db', detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.row_factory = sqlite3.Row
        self.cur = self.connection
        self.checkTableExists(self.cur, "entries")
        
    def deleteEntries(self):
        allRows = self.tableWidget.selectionModel().selectedRows()
        rowCount = len(allRows)
        
        if self.showDeleteMsgBox(rowCount):
            for row in allRows:
				# This row.data shit only works because the QModelIndex for each row happens to point to the column 0
                dbItemIndex = row.data()
                #print(dbItemIndex)
                self.connection.execute("DELETE FROM entries WHERE ID = ?;", (dbItemIndex,))
                self.connection.commit()
                print("%s deleted!" % (dbItemIndex))
		
		# Update table widget
        self.theDate = self.calendarWidget.selectedDate()
        self.get_rows_by_date(self.theDate.toPyDate())    
        
    def checkTableExists(self, dbcon, tablename):
        dbcur = dbcon.cursor()
        dbcur.execute("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table' AND name = 'entries'
            """)
        if dbcur.fetchone()[0] == 1:
            dbcur.close()
            print("Table exists")
            return True
        else:
            dbcur.execute("""
            CREATE TABLE entries 
            (id integer primary key, 
            food_name text, calories integer, 
            datetime timestamp)
            """)
        print("Table created")
        dbcur.close()
        return False
    
		
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainCalorieWindow = MainCalorieWindow()
    mainCalorieWindow.setFixedSize(mainCalorieWindow.size())
    mainCalorieWindow.connectToDB()
    mainCalorieWindow.show()
    sys.exit(app.exec_())
