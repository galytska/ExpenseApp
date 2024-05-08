import sys

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QTableWidget, \
    QLabel, QDateEdit, QComboBox, QLineEdit, QPushButton, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


class ExpenseApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Expense Tracker')
        self.resize(700, 500)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.category_combobox = QComboBox()
        self.category_combobox.addItems(
            ['Food', 'Transportation', 'Rent', 'Shopping', 'Entertainment', 'Bills', 'Other'])
        self.amount_lineedit = QLineEdit()
        self.description_lineedit = QLineEdit()
        self.add_expense_button = QPushButton('Add Expense')
        self.add_expense_button.clicked.connect(self.add_expenses)
        self.delete_expense_button = QPushButton('Delete Expense')
        self.delete_expense_button.clicked.connect(self.delete_expenses)
        self.table = QTableWidget()
        header_names = ['Id', 'Date', 'Category', 'Amount', 'Description']
        self.table.setColumnCount(len(header_names))
        self.table.setHorizontalHeaderLabels(header_names)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.sortByColumn(1, Qt.DescendingOrder)

        # Design
        self.setStyleSheet("""
                                   QWidget {background-color: #dfe6da;}

                                   QLabel{
                                        color: #333;
                                        font-size: 14px;
                                        }

                                   QLineEdit, QComboBox, QDateEdit{
                                        background-color: #dfe6da;
                                        color: #333;
                                        border: 1px solid #444;
                                        padding: 5px;
                                        }

                                   QTableWidget{
                                        background-color: #dfe6da;
                                        color: #333;
                                        border: 1px solid #444;
                                        selection-background-color: #ddd;
                                        }

                                   QPushButton{
                                        background-color: #4caf50;
                                        color: #fff;
                                        border: none;
                                        padding: 8px 16px;
                                        font-size: 14px;
                                        }

                                   QPushButton:hover{background-color: #45a049;}
                                   """)

        main_layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()
        row1.addWidget(QLabel('Date:'))
        row1.addWidget(self.date_edit)
        row1.addWidget(QLabel('Category:'))
        row1.addWidget(self.category_combobox)
        row2.addWidget(QLabel('Amount:'))
        row2.addWidget(self.amount_lineedit)
        row2.addWidget(QLabel('Description:'))
        row2.addWidget(self.description_lineedit)
        row3.addWidget(self.add_expense_button)
        row3.addWidget(self.delete_expense_button)

        main_layout.addLayout(row1)
        main_layout.addLayout(row2)
        main_layout.addLayout(row3)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
        self.load_table()

    def load_table(self):
        query = QSqlQuery()
        query.exec("""
        SELECT * FROM expenses
        """)

        self.table.setRowCount(0)
        row = 0
        while query.next():
            expense_id = query.value(0)
            date = query.value(1)
            category = query.value(2)
            amount = query.value(3)
            description = query.value(4)

            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(expense_id)))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(category))
            self.table.setItem(row, 3, QTableWidgetItem(str(amount)))
            self.table.setItem(row, 4, QTableWidgetItem(description))

            row += 1

    def add_expenses(self):
        date = self.date_edit.date().toString('yyyy-MM-dd')
        category = self.category_combobox.currentText()
        amount = self.amount_lineedit.text()
        description = self.description_lineedit.text()

        query = QSqlQuery()
        query.prepare("""
        INSERT INTO expenses (date, category, amount, description)
        VALUES (?,?,?,?)
        """)
        query.addBindValue(date)
        query.addBindValue(category)
        query.addBindValue(amount)
        query.addBindValue(description)
        query.exec()

        self.date_edit.setDate(QDate.currentDate())
        self.category_combobox.setCurrentIndex(0)
        self.amount_lineedit.clear()
        self.description_lineedit.clear()

        self.load_table()

    def delete_expenses(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'No expenses chosen', 'Please choose expenses to delete')
            return

        result = QMessageBox.question(self, 'Are you sure', "Delete expenses?", QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.No:
            return

        expenses_id = int(self.table.item(selected_row, 0).text())
        query = QSqlQuery()
        query.prepare("""
                    DELETE FROM expenses WHERE id=?
                    """)
        query.addBindValue(expenses_id)
        query.exec()

        self.load_table()


database = QSqlDatabase.addDatabase('QSQLITE')
database.setDatabaseName('expense.db')
if not database.open():
    QMessageBox.critical(None, 'Error', 'Could not open database')
    sys.exit(1)

query = QSqlQuery()
query.exec("""
    CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount REAL,
    description TEXT
    )
""")

if __name__ == '__main__':
    app = QApplication([])
    main_window = ExpenseApp()
    main_window.show()
    app.exec()
