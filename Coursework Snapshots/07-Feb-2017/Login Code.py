# Make administrator_settings button (allow them to reset passwords and delete accounts)
# Forgot Password button --> send email to administrator --> make him reset password
# Change user_id generation (find last ID made rather than calculate through length of list
# for index in self.setstable.selectionModel()
import os
import time
import sys
import sqlite3 as lite
import hashlib
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from pygame import mixer
from PyQt4 import QtGui, uic, QtCore, QtSql
con = lite.connect('Music Library.db')
cur = con.cursor()
login_window = uic.loadUiType("Login UI.ui")[0]
createaccount_window = uic.loadUiType("Create Account.ui")[0]
main_window = uic.loadUiType("Media Player UI.ui")[0]
settings_window = uic.loadUiType("Settings.ui")[0]


class LoginWindowClass(QtGui.QMainWindow, login_window):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.uname = ""
        self.password = ""
        self.setupUi(self)
        self.btn_login.clicked.connect(self.login)
        self.btn_crtacc.clicked.connect(self.createaccount)

    def login(self):
        self.uname = self.txt_uname.text()  # draws variables from what is in the two line edit boxes
        self.password = hashlib.sha256(self.txt_pass.text().encode()).hexdigest()
        print(self.uname, self.password)
        cur.execute("SELECT COUNT(Username) FROM Users WHERE UserName = ?", (str(self.uname),))
        if cur.fetchone()[0] >= 0:
            cur.execute("SELECT UserPassword FROM Users WHERE UserName = ?", (str(self.uname),))
            if cur.fetchone()[0] == self.password:
                print("access granted")
                LoginWindow.hide()
                MainWindow.show()
            else:
                self.lbl_info.setText("Wrong Password")
        else:
            self.lbl_info.setText("Wrong Username")

    def createaccount(self):
        CreateWindow.show()


class CreateAccountWindowClass(QtGui.QMainWindow, createaccount_window):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.new_username = ""
        self.new_password = ""
        self.password_hash = 0
        self.users_id = 0
        self.admin = 0
        self.btn_crtacc.clicked.connect(self.create_account)

    def create_account(self):
        new_username = self.txt_username.text()
        new_password = self.txt_password.text()
        print(new_username, new_password)
        cur.execute("select COUNT(Username) FROM Users")
        self.users_id = (cur.fetchone()[0]) + 1
        cur.execute("select COUNT(UserName) from Users where UserName=?", (str(self.new_username),))
        username_validate = cur.fetchone()[0]
        if username_validate != 0:
            self.lbl_3.setText("Username is already in use")
        else:
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            print(password_hash)
            cur.execute("INSERT INTO Users VALUES(?,?,?,0)", (int(self.users_id), str(new_username),
                                                              str(password_hash)))
            con.commit()
            CreateWindow.hide()


class MainWindowClass(QtGui.QMainWindow, main_window):
    def __init__(self, parent=None):
        mixer.init()
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.data = []
        self.model = QtGui.QStandardItemModel(self)
        self.tbl_songs.setModel(self.model)
        self.btn_settings.clicked.connect(self.settings)  # settings button programmed
        self.btn_albums.clicked.connect(self.albums)
        self.btn_songs.clicked.connect(self.songs)
        self.btn_artists.clicked.connect(self.artists)
        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)

    def settings(self):
        SettingsWindow.show()

    def songs(self):
        s = "SELECT * FROM Songs"
        cur.execute(s)
        self.data = cur.fetchall()
        self.load_data()
        self.tbl_songs.doubleClicked.connect(self.play_song)

    def albums(self):
        s = "SELECT * FROM Albums"
        cur.execute(s)
        self.data = cur.fetchall()
        self.load_data()
        self.tbl_songs.doubleClicked.connect(self.albums_to_songs)

    def artists(self):
        s = "SELECT * FROM Artists"
        cur.execute(s)
        self.data = cur.fetchall()
        self.load_data()
        self.tbl_songs.doubleClicked.connect(self.artists_to_albums())

    def artists_to_albums(self):
        #self.tbl_songs.doubleClicked.disconnect()
        self.retrieve_row()
        artist_id = row_details[0]
        cur.execute("SELECT * FROM Albums WHERE ArtistID=?", (str(artist_id)), )
        self.data = cur.fetchall()
        self.load_data()
        self.tbl_songs.doubleClicked.connect(self.albums_to_songs())

    def albums_to_songs(self):
        self.retrieve_row()
        album_id = row_details[0]
        cur.execute("SELECT * FROM Songs WHERE AlbumID=?", (str(album_id),))
        self.data = cur.fetchall()
        self.load_data()
        self.tbl_songs.doubleClicked.connect(self.play_song)

    def play_song(self):
        self.tbl_songs.doubleClicked.disconnect()
        self.retrieve_row()
        print(row_details)
        print(row_details)
        location = row_details[5]
        print(location)
        song_id = row_details[0]
        plays = row_details[8] + 1
        cur.execute("UPDATE Songs SET Plays=? WHERE SongID=?", (int(plays), int(song_id)))
        con.commit()
        mixer.music.load(location)
        mixer.music.play()

    def retrieve_row(self):
        global row_details
        for index in self.tbl_songs.selectionModel().selectedRows():
            row = index.row()
            print(row)
            row_details = self.data[row]

    def play(self):
        mixer.music.unpause()

    def pause(self):
        mixer.music.pause()

    def load_data(self):
        if len(self.data) > 0:
            for i in range(len(self.data) - 1, -1):
                print("removing row", i)
                self.data.pop(i)
                self.model.removeRow(index.row(self.data[i]))
        self.model = QtGui.QStandardItemModel(self)
        self.tbl_songs.setModel(self.model)
        for row in self.data:
            items = [QtGui.QStandardItem(str(field)) for field in row]
            self.model.appendRow(items)


