import tkinter as tk
from database_manager import DatabaseManager
from electricity_calculator import ElectricityCalculator
from gui_components import ElectricityGUI


def main():
    db_manager = DatabaseManager(
        host="localhost",
        user="root",
        password="1w2qaszx3edc#Valeriia",
        database="electricity_db"
    )
    calculator = ElectricityCalculator(db_manager)
    root = tk.Tk()
    root.title("Облік електроенергії")
    app = ElectricityGUI(root, db_manager, calculator)
    root.mainloop()
    db_manager.close()


if __name__ == "__main__":
    main()
