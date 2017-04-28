# Forgot Password button --> send email to administrator --> make him reset password
import os  # os library imported, used for directory scanning and to exit the program
import sys  # sys library imported, used to create the application alongside PyQt
import sqlite3 as lite  # sqlite3 library imported, used for database access
import hashlib  # hashlib library imported, used for hashing passwords.
import re # re library imported, used for regex during registration
from mutagen.easyid3 import EasyID3  # EasyID3 library imported from mutagen library,
# used to read the ID3 tags in mp3 files
from mutagen.mp3 import MP3  # MP3 library imported from mutagen library, used to find the length of songs
from pygame import mixer  # mixer library imported from pygame, used for music playback
from PyQt4 import QtGui, uic, QtCore  # QtGui, uic and QtCore libraries imported from PyQt library.
# Used for user interface and application creation
con = lite.connect('Music Library.db')  # Connection to database established
cur = con.cursor()  # Cursor created for database management
ui_loginWindow = uic.loadUiType("Login UI.ui")[0]  # Login Window loaded in
ui_createAccountWindow = uic.loadUiType("Create Account.ui")[0]  # Create Account Window loaded in
ui_mainWindow = uic.loadUiType("Media Player UI.ui")[0]  # Main Window loaded in
ui_settingsWindow = uic.loadUiType("Settings.ui")[0]  # Settings Window loaded in
ui_playlistWindow = uic.loadUiType("Playlist Manager.ui")[0]  # Playlist Window loaded in
ui_playlistDialog = uic.loadUiType("Playlist Name.ui")[0]  # Playlist Name Dialog Box loaded in