class SettingsWindowClass(QtGui.QMainWindow, settings_window):
        def __init__(self, parent=None):
            QtGui.QMainWindow.__init__(self, parent)
            self.setupUi(self)
            self.btn_import.clicked.connect(self.importing)  # settings button pressed
            self.btn_logout.clicked.connect(self.logout)
            self.btn_exit.clicked.connect(self.exit)

        def importing(self):
            cur.execute("DELETE FROM Albums")
            cur.execute("DELETE FROM Artists")
            cur.execute("DELETE FROM SONGS")  # resets database
            print("scanning")
            counter = 1  # counter used to calculate song_id
            rawdirectory = self.txt_dir.text()  # sets directory specified from user for their music library
            for dirName, subdirList, filelist in os.walk(rawdirectory):  # starts to walk through library
                for fname in filelist:  # scans filename in directory
                    if fname[-3:] == 'mp3':  # validation for .mp3
                        song_location = str(dirName + '\\' + fname)  # forms file location from previous information
                        print(song_location)
                        song = EasyID3(song_location)  # retrieves tags from file
                        length_info = length = MP3(song_location)
                        length = length_info.info.length
                        artist_name = (song["artist"][0])  # sets artist tag to variable
                        album_name = (song["album"][0])  # sets album tag to variable
                        cur.execute("SELECT COUNT(ArtistName) FROM Artists where ArtistName= ?", (str(artist_name),))
                        # checks if artist name already exists
                        artist_validate = cur.fetchone()[0]  # fetches result from sql query in previous line
                        if artist_validate == 0:  # If artist name doesn't exist in artists table
                            cur.execute("select COUNT(ArtistName) FROM Artists")
                            # finds length of artists list, used to create artist_id
                            artists_length = cur.fetchone()[0]  # fetches result from sql query in previous line
                            artist_id = artists_length + 1  # creates artist_id for new artist
                            cur.execute("INSERT INTO Artists VALUES(?,?)", (int(artist_id), str(artist_name)))
                            # submits artist_id to new table
                            con.commit()  # commits sql query in previous line
                        else:  # if the artist is already in the table...
                            cur.execute("select ArtistID from Artists where ArtistName= ?", (str(artist_name),))
                            # retrieve artist_id of specific artist
                            artist_id = cur.fetchone()[0]  # fetches result from sql query on previous line
                        cur.execute("SELECT COUNT(AlbumName) FROM Albums WHERE AlbumName = ?", (str(album_name),))
                        # checks if album name already exists
                        album_validate = cur.fetchone()[0]  # fetches result from sql query in previous line
                        if album_validate == 0:  # If album name doesn't exist in album table
                            cur.execute("SELECT COUNT(AlbumName) FROM Albums")
                            # finds the length of Albums table, used to calculate album_id
                            albums_length = cur.fetchone()[0]  # fetches result from sql query on previous line
                            album_id = albums_length + 1  # calculates album_id
                            cur.execute("INSERT INTO Albums VALUES(?,?,?)", (int(album_id), str(album_name),
                                                                             int(artist_id)))
                            # adds collected data to table
                            con.commit()  # commits sql statement on previous line
                        else:  # if the album name already exists in Albums table
                            cur.execute("select AlbumID from Albums where AlbumName=?", (str(album_name),))
                            # retrieves album_id
                            album_id = cur.fetchone()[0]  # fetches result from sql statement on previous line
                        genre = (song["genre"][0])  # sets genre tag to variable
                        song_id = int(counter)  # forms song_id from counting the mp3 files
                        song_name = (song["title"][0])  # sets the song title tag to variable
                        track_number = (song["tracknumber"][0])  # sets track number tag to variable
                        cur.execute("INSERT INTO Songs VALUES(?,?,?,0,?,?,?,?,0)", (int(song_id), str(song_name),
                                                                                str(track_number), str(genre),
                                                                                str(song_location), int(album_id), int(length)))
                        # appends data to table
                        counter += 1  # increments counter for next song
            print("Complete")  # once all files have been added, 'Complete is printed'

        def logout(self):
            MainWindow.hide()
            SettingsWindow.hide()
            LoginWindow.show()

        def exit(self):
            SettingsWindow.hide()

app = QtGui.QApplication(sys.argv)
LoginWindow = LoginWindowClass(None)
MainWindow = MainWindowClass(None)
SettingsWindow = SettingsWindowClass(None)
CreateWindow = CreateAccountWindowClass(None)
LoginWindow.show()
app.setWindowIcon(QtGui.QIcon('paomedia_small_n_flat_disc_vinyl__1_-0.png'))
app.exec_()
