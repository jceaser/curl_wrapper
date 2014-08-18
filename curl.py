#!/usr/bin/env python2.7

#import Tkinker as Tk


from Tkinter import *
from tkFileDialog import *
from UserString import MutableString
from ttk import *
from subprocess import call

'''

application/xml
text/plain
application/json
application/pdf

/opt/local/bin/curl \
    -X POST \
    --user-agent "GCMD-Client" \
    -H "Accept: application/xml"
    --data-urlencode record@./src/test/resources/dif.xml \
        http://<host_name>.gsfc.nasa.gov/qatool/results?rules=gcmd-0.1
'''


class App:
    def __init__(self, master):
        master.title("cURL wrapper")

        frame = Frame(master)
        self.frame = frame
        self.frame.config(pad=10)
        self.frame.pack()
        self.frame.focus_set()

        self.url_label = Label(frame, text="URL")
        #self.url = Entry(frame,width=72)
        self.url = self.lookupList('url.values', ("http://server.host.com/"))
        self.url.config(width=72)

        self.head_lbl = Label(frame, text="HTTP Headers")
        self.head_name_lbl = Label(frame, text="Name")
        self.head_name = Combobox(frame)

        def_list = ("Accept", "Content-Type")
        self.head_name = self.lookupList("head.names", def_list)

        self.head_value_lbl = Label(frame, text="Value")

        def_list = ("application/xml","text/plain","application/json","application/pdf")
        self.head_value = self.lookupList('head.values', def_list)

        self.head_add = Button(frame,text="Add Header",command=self.addHeader)
        self.headers = Listbox(frame,width=50)

        self.param_lbl = Label(frame, text="Parameters")
        self.param_name_lbl = Label(frame, text="Name")
        self.param_name = Entry(frame)
        self.param_name.insert(0,"param_name")
        self.param_value_lbl = Label(frame, text="Value")
        self.param_value = Entry(frame)
        self.param_value.insert(0,"param_value")
        self.param_addParam = Button(frame, text="Add Param", command=self.addParam)
        self.param_addFile = Button(frame, text="Add File", command=self.pickParamFile)

        self.cmd = Text(frame, height=10, width=80)
        self.run = Button(frame,text="Run",command=self.doRun,name="doRun")
        self.quit = Button(frame,text="Quit",command=frame.quit,name="quit")

        self.url_label.grid(row=0,sticky=W)
        self.url.grid(row=0,column=1,columnspan=3,sticky=E)

        self.head_lbl.grid(row=1,columnspan=3)
        self.head_name_lbl.grid(row=2)
        self.head_name.grid(row=2,column=1,columnspan=2)
        self.head_value_lbl.grid(row=3)
        self.head_value.grid(row=3,column=1,columnspan=2)
        self.head_add.grid(row=4,columnspan=3)

        self.param_lbl.grid(row=5,columnspan=3)
        self.param_name_lbl.grid(row=6)
        self.param_name.grid(row=6,column=1,columnspan=2)
        self.param_value_lbl.grid(row=7)
        self.param_value.grid(row=7,column=1,columnspan=2)
        self.param_addFile.grid(row=8, column=1)
        self.param_addParam.grid(row=8, column=2)

        self.headers.grid(row=1,column=3,columnspan=2,rowspan=8)
        self.cmd.grid(row=9,columnspan=4)
        self.run.grid(row=10,column=2,columnspan=1)
        self.quit.grid(row=10,column=3,columnspan=1)

    def updateCmd(self):
        out = MutableString()
        template = "curl \\\n\t-s -X POST \\\n\t--user-agent 'Post Maker thing' \\\n\t%s%s"
        list = self.headers.get(0, self.headers.size())
        for item in list:
            hh = item.find("HH: ")
            pp = item.find("PP: ")
            pf = item.find("PF: ")
            if hh==0:
                parts = item[3:].split("=")
                out += " -H '%s: %s' \\\n\t" % (parts[0], parts[1])
            elif pp==0:
                parts = item[3:].split("=")
                out += " --data-urlencode %s \\\n\t" % (item[3:])
            elif pf==0:
                parts = item[3:].split("=")
                out += " --data-urlencode %s@%s \\\n\t" % (parts[0], parts[1])

        c = template % (out, self.url.get())

        self.cmd.delete(1.0, END)
        self.cmd.insert(INSERT,c)

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
        cmd = self.cmd.get(0.0, END)
        call (cmd)

    def lookupList(self, name, def_list):
        try:
            file = open(name, 'r')
            list = file.readlines()
            file.close()
        except IOError:
            list = def_list

        cbox = Combobox(self.frame)
        cbox['values'] = list
        #cbox['data'] = list
        cbox.current(0)

        return cbox

    def save(self):
        urls = list(self.url['values'])
        #urls.append(self.url.get())

        head_names = self.head_name['values']
        #head_names.append(self.head_name.get())

        head_values = self.head_value['values']
        #head_values.append(self.head_value.get())

        if self.url.get() not in urls:
            urls.append(self.url.get())
            urls.sort()
            self.writeLines("url.values", urls)

        if self.head_name.get() not in head_names
            head_names.append(self.head_name.get())
            head_names.sort()
            self.writeLines("head.names", urls)

        if self.head_value.get() not in head_values
            head_values.append(self.head_value.get())
            head_values.sort()
            self.writeLines("head.values", urls)

        #print head_names
        #print head_values


    def writeLines(self, name, lines):
        try:
            with open(name, "w+") as file:
                for line in lines:
                    file.write(line + "\n")
                file.close
        except IOError:
            print ("could not write file" + name)


root = Tk()
app = App(root)
root.mainloop()
app.save()
root.destroy()