class LoginWindowClass(QtGui.QMainWindow, ui_loginWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.int_userID = 0
        self.int_admin = 0
        self.setupUi(self)
        self.btn_login.clicked.connect(self.login)
        self.txt_pass.returnPressed.connect(self.login)
        self.btn_crtacc.clicked.connect(self.createaccount)

    def login(self):
        str_username = self.txt_uname.text()  # draws variables from what is in the two line edit boxes
        str_password = self.txt_pass.text()
        str_passwordhash = hashlib.sha256(str_password.encode()).hexdigest()  # hashhes user's inputted password
        print(str_username, str_password)  # prints users inputs
        cur.execute("SELECT COUNT(Username) FROM Users WHERE UserName = ?", (str(str_username),))  # checks to see if
        # username is in the database
        if str_username == "" or str_password == "":  # Validates user's inputs to make sure that no fields
            # have been left empty
            self.lbl_info.setText("Field(s) Empty")  # Notifies user if any fields are empty
        elif cur.fetchone()[0] >= 0:  # Validates to see if username was found in database. Else, a message is displayed
            cur.execute("SELECT UserPassword FROM Users WHERE UserName = ?", (str(str_username),))  # retrieves password
            # belonging to username from database
            if cur.fetchone()[0] == str_passwordhash:  # validate user's password against password in database
                cur.execute("select UserID from Users where UserName=?", (str(str_username),)) # retrieves user's ID
                self.int_userID = int(cur.fetchone()[0]) # assigns user's ID to a variable
                cur.execute("SELECT Administrator FROM Users WHERE UserID = ?", (int(self.int_userID),))
                # retrieves user's administrator permissions from db
                self.int_admin = cur.fetchall()[0][0] # assigns user's admin. permissions to a variable
                print(self.int_userID)  # prints user's ID
                print(self.int_admin)  # prints user's admin. permissions
                LoginWindow.hide()  # closes login window
                MainWindow.showFullScreen()  # opens media player screen
            else:
                self.lbl_info.setText("Wrong Password")  # message displayed if password validation fails
        else:
            self.lbl_info.setText("Wrong Username")  # message displayed if username validation fails

    def createaccount(self):
        CreateWindow.show()


class CreateAccountWindowClass(QtGui.QMainWindow, ui_createAccountWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.admin = 0
        self.btn_crtacc.clicked.connect(self.create_account)

    def create_account(self):
        str_newusername = self.txt_username.text()  # retrieves user's input from textbox
        str_newpassword = self.txt_password.text()  # retrieves user's input from textbox

        print(str_newusername, str_newpassword)
        cur.execute("SELECT UserID FROM Users ORDER BY UserID DESC")
        # Retrieves the largest UserID from the Users table
        int_userid = int(cur.fetchone()[0]) + 1  # Forms the new userID by incrementing the largest UserID by 1
        print(int_userid)
        cur.execute("select COUNT(UserName) from Users where UserName=?", (str(str_newusername),))
        # Validates whether chosen username is already in the table
        int_usernamevalidate = int(cur.fetchone()[0])
        print(int_usernamevalidate)
        if int_usernamevalidate != 0:
            self.lbl_info.setText("Username is already in use")
        else:
            str_passwordhash = hashlib.sha256(str_newpassword.encode()).hexdigest()
            print(str_passwordhash)
            cur.execute("INSERT INTO Users VALUES(?,?,?,0)", (int(int_userid), str(str_newusername),
                                                              str(str_passwordhash)))
            con.commit()
            self.loginwindow()

    def loginwindow(self):
        CreateWindow.hide()
        LoginWindow.show()


class MainWindowClass(QtGui.QMainWindow, ui_mainWindow):
    def __init__(self, parent=None):
        mixer.init()  # Starts mixer from pygame for music playback
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.lst_data = []
        self.model = QtGui.QStandardItemModel(self)
        self.tbl_songs.setModel(self.model)
        self.btn_settings.clicked.connect(self.settings)  # settings button programmed
        self.btn_albums.clicked.connect(self.albums)  # Albums button programmed
        self.btn_songs.clicked.connect(self.songs)  # Songs button programmed
        self.btn_artists.clicked.connect(self.artists)  # Artists button programmed
        self.btn_play.clicked.connect(self.play)  # Play button programmed
        self.btn_pause.clicked.connect(self.pause)  # Pause button programmed
        self.btn_playlists.clicked.connect(self.playlists)
        self.btn_search.clicked.connect(self.search)
        self.btn_forward.clicked.connect(self.skipForward)
        self.btn_back.clicked.connect(self.skipBackward)
        self.tbl_songs.doubleClicked.connect(self.retrieve_row)  # Table interaction programmed
        self.btn_plylstmngr.clicked.connect(self.playlistManager)
        self.btn_exit.clicked.connect(self.exit)
        self.queue_next = []
        self.stack_prev = []
        self.int_songSkip = 0
        self.bool_songsQueued = False
        self.lst_nowPlaying = []

    def load_data(self):
        if len(self.lst_data) > 0:  # If data table already has items in it, the table is cleaned
            for i in range(len(self.lst_data) - 1, -1):
                print("removing row", i)
                self.lst_data.pop(i)
                self.model.removeRow(index.row(self.lst_data[i]))
        self.model = QtGui.QStandardItemModel(self)
        self.tbl_songs.setModel(self.model)
        for row in self.lst_data:
            items = [QtGui.QStandardItem(str(field)) for field in row]
            self.model.appendRow(items)

    def retrieve_row(self):
        lst_rowdetails = []
        tbl_rowdetails = self.tbl_songs.selectionModel().selectedRows()
        for index in tbl_rowdetails:
            row = index.row()
            print(row)
            lst_rowdetails = self.lst_data[row]  # Retrieves data from selected row
        print(lst_rowdetails[-1])
        if lst_rowdetails[-1] == 0:  # If the row bears the type of 0, it is a song and is played
            self.bool_songsQueued = False
            self.queue_next = []
            self.stack_prev = []
            self.play_song(lst_rowdetails)
        elif lst_rowdetails[-1] == 1:  # If the row bears the type of 1, it is a artist and the artist's albums are found
            self.artists_to_albums(lst_rowdetails)
        elif lst_rowdetails[-1] == 2:  # if the row bears the type of 2, it is an album and the album's songs are retrieved
            self.albums_to_songs(lst_rowdetails)
        elif lst_rowdetails[-1] == 3:
            self.playlists_to_songs(lst_rowdetails)

    def songs(self):
        self.lbl_artist.setText("Artist:")
        self.lbl_album.setText("Album:")
        str_query = "SELECT * FROM Songs ORDER BY SongName"  # SQL statement to retrieve all of the songs in the Music Library
        cur.execute(str_query)  # Executes SQL statement
        self.lst_data = cur.fetchall()  # Results from statement are fetched
        self.load_data()  # Data found from statement is loaded into table widget
        self.hide_song_columns()

    def albums(self):
        self.lbl_artist.setText("Artist:")
        self.lbl_album.setText("Album:")
        str_query = "SELECT * FROM Albums ORDER BY AlbumName ASC"  # SQL statement to retrieve all albums in the music library
        cur.execute(str_query)  # Statement is executed
        self.lst_data = cur.fetchall()  # Data from statement is fetched
        self.load_data()  # Data from statement is loaded into table widget
        self.hide_album_columns()

    def artists(self):
        self.lbl_artist.setText("Artist:")
        self.lbl_album.setText("Album:")
        str_query = "SELECT * FROM Artists ORDER BY ArtistName ASC"  # SQL statement to retrieve all artists in the music library
        cur.execute(str_query)  # Statement is executed
        self.lst_data = cur.fetchall()  # Data from statement is fetched
        self.load_data()  # Data from statement is loaded into table widget
        self.hide_artist_columns()

    def playlists(self):
        self.lbl_artist.setText("Artist:")
        self.lbl_album.setText("Album:")
        print(LoginWindow.int_userID)
        cur.execute("SELECT * FROM Playlists WHERE UserID=? OR UserID=0", (int(LoginWindow.int_userID),))
        self.lst_data = cur.fetchall()
        self.load_data()

    def artists_to_albums(self, details):
        int_artist_id = details[0]  # Artist ID is retrieved from selected row
        str_artist_name = details[1]
        self.lbl_artist.setText("Artist: " + str_artist_name)
        cur.execute("SELECT * FROM Albums WHERE ArtistID=? ORDER BY AlbumName ASC", (str(int_artist_id),))
        # SQL statement to retrieve all albums
        # by selected artist
        self.lst_data = cur.fetchall()  # Data from statement is fetched
        self.load_data()  # Data from statement is loaded into table widget
        self.hide_album_columns()

    def albums_to_songs(self, details):
        int_album_id = details[0]  # Album ID is retrieved from selected row
        str_album_name = details[1]
        self.lbl_album.setText("Album: " + str_album_name)
        cur.execute("SELECT * FROM Songs WHERE AlbumID=? ORDER BY TrackNumber", (str(int_album_id),))
        # SQL statement to retrieve all songs
        # from selected album
        self.lst_data = cur.fetchall()  # Data from statement is fetched
        self.load_data()  # Data is loaded into table widget
        self.hide_song_columns()

    def playlists_to_songs(self, details):
        int_playlist_id = details[0]
        cur.execute("SELECT PlaylistSongs.SongID, Songs.TrackNumber, Songs.SongName, Songs.SongRating, Songs.Genre,"
                    " Songs.FileLocation, Songs.AlbumID, Songs.Length, Songs.Plays, Songs.Type FROM PlaylistSongs "
                    "INNER JOIN Songs ON PlaylistSongs.SongID = Songs.SongID WHERE PlaylistSongs.PlaylistID = ?"
                    , (int(int_playlist_id),))
        self.lst_data = cur.fetchall()  # Data from statement is fetched
        self.load_data()  # Data is loaded into table widget
        self.hide_song_columns()

    def play_song(self, details):
        print(details)
        self.lst_nowPlaying = details
        str_song_name = details[2]
        str_location = (details[5])  # Song location is retrieved from selected row
        print(str_location)
        int_song_id = details[0]  # Song ID is retrieved from selected row
        int_plays = details[8] + 1  # Number of song plats is retrieved from selected row and incremented
        cur.execute("UPDATE Songs SET Plays=? WHERE SongID=?", (int(int_plays), int(int_song_id)))
        # Updates number of plays of
        # the song in the database
        con.commit()  # Commits previous statement
        mixer.music.load(str_location)  # Selected music is loaded into pygame mixer
        mixer.music.play()  # Selected music is played through the mixer
        self.lbl_nowplaying.setText("Now Playing: " + str_song_name)
        if self.bool_songsQueued == False:
            self.queueSongs()
        self.refreshmostplayedplaylist()
        self.next_song()


    def play(self):
        mixer.music.unpause()  # Music in mixer is paused

    def pause(self):
        mixer.music.pause()  # Music in mixer is resumed

    def settings(self):
        if LoginWindow.int_admin == 0:
            SettingsWindow.fr_admin.hide()
        else:
            SettingsWindow.loadUserData()
        SettingsWindow.show()  # Settings window is shown

    def hide_song_columns(self):
        for i in range(8):
            columns_to_hide = (0, 3, 4, 5, 6, 7, 8, 9)
            self.tbl_songs.hideColumn(columns_to_hide[i])
            i += 1

    def hide_album_columns(self):
        for i in range(3):
            columns_to_hide = (0, 2, 3)
            self.tbl_songs.hideColumn(columns_to_hide[i])
            i += 1

    def hide_artist_columns(self):
        for i in range(2):
            columns_to_hide = (0, 2)
            self.tbl_songs.hideColumn(columns_to_hide[i])
            i += 1

    def queueSongs(self):
        self.queue_next = []
        flag = False
        i = 1
        while flag == False:
            row_details = []
            table_row_details = self.tbl_songs.selectionModel().selectedRows()
            for index in table_row_details:
                row = index.row() + i
                print(row)
                row_details = self.lst_data[row]
                print(row_details[2])
                self.queue_next.append(row_details)
                if row_details[0] == self.lst_data[-1][0]:
                    flag = True
                i = i + 1
        self.bool_songsQueued = True

    def next_song(self):
        while mixer.music.get_busy() == True and self.int_songSkip == 0:
            QtCore.QCoreApplication.processEvents()
        if self.int_songSkip == -1:
            self.int_songSkip = 0
            self.queue_next.insert(0, self.lst_nowPlaying)
            next_song = self.stack_prev[0]
            self.stack_prev.remove(next_song)
            print("Song changing to " + next_song[2])
            self.play_song(next_song)
        else:
            self.int_songSkip = 0
            self.stack_prev.insert(0, self.lst_nowPlaying)
            next_song = self.queue_next[0]
            self.queue_next.remove(next_song)
            print("Song changing to " + next_song[2])
            self.play_song(next_song)

    def search(self):
        self.searchTerm = self.txt_search.text()
        self.searchTerm = str(self.searchTerm + "%")
        self.searchTable = self.drp_search.currentText()
        if self.searchTable == "Songs":
            cur.execute("SELECT * FROM Songs WHERE SongName LIKE ?", (self.searchTerm,))
            self.lst_data = cur.fetchall()
            self.load_data()
            self.hide_song_columns()
        elif self.searchTable == "Albums":
            cur.execute("SELECT * FROM Albums WHERE AlbumName LIKE ?", (self.searchTerm,))
            self.lst_data = cur.fetchall()
            self.load_data()
            self.hide_album_columns()
        elif self.searchTable == "Artists":
            cur.execute("SELECT * FROM Artists WHERE ArtistName LIKE ?", (self.searchTerm,))
            self.lst_data = cur.fetchall()
            self.load_data()
            self.hide_artist_columns()
        else:
            cur.execute("SELECT * FROM Playlists WHERE Playlist LIKE ?", (self.searchTerm,))
            self.lst_data = cur.fetchall()
            self.load_data()

    def skipForward(self):
        self.int_songSkip = 1

    def skipBackward(self):
        self.int_songSkip = -1

    def refreshmostplayedplaylist(self):
        cur.execute("DELETE FROM PlaylistSongs WHERE PlaylistID = 1")
        con.commit()
        cur.execute("SELECT * FROM Songs WHERE Plays > 0 ORDER BY Plays DESC")
        lst_playlistItems = cur.fetchall()
        print(lst_playlistItems)
        cur.execute("SELECT PlaylistSongsID FROM PlaylistSongs ORDER BY PlaylistSongsID DESC")
        latestPlaylistSongsID = cur.fetchone()[0] + 1
        for i in range(20):
            cur.execute("SELECT PlaylistSongsID FROM PlaylistSongs ORDER BY PlaylistSongsID DESC")
            PlaylistSongsID = latestPlaylistSongsID + i
            print(PlaylistSongsID)
            songID = lst_playlistItems[i][0]
            cur.execute("INSERT INTO PlaylistSongs VALUES(?,1,?)", (int(PlaylistSongsID), int(songID),))
            con.commit()

    def playlistManager(self):
        PlaylistWindow.showFullScreen()
        print(LoginWindow.int_userID)
        cur.execute("SELECT * FROM Playlists WHERE UserID=?", (int(LoginWindow.int_userID),))
        PlaylistWindow.playlistData = cur.fetchall()
        PlaylistWindow.load_playlist_data(PlaylistWindow.playlistData)
        PlaylistWindow.load_song_data()

    def exit(self):
        os._exit(0)


class SettingsWindowClass(QtGui.QMainWindow, ui_settingsWindow):
        def __init__(self, parent=LoginWindowClass):
            QtGui.QMainWindow.__init__(self, parent)
            self.setupUi(self)
            self.selectedUser = ""
            self.tbl_users.clicked.connect(self.select_user)
            self.btn_import.clicked.connect(self.importing)  # settings button pressed
            self.btn_logout.clicked.connect(self.logout)
            self.btn_delUser.clicked.connect(self.deleteUser)
            self.btn_admin.clicked.connect(self.toggleAdmin)
            self.btn_exit.clicked.connect(self.exit)

        def loadUserData(self):
            print(self.int_userID)
            cur.execute("SELECT * FROM Users WHERE UserID != ?", (int(self.int_userID),))
            self.lst_data = cur.fetchall()
            print(self.lst_data)
            if len(self.lst_data) > 0:  # If data table already has items in it, the table is cleaned
                for i in range(len(self.lst_data) - 1, -1):
                    print("removing row", i)
                    self.lst_data.pop(i)
                    self.model.removeRow(index.row(self.lst_data[i]))
            self.model = QtGui.QStandardItemModel(self)
            self.tbl_users.setModel(self.model)
            for row in self.lst_data:
                items = [QtGui.QStandardItem(str(field)) for field in row]
                self.model.appendRow(items)

        def select_user(self):
            row_details = []
            table_row_details = self.tbl_users.selectionModel().selectedRows()
            for index in table_row_details:
                row = index.row()
                print(row)
                row_details = self.lst_data[row]  # Retrieves data from selected row
            self.selectedUser = row_details
            self.lbl_user.setText("User: " + row_details[1])

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
                        length_info = MP3(song_location)
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
                            cur.execute("INSERT INTO Artists VALUES(?,?,1)", (int(artist_id), str(artist_name)))
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
                            cur.execute("INSERT INTO Albums VALUES(?,?,?,2)", (int(album_id), str(album_name),
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
                        slash_location = track_number.find("/")
                        if slash_location != -1:
                            track_number = track_number[:slash_location]
                            print(track_number)
                        track_number = int(track_number)
                        cur.execute("INSERT INTO Songs VALUES(?,?,?,?,?,?,?,0,0)", (int(song_id), int(track_number),
                                                                                str(song_name), str(genre),
                                                                                str(song_location), int(album_id),
                                                                                       int(length)))
                        # appends data to table
                        counter += 1  # increments counter for next song
            print("Complete")  # once all files have been added, 'Complete is printed'

        def logout(self):
            LoginWindow.userID = ""
            MainWindow.hide()
            SettingsWindow.hide()
            LoginWindow.show()

        def exit(self):
            SettingsWindow.hide()

        def deleteUser(self):
            cur.execute("DELETE FROM Users WHERE UserID = ?", (int(self.selectedUser[0]),))
            con.commit()
            self.loadUserData()
            self.selectedUser = ""

        def toggleAdmin(self):
            if self.selectedUser[3] == 0:
                cur.execute("UPDATE Users SET Administrator = 1 WHERE UserID = ?", (int(self.selectedUser[0]),))
                con.commit()
            else:
                cur.execute("UPDATE Users SET Administrator = 0 WHERE UserID = ?", (int(self.selectedUser[0]),))
                con.commit()
            self.loadUserData()
            self.selectedUser = ""


class PlaylistWindowClass(QtGui.QMainWindow, ui_playlistWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.playlistData = []
        self.btn_close.clicked.connect(self.close_window)
        self.tbl_playlists.doubleClicked.connect(self.retrieve_playlists_row)
        self.tbl_songs.doubleClicked.connect(self.add_to_playlist)
        self.btn_plylstreset.clicked.connect(self.playlist_reset)
        self.btn_newplylst.clicked.connect(self.new_playlist)

    def retrieve_playlists_row(self):
        row_details = []
        table_row_details = self.tbl_playlists.selectionModel().selectedRows()
        for index in table_row_details:
            row = index.row()
            print(row)
            row_details = self.playlistData[row]  # Retrieves data from selected row
            print(row_details)
        print(row_details[-1])
        if row_details[-1] == 3:  # If the row bears the type of 0, it is a song and is played
            self.playlists_to_songs(row_details)
        else:
            self.remove_from_playlist(row_details)

    def add_to_playlist(self):
        row_details = []
        table_row_details = self.tbl_songs.selectionModel().selectedRows()
        for index in table_row_details:
            row = index.row()
            print(row)
            row_details = self.songData[row]  # Retrieves data from selected row
            print(row_details)
        songID = row_details[0]
        cur.execute("SELECT PlaylistSongsID FROM PlaylistSongs ORDER BY PlaylistSongsID DESC")
        try:
            PlaylistSongsID = int(cur.fetchall()[0][0]) + 1
        except:
            PlaylistSongsID = int(cur.fetchone()[0]) + 1
            print(PlaylistSongsID)
        cur.execute("INSERT INTO PlaylistSongs VALUES (?,?,?)", (int(PlaylistSongsID), int(self.playlist_id),
                                                                 int(songID),))
        con.commit()
        self.refresh_playlist()

    def remove_from_playlist(self, row_details):
        songID = row_details[1]
        print(songID, self.playlist_id)
        cur.execute("DELETE FROM PlaylistSongs WHERE PlaylistID = ? AND SongID = ?", (int(self.playlist_id),
                                                                                      int(songID),))
        print("Executed")
        con.commit()
        self.refresh_playlist()

    def playlists_to_songs(self, details):
        self.playlist_id = details[0]
        self.playlist_query = "SELECT PlaylistSongs.PlaylistID, Songs.SongID, Songs.SongName FROM PlaylistSongs " \
                              "INNER JOIN Songs ON PlaylistSongs.SongID = Songs.SongID " \
                              "WHERE PlaylistSongs.PlaylistID = ?"
        cur.execute(self.playlist_query, (int(self.playlist_id),))
        self.playlistData = cur.fetchall()
        self.load_playlist_data(self.playlistData)

    def load_song_data(self):
        cur.execute("SELECT * FROM Songs")
        self.songData = cur.fetchall()
        if len(self.songData) > 0:  # If data table already has items in it, the table is cleaned
            for i in range(len(self.songData) - 1, -1):
                print("removing row", i)
                self.songData.pop(i)
                self.model.removeRow(index.row(self.lst_data[i]))
        self.model = QtGui.QStandardItemModel(self)
        self.tbl_songs.setModel(self.model)
        for row in self.songData:
            items = [QtGui.QStandardItem(str(field)) for field in row]
            self.model.appendRow(items)
        for i in range(8):
            columns_to_hide = (0, 3, 4, 5, 6, 7, 8, 9)
            self.tbl_songs.hideColumn(columns_to_hide[i])
            i += 1

    def load_playlist_data(self, playlistdata):
        print(playlistdata)
        if len(playlistdata) > 0:  # If data table already has items in it, the table is cleaned
            for i in range(len(playlistdata) - 1, -1):
                print("removing row", i)
                playlistdata.pop(i)
                self.model.removeRow(index.row(self.lst_data[i]))
        self.model = QtGui.QStandardItemModel(self)
        self.tbl_playlists.setModel(self.model)
        for row in playlistdata:
            items = [QtGui.QStandardItem(str(field)) for field in row]
            self.model.appendRow(items)

    def refresh_playlist(self):
        cur.execute(self.playlist_query, (int(self.playlist_id),))
        playlistData = cur.fetchall()
        self.load_playlist_data(playlistData)

    def close_window(self):
        PlaylistWindow.hide()

    def playlist_reset(self):
        cur.execute("SELECT * FROM Playlists WHERE UserID=? OR UserID=0", (int(LoginWindow.userID),))
        self.playlistData = cur.fetchall()
        self.load_playlist_data(self.playlistData)

    def new_playlist(self):
        PlaylistNameWindow.show()


class PlaylistDialogClass(QtGui.QDialog, ui_playlistDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.btn_ok.clicked.connect(self.add_playlist)
        self.btn_cancel.clicked.connect(self.close_window)

    def add_playlist(self):
        playlistName = self.txt_plylstname.text()
        if len(playlistName) <= 5:
            self.lbl_plylst_create.setText("Longer Playlist Name Needed")
        else:
            cur.execute("SELECT PlaylistID FROM Playlists ORDER BY PlaylistID DESC")
            playlistID = cur.fetchall()[0][0] + 1
            cur.execute("INSERT INTO Playlists VALUES (?,?,?,3)", (int(playlistID), str(playlistName),
                                                                   int(LoginWindow.userID)))
            con.commit()
            PlaylistWindow.playlist_reset()
            PlaylistNameWindow.hide()

    def close_window(self):
        PlaylistNameWindow.hide()


app = QtGui.QApplication(sys.argv)
LoginWindow = LoginWindowClass(None)
MainWindow = MainWindowClass(None)
SettingsWindow = SettingsWindowClass(None)
CreateWindow = CreateAccountWindowClass(None)
PlaylistWindow = PlaylistWindowClass(None)
PlaylistNameWindow = PlaylistDialogClass(None)
LoginWindow.show()
app.setWindowIcon(QtGui.QIcon('Icon.png'))
app.exec_()