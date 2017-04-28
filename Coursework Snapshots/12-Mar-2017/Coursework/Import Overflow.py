song_location = str(dirName + '\\' + fname)
                        song = EasyID3(song_location)
                        song_id = int(counter)
                        rsong_name = (song["title"])
                        song_name = rsong_name_name[2:-2]
                        rgenre_name = (song["genre"])

                        rtrack_number = (song["tracknumber"])
                        rproducer_name = (song["organization"])
                        rartist_name = (song["artist"])
                        counter = counter + 1