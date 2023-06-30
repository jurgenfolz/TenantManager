from ttkthemes import ThemedTk
import tkinter as tk
from tkinter import ttk
import os
import json
from api import PBI_API
import pandas as pd
from tkinter import filedialog
import utils

class GUI:
    
    def __init__(self, theme):
        self.theme = theme
        self.application_path = os.path.dirname(os.path.abspath(__file__))
        self.data = self.read_json()
        self.result_option="Save results"
        
        self.levels_definer()
        
        self.api=PBI_API()
        self.api.authenticate()
        self.main_gui()
        
        
        

    # region Start function
    def read_json(self):
        with open(os.path.join(self.application_path, "commands.json"), 'r') as json_file:
            data = json.load(json_file)
        return data
    
    def levels_definer(self):
        self.first_level = 0
        self.second_level = 0.045
        self.third_level = 0.09
        self.fourth_level = 0.135
        self.fifth_level = 0.18
        
    # endregion
    
    # region Main GUI      
    def main_gui(self):
        self.main_window = ThemedTk(theme=self.theme)
        self.main_window.title("Tenant Manager")  # Title
        self.main_window.geometry("1280x720+50+50")  # size
        #self.main_window.resizable(0, 0)
        self.main_window.iconbitmap(self.application_path + "\\images\\logo.ico")  # icon
        # >>>Frame:
        
        
        self.main_frame = ttk.Frame(self.main_window, padding=10)
        self.main_frame.place(relx=0.5, rely=0, relwidth=1, relheight=1, anchor="n")
        
        self.create_tree()
        self.build_widgets()
        self.build_secondary_frame()
        
        
        self.main_window.lift()
        self.main_window.mainloop()
    
    #Widget builders 
    def build_widgets(self):
        # Search entry and button
        search_label = ttk.Label(self.main_frame, text="Search:")
        search_label.place(relx=0, rely=0,relheight=0.04,relwidth=0.04)
        
        self.search_entry = ttk.Entry(self.main_frame)
        self.search_entry.place(relx=0.045, rely=0,relheight=0.04,relwidth=0.25)
        self.search_entry.bind("<Return>", self.search)

    def create_tree(self):
        self.tree = ttk.Treeview(self.main_frame)
        self.tree.place(relx=0, rely=0.045, relwidth=0.295, relheight=.955)
        self.tree.heading("#0", text="List of commands")
        
        self.populate_tree()

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
    
    def build_secondary_frame(self):
        self.sec_frame = ttk.Frame(self.main_frame, padding=5, relief="groove")
        self.sec_frame.place(relx=0.3, rely=0, relwidth=0.7, relheight=1)
    
    def reset_secondary_frame(self):
        try:
            self.sec_frame.destroy()
            self.build_secondary_frame()
        except:
            pass
    
    #Functions
    def search(self, event=None):
        term = self.search_entry.get()
        # Remove all items from the tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Repopulate the tree with only the items containing the search term
        self.populate_tree(term)

    
    def populate_tree(self, search=None):
        for key in self.data:
            matching_items = [item for item in self.data[key] 
                            if search is None or search.lower() in item.lower()]
            if matching_items:
                parent = self.tree.insert("", "end", text=key)
                for item in matching_items:
                    self.tree.insert(parent, "end", text=item)

        # Automatically expand all items
        if not search is None:
            for item in self.tree.get_children():
                self.tree.item(item, open=True)
    # endregion
    
    
    def on_tree_select(self, event):
        item_id = self.tree.selection()[0]
        parent_id = self.tree.parent(item_id)
        if parent_id:  # If the item has a parent, it's a second-level item
            item_text = self.tree.item(item_id, "text")
            
            #Build the frames
            if item_text.lower()=="get workspaces as admin":
                self.build_frame_workspaces_as_admin()
    
    # region Admin functions builder
    
    def results_options_builder(self):
        self.result_option = tk.StringVar(value=self.result_option)  # Assuming self.result_option is initialized in __init__

        rb1 = ttk.Radiobutton(self.sec_frame, text="Show table", variable=self.result_option, value="Show table")
        rb1.place(relx=0.4, rely=self.first_level, relwidth=0.2, relheight=0.04)

        rb2 = ttk.Radiobutton(self.sec_frame, text="Save results", variable=self.result_option, value="Save results")
        rb2.place(relx=0.6, rely=self.first_level, relwidth=0.2, relheight=0.04)

        rb3 = ttk.Radiobutton(self.sec_frame, text="Show json", variable=self.result_option, value="Show json")
        rb3.place(relx=0.8, rely=self.first_level, relwidth=0.2, relheight=0.04)
        
        self.response_label=ttk.Label(self.sec_frame, text="")
        self.response_label.place(relx=0.2, rely=self.third_level, relwidth=0.2, relheight=0.04)
    
    def build_frame_workspaces_as_admin(self):
        self.reset_secondary_frame()
        self.build_secondary_frame()
        
        label=ttk.Label(self.sec_frame, text="Workspaces as admin")
        label.place(relx=0, rely=self.first_level, relwidth=0.2, relheight=0.04)
        
        label=ttk.Label(self.sec_frame, text="Number of workspaces")
        label.place(relx=0.2, rely=self.second_level, relwidth=0.2, relheight=0.04)
        
        self.number_of_workspaces=ttk.Entry(self.sec_frame)
        self.number_of_workspaces.place(relx=0, rely=self.second_level, relwidth=0.195, relheight=0.04)
        self.number_of_workspaces.insert(0, "1000")
        
        
        
        self.results_options_builder()
        
        run_btn=ttk.Button(self.sec_frame, text="Get workspaces", command=self.get_workspaces_as_admin)
        run_btn.place(relx=0, rely=self.third_level, relwidth=0.195, relheight=0.04)
        
    def get_workspaces_as_admin(self):
        top=self.number_of_workspaces.get()
        run_api = False
        try:
            top=int(top)
            run_api=True
        except:
            tk.messagebox.showerror(title='Error', message="Please enter a number")
    
        if run_api:
            
            try:
                response=self.api.admin_workspaces(top=top)
                self.response_label['text']=f'Success {response.status_code}'
                
                if self.result_option.get()=='Show table':
                    self.show_df_cmd(self.api.df_workspaces_admin)
                elif self.result_option.get()=='Save results':
                    self.save_df_cmd(self.api.df_workspaces_admin)
                elif self.result_option.get()=='Show json':
                    self.show_json_cmd(self.api.df_workspaces_admin)
            
            except Exception as e:
                self.response_label['text']=utils.api_error(e)
                tk.messagebox.showerror(title='Error', message=str(e))
                
        
    # endregion
    

    # region print functions
    def save_df_cmd(self,df:pd.DataFrame):
        # Open save file dialog
        filepath = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Excel Files', '*.xlsx'), ('All Files', '*.*')],
        )
        
        # If the user doesn't cancel the dialog
        if filepath:
            try:
                # Save the dataframe as an excel file
                df.to_excel(filepath, index=False)
                return "Saved"
            except Exception as e:
                # If there's an error, show a message box with the error
                tk.messagebox.showerror(title='Error', message=str(e)) 
                return "Error"
        else:
            return "Cancelled"
        
    def show_df_cmd(self, df:pd.DataFrame):
        
        cmdGUI = ThemedTk(theme=self.theme)

        # Main window settings
        cmdGUI.title("API Response")  # Title
        cmdGUI.geometry("1280x720+50+50")  # size
        cmdGUI.minsize(1280, 720)
        cmdGUI.iconbitmap(self.application_path + "\\images\\logo.ico")  # icon
        
        
        cmdframe = ttk.Frame(cmdGUI)
        cmdframe.pack(fill='both', expand=True)

        # Create scrollbars
        vsb = ttk.Scrollbar(cmdframe, orient="vertical")
        hsb = ttk.Scrollbar(cmdframe, orient="horizontal")

        # Create the Treeview
        tree = ttk.Treeview(cmdframe, columns=df.columns, show='headings',
                            yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        

        # Add each column from DataFrame
        for i, column in enumerate(df.columns):
            tree.heading(i, text=column, command=lambda col=i: sort_by(tree, col, 0))
            tree.column(i, stretch=tk.YES)

        # Add data to Treeview
        for index, row in df.iterrows():
            row_as_list = list(row)
            row_as_str = [str(x).replace('\n', ' ') for x in row_as_list]
            tree.insert("", "end", values=row_as_str)

        def sort_by(tree, col, descending):
            """Sort tree contents when a column is clicked on."""
            # grab values to sort
            data = [(tree.set(child, col), child) for child in tree.get_children('')]

            # reorder data
            data.sort(reverse=descending)
            for idx, item in enumerate(data):
                tree.move(item[1], '', idx)

            # switch the heading so that it will sort in the opposite direction
            tree.heading(col,
                        command=lambda col=col: sort_by(tree, col, int(not descending)))

            
        # Create a context menu
        menu = tk.Menu(cmdGUI, tearoff=0)

        def copy_row():
            selected_item = tree.selection()[0]  # Get selected item
            row_content = tree.item(selected_item)['values']
            row_str = '\t'.join(row_content)
            cmdGUI.clipboard_clear()
            cmdGUI.clipboard_append(row_str)

        def copy_table():
            df.to_clipboard(index=False)
            

        menu.add_command(label="Copy Row", command=copy_row)
        menu.add_command(label="Copy Table", command=copy_table)

        def display_menu(event):
            # Display the context menu
            menu.post(event.x_root, event.y_root)

        # Bind the right-click event to the display_menu function
        tree.bind("<Button-3>", display_menu)

        # Configure scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

        tree.pack(fill='both', expand=True)
    # endregion 
                    
if __name__ == "__main__":
    gui = GUI('equilux')
    