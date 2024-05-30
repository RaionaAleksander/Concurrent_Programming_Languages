'''

Subject: Concurrent Programming Languages (Paralleelprogrammeerimise keeled)
Work: Project
Student: Aleksander Ontin

'''

#################  Python Modules  #################

# Module for GUI - Python interface to Tcl/Tk and Tk themed widgets
import tkinter as tk # https://docs.python.org/3/library/tkinter.html
from tkinter import ttk # https://docs.python.org/3/library/tkinter.ttk.html

# Module for FTP - FTP protocol client
from ftplib import FTP # https://docs.python.org/3/library/ftplib.html

# Module for URL - Parse URLs into components
    # https://docs.python.org/3/library/urllib.html
from urllib.parse import urlparse # https://docs.python.org/3/library/urllib.parse.html

# Miscellaneous operating system interfaces
import os # https://docs.python.org/3/library/os.html

# Thread-based parallelism
import threading # https://docs.python.org/3/library/threading.html

# Time access and conversions
import time # https://docs.python.org/3/library/time.html


# Files from BNRB, what we can use:
    # ftp://ftp.bmrb.io/pdb/holdings/all_removed_entries.json.gz
    # ftp://ftp.bmrb.io/pdb/holdings/current_file_holdings.json.gz
    # ftp://ftp.bmrb.io/pdb/holdings/obsolete_experimental_data_last_modified_dates.json.gz
    # ftp://ftp.bmrb.io/pdb/holdings/obsolete_structures_last_modified_dates.json.gz
    # ftp://ftp.bmrb.io/pdb/holdings/refdata_id_list.json.gz
    # ftp://ftp.bmrb.io/pdb/holdings/released_experimental_data_last_modified_dates.json.gz
    # ftp://ftp.bmrb.io/pdb/holdings/released_structures_last_modified_dates.json.gz
    # ftp://ftp.bmrb.io/pdb/holdings/unreleased_entries.json.gz


############  Tkinter FTPDownloaderGUI  ############

class FTPDownloaderGUI:
    def __init__(self, master):
        self.master = master
        master.title("FTPDownloaderGUI") # Give the screen a name
        master.geometry("1100x600") # Set the length and width of the screen
        master.resizable(False, False) # Does not allow you to resize the screen
        master.iconbitmap("326639_download_file_icon.ico") # Icon for the window
            # You can download icons there: https://www.iconfinder.com/

        # Create a frame row for the label with the text "URL:", input field and button for downloading the file
        frame_row = ttk.Frame(master)
        frame_row.grid(row=0, column=0, pady=10, padx=36)
        
        # Create a label with the bold text "URL:" and add it to the frame row
        self.label_url = ttk.Label(frame_row, text="URL:", font=tk.font.Font(weight="bold"))
        self.label_url.grid(row=0, column=0, pady=12, padx=2, sticky="e")

        # Create an input field and add it to a frame row
        self.entry_url = ttk.Entry(frame_row, width=72)
        self.entry_url.grid(row=0, column=1, pady=12, padx=10, sticky="ew")

        # Create a button with the text " Download " and add it to the frame row
            # Clicking the button activates the "start_download" function
        self.btn_download = tk.Button(frame_row, text=" Download ", command=self.start_download)
        self.btn_download.configure(foreground="white", background="black") # Makes the button black with white text
        self.btn_download.grid(row=0, column=2, pady=12, padx=4, sticky="w")

        # Center the first line
        master.columnconfigure(0, weight=1)
        
        # File slots are created in a for-loop
            # There are a maximum of 8 slots in total and each contains a label and progress bar
        for i in range(8):
            # Create a label where the file name will be located in the future
                # Initially the file name is not there and it is written that this is a slot for some file that is not used
            process_label = ttk.Label(master, text=f"File {i + 1} slot  (not used)", font=tk.font.Font(weight="bold"))
            process_label.place(x=50, y=i*60 + 120) # For convenience, the labels are placed by coordinates
            Processes_labels.append(process_label) # Label is added to the list "Processes_labels" so that it can be accessed by index
            
            # Create a deterministic horizontal progress bar that will show the progress of a file download
                # Initially the file is not downloaded, so the value is set to 0, i.e. 0%
            process_bar = ttk.Progressbar(master, orient="horizontal", length=400, mode="determinate")
            process_bar.place(x=648, y=i*60 + 124) # For convenience, the progress bars are placed by coordinates
            Processes_bars.append(process_bar) # Progress bar is added to the list "Processes_bars" so that it can be accessed by index


