import socket
import threading
from customtkinter import *
import tkinter
from tkinter.messagebox import showerror, showinfo
from pygame import mixer


mixer.init()
ding = mixer.Sound("ding.wav")



def clear_frame(root_frame):
    root_frame.destroy()


class Client: # handles all client related info.
    def __init__(self, host, port, username, app, current_frame):
        self.username = username
        self.chat_label = None
        self.app = app
        clear_frame(current_frame)
        self.chat = CTkFrame(app)
        self.chat.pack(pady=20, padx=60, fill="both", expand=True)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
        except Exception:
            showerror("Faulty Server",
                      "The server you are trying to connect is either down or is unable to establish a connection.")
            clear_frame(self.chat)
            input_server_info()

        self.gui_done = False
        self.running = True
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.scrollbar = CTkScrollbar(self.chat)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.chat_label = CTkLabel(self.chat, text=self.username)
        self.chat_label.configure(font=("Tahoma", 30))
        self.chat_label.pack(padx=20, pady=5)
        self.text_area = CTkTextbox(self.chat, font=("Tahoma", 30))
        self.text_area.pack(fill="both", expand=True)
        self.text_area.configure(state="disabled")
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.text_area.yview)
        self.msg_label = CTkLabel(self.chat, text="Message: ", font=("Tahoma", 30))
        self.msg_label.pack(padx=20, pady=10)
        self.input_area = CTkTextbox(self.chat, height=40, font=("Tahoma", 25))
        self.input_area.pack(padx=20, pady=10, fill="both")
        self.send_btn = CTkButton(self.chat, text="Send", command=lambda: self.write(code="press"), font=("Tahoma", 30))
        self.send_btn.pack(padx=20, pady=10)
        self.disconnect = CTkButton(self.chat, text="Disconnect",
                                    command=lambda: [self.sock.close(), clear_frame(self.chat),
                                                     showinfo("Disconnected", "You have disconnected from the server."),
                                                     input_server_info()],
                                    font=("Tahoma", 15))
        self.disconnect.place(x=0, y=0)

        def switch_event():
            if str(switch_var.get()) == "on":
                set_appearance_mode("light")
            else:
                set_appearance_mode("dark")

        switch_var = StringVar(value="off")
        switch = CTkSwitch(self.chat, text="Dark/Light Mode", command=switch_event, variable=switch_var, onvalue="on",
                           offvalue="off").pack(pady=0, padx=0)

        self.gui_done = True
        self.app.protocol("WM_DELETE_WINDOW", self.stop)
        self.app.bind("<Return>", func=lambda event: self.write(code="enter"))
        set_appearance_mode("dark")

    def write(self, code):
        if code == "enter":
            message = f"{self.username}: {self.input_area.get('1.0', 'end')}"
        else:
            message = f"{self.username}: {self.input_area.get('1.0', 'end')}  \n"
        self.sock.send(message.encode("utf-8"))
        self.input_area.delete('1.0', 'end')

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode("utf-8")
                ding.play()
                if message == "NICK":
                    self.sock.send(self.username.encode("utf-8"))

                else:
                    if self.gui_done:
                        self.text_area.configure(state="normal")
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.configure(state="disabled")
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                clear_frame(self.chat)
                showinfo("Disconnected", "You have been disconnected from the server.")
                input_server_info()
                break

    def stop(self):
        #terminates program
        self.running = False
        self.app.destroy()
        self.sock.close()
        exit()


def input_server_info():
    clear_frame(frame)
    create = CTkFrame(root)
    create.pack(pady=20, padx=60, fill="both", expand=True)
    root.unbind_all("<Return>")

    def username_has_space(users_username):
        try:
            if len(users_username.split(" ")) >= 2:
                return True
            else:
                return False

        except Exception as exc:
            print(exc)
            return False

    def connect(user_username, host, port): #connects users
        client = Client(host=host, port=port, username=user_username, app=root, current_frame=create)

    def join(user_name, server, port):
        #does a bit of handling
        try:
            if not username_has_space(str(user_name)):
                connect(str(user_name), str(server), int(port))
            elif username_has_space(str(user_name)):
                showerror("Faulty Username", "You can not use spaces in your username! Try again")
            else:
                print("This is an error")
        except Exception as ex:
            # showerror("Wrong Info", "Something went wrong. Please try again. Hint(s): Is your port a number?")
            print(ex)

    CTkLabel(create, text="Join Chat", font=("Tahoma", 40)).pack(pady=80)
    name = CTkEntry(master=create,
                    placeholder_text="Username", height=60, width=450, font=("Tahoma", 20))
    name.pack(pady=12, padx=10)
    username = CTkEntry(master=create,
                        placeholder_text="Server IP Address", height=60, width=450, font=("Tahoma", 20))
    username.pack(pady=12, padx=10)
    password = CTkEntry(master=create,
                        placeholder_text="Server Port", height=60, width=450, font=("Tahoma", 20))
    password.pack(pady=12, padx=10)
    button = CTkButton(master=create,
                       command=lambda: join(name.get(), username.get(), password.get()),
                       text='Join Chat', height=60, width=160, font=("Tahoma", 25))
    button.pack(pady=12, padx=10)
    
    # Switch event to control dark or light mode.
    def switch_event():
        if str(switch_var.get()) == "on":
            set_appearance_mode("light")
        else:
            set_appearance_mode("dark")

    switch_var = StringVar(value="off")
    switch = CTkSwitch(create, text="Dark/Light Mode", command=switch_event, variable=switch_var, onvalue="on",
                       offvalue="off").pack(pady=40, padx=0)


if __name__ == "__main__":
    #creating main window and setting things up.
    root = CTk()
    root.geometry("700x780")
    root.title("Pycord")
    root.iconbitmap("logo.ico")
    set_appearance_mode("dark")
    set_default_color_theme("green")
    frame = CTkFrame(root)
    input_server_info()
    # me = Client("localhost", 9090, "test_user", root, frame)
    root.mainloop()
