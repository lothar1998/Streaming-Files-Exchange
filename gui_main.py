import time
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
from Client import Client as client
from Client import multicast_search
import math
import os
import socket



class gui():
    def fileDialog(self):
        self.file_path = filedialog.askopenfilename(initialdir="/home", title="Select file", filetypes=(
            ("txt files", "*.txt"), ("jpeg files", "*.jpg"), ("all files", "*.*")))
        print(self.file_path)
        self.file_path_label = Label(self.window, text="file_path", font=("Arial Bold", 10))
        self.file_path_label.grid(column=0, row=10)
        self.empty_lbl_5 = Label(self.window, text=self.file_path, font=("Arial Bold", 10))
        self.empty_lbl_5.grid(column=1, row=10)

    def if_downloaded(self, file_name):
        self.ip_button_connect.config(state=DISABLED)
        self.browser_button_file.config(state=NORMAL)
        self.send_file.config(state=NORMAL)
        self.stop_sending.config(state=DISABLED)
        self.txt_destinaiton.config(state=NORMAL)
        if self.client_module.recv_interrupted:
            messagebox.showinfo("Download Info", "Downloading file: " + file_name + " was stopped!")
        else:
            messagebox.showinfo("Download Info", "The file has been downloaded! \nPath: " + str(os.getcwd() + "/" +
                                                                                                file_name))

    def if_start_downloading(self, file_name):
        self.ip_button_connect.config(state=DISABLED)
        self.browser_button_file.config(state=DISABLED)
        self.send_file.config(state=DISABLED)
        self.stop_sending.config(state=DISABLED)
        self.txt_destinaiton.config(state=DISABLED)
        messagebox.showinfo("Download Info", "File: " + file_name + " is currently downloading")

    def if_wrong_key(self):
        self.ip_button_connect.config(state=DISABLED)
        self.browser_button_file.config(state=NORMAL)
        self.send_file.config(state=NORMAL)
        self.stop_sending.config(state=DISABLED)
        self.txt_destinaiton.config(state=NORMAL)
        messagebox.showinfo("Send Info",
                            "Your destination key does not exist!")

    def adding_server_ip(self):
        if not self.socket_error:
            if self.server_IP is not None:
                self.client_module.close_connection()

        if self.server_address_input.get() == '':
            print(f"from function multicast: {multicast_search()}")
            ip_addr = multicast_search()
            if ip_addr is None:
                messagebox.showinfo("Multicast server", f"Cannot reach server with multicast")
                return
            else:
                self.server_IP = ip_addr
                self.server_address_input.delete(0, END)
                self.server_address_input.insert(0, self.server_IP)
        else:
            self.server_IP = self.server_address_input.get()

        self.client_module = client(self.server_IP, 6969, self.if_downloaded, self.if_start_downloading, self.if_wrong_key)
        try:
            self.client_module.initiate_connection()
            self.get_my_id()

            messagebox.showinfo("Server IP", f"The server has been connected!")
            self.socket_error = False
            self.ip_button_connect.config(state=DISABLED)
            self.server_address_input.config(state=DISABLED)
        except socket.error:
            messagebox.showinfo("Server IP", "Connection refused!")
            self.socket_error = True


    def get_my_id(self):
        self.my_ID = self.client_module.client_id

        self.my_id_label = Label(self.window, text=self.my_ID, font=("Arial Bold", 20), borderwidth=2, relief="sunken")
        self.my_id_label.grid(column=1, row=4)

    def close_window(self):
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.window.destroy()
            print("Window closed")
            if not self.socket_error:
                if self.server_IP is not None:
                    self.client_module.close_connection()
            self.window.quit()

    def add_destination_id(self):
        return self.txt_destinaiton.get()  # on add button processed

    def stop_sending(self):
        self.client_module.sending_interrupted = True
        self.progress_bar_text.config(text="Progress : " + str(0) + " %")  # TODO does not work updating progress bar
        self.bar["value"] = 0  # TODO does not work updating progress bar
        self.bar.update()  # TODO does not work updating progress bar
        self.ip_button_connect.config(state=NORMAL)
        self.browser_button_file.config(state=NORMAL)
        self.send_file.config(state=NORMAL)
        self.stop_sending.config(state=DISABLED)


    def send_file_tcp(self):
        destination_id = self.add_destination_id()
        self.client_module.send_file(self.file_path, destination_id)
        self.ip_button_connect.config(state=DISABLED)
        self.browser_button_file.config(state=DISABLED)
        self.send_file.config(state=DISABLED)
        self.stop_sending.config(state=NORMAL)
        current_progress = 0
        while True:
            current_progress = math.floor(self.client_module.current_progress * 100)
            time.sleep(0.05)
            self.progress_bar_text.config(text="Progress : " + str(current_progress) + " %")
            self.bar["value"] = current_progress
            self.bar.update()

            if current_progress == 100:
                self.ip_button_connect.config(state=NORMAL)
                self.browser_button_file.config(state=NORMAL)
                self.send_file.config(state=NORMAL)
                self.stop_sending.config(state=DISABLED)
                break

    def __init__(self):
        self.socket_error = False
        self.client_module = None
        self.my_ID = None

        self.server_IP = None

        self.window = Tk()
        self.window.title('Kugburkalimetr')
        self.window.geometry('610x400+700+500')
        self.window.minsize(610, 450)
        self.window.maxsize(610, 450)
        self.downloaded_file_path = ''

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

        self.empty_lbl_5 = Label(self.window, text="", justify=CENTER, font=("Arial Bold", 20))
        self.empty_lbl_5.grid(column=0, row=10)

        self.send_file = Button(self.window, text="Send File", command=self.send_file_tcp, height=1, width=7)
        self.send_file.grid(column=1, row=11)

        self.stop_sending = Button(self.window, state=DISABLED,text="Stop Sending", command=self.stop_sending, height=1, width=9)
        self.stop_sending .grid(column=0, row=11)

        self.bar.start()
        # for i in range(101):

        i = 0

        self.bar["value"] = i

        self.progress_bar_text = Label(self.window, text="Progress : " + str(i) + "%", font=("Arial Bold", 20))
        self.progress_bar_text.grid(column=1, row=8)


        if self.bar["value"] == 100:
            self.if_downloaded()
        self.bar.stop()


        self.window.mainloop()


if __name__ == "__main__":
    print("Begin of Program")
    gui()
    print("End of Program")
