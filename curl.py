#!/usr/bin/env python2.7

#import Tkinker as Tk


from Tkinter import *
from tkFileDialog import *
from UserString import MutableString
from ttk import *
from subprocess import call

class App:
    def __init__(self, master):
        master.title("cURL Wrapper")

        frame = Frame(master)
        self.frame = frame
        self.frame.config(pad=10)
        self.frame.pack()
        self.frame.focus_set()

        self.url_lbl = Label(frame, text="URL")
        self.url = self.lookupList('url.values', ("http://server.host.com/"))
        self.url.config(width=72)
        
        self.account = Frame(self.frame)
        self.account.pack()
        self.user_lbl = Label(self.account, text="User Name")
        self.user = Entry(self.account)
        self.user.config(width=8)
        self.passwd_lbl = Label(self.account, text="Password")
        self.passwd = Entry(self.account, text="Password", show="*")
        self.passwd.config(width=14)

        self.head_lbl = Label(frame, text="HTTP Headers")
        self.head_name_lbl = Label(frame, text="Name")
        self.head_name = Combobox(frame)

        def_list = ("Accept", "Content-Type")
        self.head_name = self.lookupList("head.names", def_list)

        self.head_value_lbl = Label(frame, text="Value")

        def_list = ("application/xml","text/plain","application/json","application/pdf")
        self.head_value = self.lookupList('head.values', def_list)

        self.head_add = Button(frame,text="Add Header",command=self.addHeader)
        self.headers = Listbox(frame,width=50,selectmode=MULTIPLE)
        self.headers_rm = Button(frame, text="Remove", command=self.rmHeader)

        self.param_lbl = Label(frame, text="Parameters")
        self.param_name_lbl = Label(frame, text="Name")
        self.param_name = Entry(frame)
        self.param_name.insert(0,"param_name")
        self.param_value_lbl = Label(frame, text="Value")
        self.param_value = Entry(frame)
        self.param_value.insert(0,"param_value")
        self.param_addParam = Button(frame, text="Add Param", command=self.addParam)
        self.param_addFile = Button(frame, text="Add File", command=self.pickParamFile)

        self.cmd = Text(frame, height=10, width=90)
        self.run = Button(frame,text="Run",command=self.doRun,name="doRun")
        self.quit = Button(frame,text="Quit",command=frame.quit,name="quit")

        '''
Layout Phase:

markdown table of the grid layout. spans between -> and <-

|    | 0               | 1              | 2        | 3               | 4  | 5  |
| -- | --------------- | -------------- | -------- | --------------- | -- | -- |
| 00 | url_lbl         | url -> 3       | -        | <-              |    |    |
| 01 | user_lbl        | user -> 2      | <-       | passwd_lbl      | pw | <- |
| 02 | head_lbl->3     | -              | <-       | headers->3 -y 7 | -  | <- |
| 03 | Head_name_lbl   | Head_name->2   | <-       | _               | -  | -  |
| 04 | head_value      | head_value->2  | <-       | _               | -  | -  |
| 05 | head_add->3     | -              | <-       | _               | -  | -  |
| 06 | param_lbl       | -              | <-       | _               | -  | -  |
| 07 | param_name_lbl  | param_name->2  | <-       | _               | -  | -  |
| 08 | param_value_lbl | param_value->2 | <-       | ^-              | -  | -  |
| 09 |                 | addFile        | addParam | remove->3       | -  | <- |
| 10 | cmd->6          | -              | -        | -               | -  | <- |
| 11 |                 |                | run      | quit            |    |    |
        
        '''

        self.url_lbl.grid(row=0,sticky=W)
        self.url.grid(row=0,column=1,columnspan=3,sticky=E)
        
        self.account.grid(row=1,columnspan=6,sticky=W)
        self.user_lbl.grid(row=0)
        self.user.grid(row=0,column=1)
        self.passwd_lbl.grid(row=0,column=2)
        self.passwd.grid(row=0,column=3)

        self.head_lbl.grid(row=2,columnspan=3)
        self.head_name_lbl.grid(row=3)
        self.head_name.grid(row=3,column=1,columnspan=2)
        self.head_value_lbl.grid(row=4)
        self.head_value.grid(row=4,column=1,columnspan=2)
        self.head_add.grid(row=5,columnspan=3)

        self.param_lbl.grid(row=6,columnspan=3)
        self.param_name_lbl.grid(row=7)
        self.param_name.grid(row=7,column=1,columnspan=2)
        self.param_value_lbl.grid(row=8)
        self.param_value.grid(row=8,column=1,columnspan=2)
        self.param_addFile.grid(row=9, column=1)
        self.param_addParam.grid(row=9, column=2)

        self.headers.grid(row=2,column=3,columnspan=2,rowspan=7)
        self.headers_rm.grid(row=9,column=3)
        
        self.cmd.grid(row=10,columnspan=6)
        self.run.grid(row=11,column=2)
        self.quit.grid(row=11,column=3)
        
        self.command = []

    def updateCmd(self):
        out = MutableString()
        
        command = ["curl","-s","-X","POST","--user-agent","Post_Maker_thing"]
                
        template = "curl \\\n\t-s -X POST \\\n\t--user-agent 'Post_Maker_thing' \\\n\t%s%s"
        list = self.headers.get(0, self.headers.size())
        for item in list:
            hh = item.find("HH: ")
            pp = item.find("PP: ")
            pf = item.find("PF: ")
            if hh==0:
                parts = item[3:].split("=")
                head = "-H '%s: %s'" % (trim(parts[0]), trim(parts[1]))
                out += "%s \\\n\t" % head
                command.append("-H")
                command.append("%s: %s" % (trim(parts[0]), trim(parts[1])) )
            elif pp==0:
                parts = item[3:].split("=")
                param = "--data-urlencode %s" % (item[3:])
                out += "%s \\\n\t" % param
                command.append("--data-urlencode")
                command.append("%s=%s" % (trim(parts[0]), trim(parts[1])) )
            elif pf==0:
                parts = item[3:].split("=")
                param = "--data-urlencode %s@%s" % (trim(parts[0]), trim(parts[1]))
                out += "%s \\\n\t" % param
                command.append("--data-urlencode")
                command.append("%s@%s" % (trim(parts[0]), trim(parts[1])) )

        c = template % (out, self.url.get())
        command.append(self.url.get().rstrip())

        self.cmd.delete(1.0, END)
        self.cmd.insert(INSERT,c)
        self.command = command

    def addHeader(self):
        name = self.head_name.get()
        value = self.head_value.get()
        self.headers.insert(END, "HH: %s=%s" % (name, value))
        self.updateCmd()

    def addParam(self):
        name = self.param_name.get()
        value = self.param_value.get()
        self.headers.insert(END, "PP: %s=%s" % (name, value))
        self.updateCmd()

    def pickParamFile(self):
        name = self.param_name.get()
        value = askopenfilename()
        self.headers.insert(END, "PF: %s=%s" % (name, value))
        self.updateCmd()

    def doRun(self):
        
        #print self.user.get()
        #print self.passwd.get()
        
        if (0<len(self.user.get()) and 0<len(self.passwd.get())):
            self.command.insert(1, "-u")
            self.command.insert(2, "%s:%s" % (self.user.get(), self.passwd.get()) )
            #print "'%s:%s'" % (self.user.get(), self.passwd.get())


        #file = asksaveasfilename(title="Save output",parent=self.frame)
        #if file == "": return
        #self.command.append(">")
        #self.command.append(file)
        
        #print self.command
        call (self.command)
    
    def rmHeader(self):
        for i in  reversed(self.headers.curselection()): self.headers.delete(i)
        self.updateCmd()

    def lookupList(self, name, def_list):
        try:
            file = open(name, 'r')
            list = file.readlines()
            file.close()
        except IOError:
            list = def_list

        cbox = Combobox(self.frame)
        cbox['values'] = list
        cbox.current(0)

        return cbox

    def save(self):
        urls = list(self.url['values'])
        head_names = list(self.head_name['values'])
        head_values = list(self.head_value['values'])

        if self.url.get() not in urls:
            urls.append(self.url.get())
            urls.sort()
            self.writeLines("url.values", urls)

        if self.head_name.get() not in head_names:
            head_names.append(self.head_name.get())
            head_names.sort()
            self.writeLines("head.names", head_names)

        if self.head_value.get() not in head_values:
            head_values.append(self.head_value.get())
            head_values.sort()
            self.writeLines("head.values", head_values)

    def writeLines(self, name, lines):
        try:
            with open(name, "w+") as file:
                for line in lines:
                    file.write(line + "\n")
                file.close
        except IOError:
            print ("could not write file" + name)

def trim(str):
    str = str.lstrip()
    str = str.rstrip()
    return str

def main():
    root = Tk()
    app = App(root)
    root.mainloop()
    app.save()
    root.destroy()

if __name__ == "__main__": main()