#################  Start Download  #################

    # The function "start_download" prepares for downloading a file via an ftp link
        # This function has several tasks:
            # 1. to check the data that the user has entered or pasted
                # and in case of a problem to show the user an error window and then terminate the function.
            # 2. to select an not used slot for file download
                # and in case of a problem to show the user an error window that there is no space available and you need to wait.
            # 3. to create a thread that goes to do its job of downloading the file
    def start_download(self):
        # Getting FTP URL from the input field
        url = self.entry_url.get()
        
        # We check whether the input field is empty
        # If empty, an error window appears. If not empty, the program will continue to work
        if not url:
            print("Error: Empty input field!")
            tk.messagebox.showerror("Error", "Empty input field!")
            return
        
        # We check whether the url is not valid
        # If not valid, an error window appears. If valid, the program will continue to work
        if not self.is_valid_url(url):
            print("Error: Please enter a valid URL!")
            tk.messagebox.showerror("Error", "Please enter a valid URL!")
            return
        
        # We check whether the url is not ftp url
        # If not ftp, an error window appears. If ftp, the program will continue to work
        if not self.is_ftp_url(url):
            print("Error: Please enter an ftp link, not https or http!")
            tk.messagebox.showerror("Error", "Please enter an ftp link, not https or http!")
            return
        
        #print(url)
                
        is_okei = False # variable "is_okei" that determines whether a free (not used) slot has been found or not
        for i in range(8):
            if is_the_space_available[i]: # if space is available for the file (is_the_space_available[i] is True)
                is_okei = True # variable "is_okei" becomes true because a slot for downloading the file has been found
                is_the_space_available[i] = False # the "is_space_available" with i index becomes False because it becomes occupied
                
                path_parts = url.replace("ftp://", "").split("/") # creates a list that consists of the url link elements, except for the protocol
                
                # Example:
                    # url = ftp://ftp.bmrb.io/pdb/holdings/all_removed_entries.json.gz
                    # path_parts = ["ftp.bmrb.io", "pdb", "holdings", "all_removed_entries.json.gz"]
                
                domain_name = path_parts[0] # domain_name, which is the first element of the list "path_parts"
                #print(f"Domain name: {domain_name}")
                
                download_file = path_parts[-1] # download_file, which is the last element of the list "path_parts"
                #print(f"Download file: {download_file}")
                
                # We check whether the link contains the file
                # If f it does not contain a file, an error window appears. If contains, the program will continue to work
                if download_file == "":
                    print("Error: Please specify the file name in the URL!")
                    tk.messagebox.showerror("Error", "Please specify the file name in the URL!")
                    is_the_space_available[i] = True
                    return
                    
                path_to_file = "/".join(path_parts[1:-1]) # path_to_file
                #print(f"Path to file: {path_to_file}")
                
                # Create a thread that will use the "download_file_ftp" function
                # The thread uses variables such as path_to_file, domain_name, download_file and i
                thread = threading.Thread(
                    target=self.download_file_ftp,
                    args=(path_to_file, domain_name, download_file, i)
                )
                
                thread.start() # The thread is starting to work
                
                break # The break statement is used to terminate the loop immediately when it is encountered
        
        # If no non used slots were found, the user is presented with an error window that asks them to wait
        # If this does not happen, the error window is not shown
        if not is_okei:
            print("Error: No space to download files! Please wait for the file to download!")
            tk.messagebox.showerror("Error", "No space to download files! Please wait for the file to download!")


##################  Is valid URL  ###################

    # is_valid_url is a function that checks that a string is a valid URL
        # Input data: string (url that the user gave)
        # Output data: True or False
            # True, if the string is correct (valid) url
            # False, if not
    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


