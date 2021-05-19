class DataBaseTables:
    SONGS = "songs"
    SONG_TO_TAG = "songtotag"
    STAFF = "staff"
    TAGS = "tags"
    USER_BUY_SONG = "userbuysong"
    USERS = "users"


class UserFields:
    ID = "id"
    NAME = "name"
    PASS = "password"


class StaffFields:
    STAFF_ID = "staff_id"
    USER_ID = "user_id"


class SongFields:
    ID = "id"
    NAME = "name"
    OWNER_ID = "owner_id"


class SongToTagFields:
    SONG_ID = "song_id"
    TAG_NAME = "tag_name"


class TagFields:
    NAME = "name"


class UserBuySong:
    SONG_ID = "song_id"
    USER_ID = "user_id"
