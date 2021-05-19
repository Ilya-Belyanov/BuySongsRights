def printAllSongs(songs: list, authors: list, tags: list):
    print("----------")
    print("Список песен:")
    if len(songs) == 0:
        print("Песен пока нет", end="\n\n")
    else:
        __printSongs(songs, authors, tags)


def printBuyingSongs(songs: list, authors: list, tags: list):
    print("----------")
    print("Список купленных песен:")
    if len(songs) == 0:
        print("Вы не купили ни одну песню", end="\n\n")
    else:
        __printSongs(songs, authors, tags)


def __printSongs(songs: list, authors: list, tags: list):
    for i in range(len(songs)):
        print(f"{i + 1}. {songs[i]} (автор - '{authors[i]}', тэги - {tags[i]})")
    print("----------", end="\n\n")


def printMySongs(songs: list, tags: list):
    print("----------")
    print("Список ваших песен:")
    if len(songs) == 0:
        print("Вы не добавили ни одну песню")
    for i in range(len(songs)):
        print(f"{i + 1}. {songs[i]} (тэги - {tags[i]})")
    print("----------", end="\n\n")


def printAllTags(tags: list):
    print("----------")
    print("Список тэгов")
    if len(tags) == 0:
        print("Тэгов пока нет...")
    for i in range(len(tags)):
        print(f"{i + 1}. {tags[i]}")
    print("----------", end="\n\n")