###################  Is FTP URL  ####################

    # is_ftp_url is a function that checks that an url is a ftp URL
        # Input data: string (url that the user gave)
        # Output data: True or False
            # True, if the string is ftp url
            # False, if not
    def is_ftp_url(self, url):
        result = urlparse(url)
        return result.scheme.lower() == 'ftp'


################  Download File FTP  ################

    # download_file_ftp is a function that downloads a file via ftp protocol
        # Input data: path_to_file, domain_name, download_file, index
        # The function returns nothing
    def download_file_ftp(self, path_to_file, domain_name, download_file, index):
        
        Processes_labels[index].config(text=download_file) # A label with a certain index has the text of a specific file
        Processes_bars[index]["value"] = 0 # Just in case, we make the progress bar empty
        
        ftp = None
        try:
            
            ftp = FTP(domain_name) # Creating an FTP object
            
            ftp.login(USERNAME, PASSWORD) # Authentication on the FTP server
            
            ftp.cwd(path_to_file) # Changing the current working directory on the FTP server
            
            file_size = ftp.size(download_file) # Getting the file size on the FTP server
            
            download_folder = os.path.abspath("downloads") # Get the absolute path to the folder "downloads" and save it in the variable "download_folder"
            os.makedirs(download_folder, exist_ok=True) # Create the "downloads" folder if it doesn't exist
                # exist_ok=True avoids an error if the folder already exists
                
            # The following six lines of code are needed to create unique files if the user uses the same URL multiple times
            base_name, extension = os.path.splitext(download_file) # Separate the file name and its extension
            count = 1 # Initialize the variable "count" to create a unique file name if a file with this name already exists
            new_download_file = download_file # Copy the name of the downloaded file into a new variable "new_download_file"
            while os.path.exists(os.path.join(download_folder, new_download_file)): # Check if the file with the name
                new_download_file = f"{base_name} ({count}){extension}" # If a file with this name already exists, add a counter to the file name to create a unique name
                count += 1 # variable "count" is incremented by 1
            
            download_path = os.path.join(download_folder, new_download_file) # Create the full path to the new file
            
            with open(download_path, 'wb') as file: # Open the file in binary format for writing ('wb')
                def callback(data): # A callback function "callback" that will be called when a block of data is received while downloading a file
                    file.write(data) # Write the obtained data to an open file
                    Processes_bars[index]["value"] += (len(data) / file_size) * 100 # Update the progress bar value according to the amount of transferred data relative to the total file size
                    time.sleep(0.05) # Insert a small pause (50 milliseconds) after each data block. 
                        # This is needed to smoothly show how the interface works.
                    
                ftp.retrbinary(f"RETR {download_file}", callback) # Call the retrbinary method to download a file from an FTP server
            
            Processes_bars[index]["value"] = 100 # Progress bar is full (100%)
        
        except Exception as e: # If an error occurs
            print(f"Error during FTP download: {e}")
            tk.messagebox.showerror("Error during FTP download", f"Error during FTP download: {e}")

        finally: # A block of code that will be executed anyway, even if an exception occurs in the try block
            if ftp: # Check if an ftp object exists (FTP connection)
                ftp.quit() # Call the quit() method to terminate the FTP session correctly
                
            Processes_bars[index]["value"] = 0 # Now progress bar is empty
            Processes_labels[index].config(text=f"File {index + 1} slot  (not used)") # Write the former name of the label with a certain index
            is_the_space_available[index] = True # We make the variable True, since space has been freed up


################  Global Variables  #################

# List consisting of boolean values, which means whether the slot for downloading the file is free or not
is_the_space_available = [True] * 8
# List in which Tkinter Labels are stored and can be accessed by an index
Processes_labels = []
# List in which Tkinter Progress bars are stored and can be accessed by an index
Processes_bars = [] #

# The user's username and password, which is anonymous
USERNAME = "anonymous"
PASSWORD = "anonymous"


###################  Main Window  ###################

# Create the main window
root = tk.Tk()

# Creates an object of the FTPDownloaderGUI class
app = FTPDownloaderGUI(root)

# Launch the main event loop
root.mainloop()