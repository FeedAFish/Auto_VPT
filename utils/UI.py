import tkinter as tk
from tkinter import ttk
import csv
import os


class CSVViewer:
    def __init__(self, file_path):
        # Set up the main window
        self.root = tk.Tk()
        self.root.title("CSV Viewer")
        self.root.geometry("600x180")
        self.root.resizable(False, False)

        # Data initiates
        self.file_path = file_path
        self.current_page = 0
        self.rows_per_page = 5

        # Load data from the CSV file
        self.data = self.load_csv_data()

        # Set up the UI
        self.setup_ui()

    # Data Load and save
    def load_csv_data(self):  # Load data
        if not os.path.exists(self.file_path):
            self.create_empty_csv()
        with open(self.file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
        return data

    def save_csv_data(self):  # Save data
        with open(self.file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.data)

    def create_empty_csv(self):  # Create an empty CSV file
        columns = ["ID", "Name", "Server", "Account", "Password"]
        with open(self.file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            csvfile.write(",".join(columns) + "\n")

    # UI setup
    def setup_ui(self):
        self.tree = ttk.Treeview(
            self.root,
            columns=[f"col{i}" for i in range(len(self.data[0]))],
            show="headings",
            height=self.rows_per_page,
        )

        # Set up column headings
        for i, column in enumerate(self.data[0]):
            self.tree.heading(f"# {i+1}", text=column)

        # Automatically adjust column widths to fit content
        for i in range(len(self.data[0]) - 1):
            max_width = max(len(str(row[i])) for row in self.data)
            self.tree.column(
                f"# {i+1}", width=max_width * 10 + 10, anchor=tk.W, stretch=False
            )

        self.tree.column(f"# {len(self.data[0])}", minwidth=100, stretch=tk.YES)

        self.tree.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        # Buttons to navigate pages
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)

        button_list = {
            "Previous": self.show_prev_page,
            "Next": self.show_next_page,
            "Remove Selected": self.remove_selected,
            "Add Row": self.add_row,
        }
        for text, command in button_list.items():
            button = tk.Button(button_frame, text=text, command=command)
            button.pack(side=tk.LEFT, padx=5)
        # Show initial data
        self.update_tree()

    # Handle page navigation
    def update_tree(self):
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Get data for the current page
        start_idx = 1 + self.current_page * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.data[start_idx:end_idx]

        # Insert new data
        for row in page_data:
            self.tree.insert("", tk.END, values=row)

    def remove_selected(self):  # Remove selected data
        """Remove the selected row from the data."""
        selected_item = self.tree.selection()
        if selected_item:
            # Get the selected item's values
            values = self.tree.item(selected_item, "values")

            # Find and remove the row from data
            for idx, row in enumerate(self.data):
                if list(row) == list(values):
                    del self.data[idx]
                    break

            # Save the updated data back to the CSV file
            self.save_csv_data()

            # Update the treeview
            self.update_tree()

    def add_row(self):
        new_row_window = tk.Toplevel(self.root)
        new_row_window.title("Add New Account")

        if len(self.data) > 1:  # Ensure the first row is skipped (header row)
            ids = [
                int(row[0]) for row in self.data[1:]
            ]  # Extract the first column (ID)
            next_id = max(ids) + 1
        else:
            next_id = 1

        entries = []
        for i, column in enumerate(self.data[0]):
            if i == 0:
                continue
            tk.Label(new_row_window, text=column).grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(new_row_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)

        def save_new_row():
            new_row = [next_id] + [entry.get() for entry in entries]
            self.data.append(new_row)
            self.save_csv_data()
            self.data = self.load_csv_data()
            self.update_tree()
            new_row_window.destroy()

        tk.Button(new_row_window, text="Save", command=save_new_row).grid(
            row=len(self.data[0]), column=0, columnspan=2, pady=10
        )

    def show_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_tree()

    def show_next_page(self):
        if (self.current_page + 1) * self.rows_per_page < len(self.data) - 1:
            self.current_page += 1
            self.update_tree()
