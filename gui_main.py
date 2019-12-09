import time
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
from Client import Client as client


class gui():
    def fileDialog(self):
        self.file_path = filedialog.askopenfilename(initialdir="/home", title="Select file", filetypes=(
            ("txt files", "*.txt"), ("jpeg files", "*.jpg"), ("all files", "*.*")))
        print(self.file_path)
        self.file_path_label = Label(self.window, text="file_path", font=("Arial Bold", 10))
        self.file_path_label.grid(column=0, row=10)
        self.empty_lbl_5 = Label(self.window, text=self.file_path, font=("Arial Bold", 10))
        self.empty_lbl_5.grid(column=1, row=10)

    def if_downloaded(self):
        messagebox.showinfo("Download Info",
                            "The file has been downloaded! \nThe file path:" + str(self.downloaded_file_path))

    def adding_server_ip(self):
        messagebox.showinfo("Server IP", "The server has been connected!")
        self.server_IP = self.server_address_input.get()
        self.client_module = client(self.server_IP, 6969)
        self.client_module.initiate_connection()
        self.get_my_id()

    def get_my_id(self):
        self.my_ID = self.client_module.client_id
        self.my_id_label = Label(self.window, text=self.my_ID, font=("Arial Bold", 20), borderwidth=2, relief="sunken")
        self.my_id_label.grid(column=1, row=4)

    def close_window(self):
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.window.destroy()
            print("Window closed")
            if self.client_module is not None:
                self.client_module.close_connection()
            self.window.quit()

    def add_destination_id(self):
        return self.txt_destinaiton.get()  # on add button processed

    def send_file_tcp(self):
        destination_id = self.add_destination_id()
        self.client_module.send_file(self.file_path, destination_id)

    def __init__(self):
        self.client_module = None
        self.my_ID = None

        self.window = Tk()
        self.window.title('Kugburkalimetr')
        self.window.geometry('610x400+700+500')
        self.window.minsize(610, 400)
        self.window.maxsize(610, 400)
        self.downloaded_file_path = 'dupa'

        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        self.empty_lbl_1 = Label()
        self.empty_lbl_1.grid(column=0, row=1)

        self.server_address_label = Label(self.window, text="Server IP4 address ", font=("Arial Bold", 20))
        self.server_address_label.grid(column=0, row=2)

        self.server_address_input = Entry(self.window, width=17, text="plant", justify=CENTER, bd=5,
                                          font=("Arial Bold", 18))
        self.server_address_input.grid(column=1, row=2)

        self.ip_button_connect = Button(self.window, text="Connect", command=self.adding_server_ip, height=2, width=5,
                                        padx=10)
        self.ip_button_connect.grid(column=3, row=2)

        self.empty_lbl = Label(self.window, text=" ")
        self.empty_lbl.grid(column=2, row=2)
        self.empty_lbl = Label(self.window, text=" ")
        self.empty_lbl.grid(column=0, row=3)

        self.your_id_label = Label(self.window, text="Your ID", font=("Arial Bold", 20))
        self.your_id_label.grid(column=0, row=4)

        self.empty_lbl_2 = Label(self.window, text="", justify=CENTER, font=("Arial Bold", 20))
        self.empty_lbl_2.grid(column=0, row=5)

        self.destination_id_label = Label(self.window, text="Destination ID ", font=("Arial Bold", 20))
        self.destination_id_label.grid(column=0, row=7)

        self.txt_destinaiton = Entry(self.window, width=17, justify=CENTER, bd=5, font=("Arial Bold", 18))
        self.txt_destinaiton.grid(column=1, row=7)

        # self.destination_button = Button(self.window, text="Add", command=self.add_destination_id, height=2, width=5,
        #                                 padx=10)
        # self.destination_button.grid(column=3, row=7)

        self.empty_lbl_3 = Label(self.window, text="", font=("Arial Bold", 20))
        self.empty_lbl_3.grid(column=0, row=7)
        self.empty_lbl_4 = Label(self.window, text="", font=("Arial Bold", 20))
        self.empty_lbl_4.grid(column=0, row=8)

        self.browser_button_file = Button(self.window, text="Browse A File", command=self.fileDialog, height=5, width=9)
        self.browser_button_file.grid(column=0, row=9)

        self.bar = Progressbar(self.window, length=200, style='black.Horizontal.TProgressbar', mode='determinate')
        self.bar['maximum'] = 100
        self.bar.grid(column=1, row=9)

        self.send_file = Button(self.window, text="Send File", command=self.send_file_tcp, height=1, width=7)
        self.send_file.grid(column=1, row=10)

        self.bar.start()
        for i in range(101):

            time.sleep(0.05)
            self.bar["value"] = i

            self.progress_bar_text = Label(self.window, text="Progress : " + str(i) + "%", font=("Arial Bold", 20))
            self.progress_bar_text.grid(column=1, row=8)

            self.bar.update()
            if self.bar["value"] == 100:
                self.if_downloaded()
            self.bar.stop()
            self.progress_bar_text.config(text="Progress : 0% ")

        self.bar["value"] = 0

        self.window.mainloop()


if __name__ == "__main__":
    print("Begin of Program")
    gui()
    print("End of Program")
