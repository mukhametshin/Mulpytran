#!/usr/bin/env python
# encoding=utf-8


#This script and included resources are licensed under GNU GPLv3 license
#Please read http://www.gnu.org/copyleft/gpl.html for more information
#
#Mulpytran is a small Python script to query word translations by the
#use of the Multitran.ru online dictionary


import sys

try:
    import requests
except:
    print "Requests Library Not Available"
    sys.exit(1)

try:
    from gi.repository import Gtk, WebKit
except:
    print "PyGObject and/or WebKit libraries not available"
    sys.exit(1)

class App:
    def __init__( self ):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('/usr/lib/Mulpytran/Mulpytran.glade')
        self.window = self.builder.get_object("windowMain")

        #Close the app by the x-button
        if self.window:
            self.window.connect("destroy", Gtk.main_quit)

        #Init of a scroll widget as a html renderer
        self.htm=WebKit.WebView()
        scroll=self.builder.get_object("scrolledWindow")
        scroll.add(self.htm)
        self.builder.get_object("boxTransl").pack_start(scroll, True, True, 0)

        #Define list of language for the query
        lang_store=["Eng","Ger","Esp","Fra","Ned","Ita","Lat","Est","Est<->Eng","Afr","Eng<->Ger","Esper","Kalm"]

        langBox=self.builder.get_object("langBox")
        #Init of the language selection ComboBoxText
        self.langComboBoxText=Gtk.ComboBoxText()
        self.langComboBoxText.set_name("langCombo")
        self.langComboBoxText.set_entry_text_column(0)
        for lang in lang_store:
            self.langComboBoxText.append_text(lang)
        langBox.pack_start(self.langComboBoxText, False, False, 0)
        self.langComboBoxText.set_active(0)

        #A dictionary with the signal handlers
        dic = {
        "on_windowMain_destroy" : self.quit,
        "on_menubutton_quit_button_press_event": self.menuitem_quit,
        "on_queryButton_clicked": self.mu_query,
        "on_gtk_about_activate": self.aboutDialog_open,
        "on_wordEntry_activate": self.mu_query
        }

        #Additional handlers
        self.langComboBoxText.connect("changed", self.on_langComboBoxText_changed)
        self.windowAbout = self.builder.get_object("aboutDialog")
        self.builder.connect_signals(dic)

        self.window.show_all()

    def main( self ):
        Gtk.main()

    def aboutDialog_open ( self, menuitem ):
        self.response = self.windowAbout.run()
        self.windowAbout.hide()

    def quit( self, widget ):
        Gtk.main_quit()

    def menuitem_quit( *args ):
        sys.exit(0)

    def on_langComboBoxText_changed( self, combo ):
        text=combo.get_active_text()
        if text != "":
            self.mu_query(self.builder.get_object("queryButton"))

    def parsing( self, tbl ):
    # This function parses the multitran page and returns the word definitions table
        matching_start='<table border="0" cellspacing="0" cellpadding="0"><tr><td bgcolor="#DBDBDB"'
        matching_end='</table><a name="phrases"></a>'
        flag=0
        parsed=[]
        for item in tbl.split("\n"):
            if (matching_start in item) or (flag==1):
                flag=1
                parsed.append(item)
                if matching_end in item:
                    return "<head></head><body>" + "\n".join(parsed) + "</body>"
                    break

    def mu_query( self, *args ):
    # This function requests a translation
    # of the word from the server http://www.multitran.ru
        word = self.builder.get_object("wordEntry").get_text()
        lang = self.langComboBoxText.get_active_text()
        if lang == "Eng":
            lang_code = "?l1=1&l2=2&s="
        elif lang == "Ger":
            lang_code = "?l1=3&CL=1&s="
        elif lang == "Esp":
            lang_code = "?l1=5CL=1&a=0&s="
        elif lang == "Fra":
            lang_code = "?l1=4&CL=1&a=0&s="
        elif lang == "Ned":
            lang_code = "?l1=24&CL=1&a=0&s="
        elif lang == "Ita":
            lang_code = "?l1=23&CL=1&a=0&s="
        elif lang == "Lat":
            lang_code = "?l1=27&CL=1&a=0&s="
        elif lang == "Est":
            lang_code = "?l1=26&CL=1&a=0&s="
        elif lang == "Est<->Eng":
            lang_code = "?l1=26&l2=1&CL=1&a=0&s="
        elif lang == "Afr":
            lang_code = "?l1=31&CL=1&a=0&s="
        elif lang == "Eng<->Ger":
            lang_code = "?l1=1&l2=3&CL=1&a=0&s="
        elif lang == "Esper":
            lang_code = "?l1=34&CL=1&a=0&s="
        elif lang == "Kalm":
            lang_code = "?l1=35&CL=1&a=0&s="
        #elif lang == "Jap":
        #    lang_code = "?l1=28&CL=1&a=0&s="

        link = 'http://89.108.112.70/c/m.exe' + str(lang_code) + str(word)
        r = requests.get(link)
        r.encoding = 'Windows-1251'
        if r.status_code == requests.codes.ok:
            if self.parsing(r.text) != None:
                    self.htm.load_html_string(self.parsing(r.text), "http://89.108.112.70")
                    #self.htm.load_string(self.parsing(r.text), "text/html", "utf-8", "file://")
            else:
                errorMessage="<head></head><body>Слово не найдено...</body>"
                self.htm.load_html_string(errorMessage, "file://")
        else:
            #self.builder.get_object("returnedText").get_buffer().set_text(str(r.status_code))
            errorMessage="<head></head><body>Ошибка соединения: " + str(r.status_code) + "</body>"
            self.htm.load_html_string(errorMessage, "file://")

if __name__ == "__main__":
    app = App()
    app.main()
