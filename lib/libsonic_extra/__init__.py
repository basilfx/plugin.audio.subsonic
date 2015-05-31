import urllib
import urlparse
import libsonic


def force_dict(value):
    """
    Coerce the input value to a dict.
    """

    if type(value) == dict:
        return value
    else:
        return {}


def force_list(value):
    """
    Coerce the input value to a list.

    If `value` is `None`, return an empty list. If it is a single value, create
    a new list with that element on index 0.

    :param value: Input value to coerce.
    :return: Value as list.
    :rtype: list
    """

    if value is None:
        return []
    elif type(value) == list:
        return value
    else:
        return [value]


class Connection(libsonic.Connection):
    """
    Extend `libsonic.Connection` with new features and fix a few issues.

    - Add library name property.
    - Parse URL for host and port for constructor.
    - Make sure API results are of of uniform type.

    :param str name: Name of connection.
    :param str url: Full URL (including protocol) of SubSonic server.
    :param str username: Username of server.
    :param str password: Password of server.
    """

    def __init__(self, url, username, password):
        self._intercept_url = False

        # Parse SubSonic URL
        parts = urlparse.urlparse(url)
        scheme = parts.scheme or "http"

        # Make sure there is hostname
        if not parts.hostname:
            raise ValueError("Expected hostname for URL: %s" % url)

        # Validate scheme
        if scheme not in ("http", "https"):
            raise ValueError("Unexpected scheme '%s' for URL: %s" % (
                scheme, url))

        # Pick a default port
        host = "%s://%s" % (scheme, parts.hostname)
        port = parts.port or {"http": 80, "https": 443}[scheme]

        # Invoke original constructor
        super(Connection, self).__init__(host, username, password, port=port)

    def getArtists(self, *args, **kwargs):
        """
        """

        def _artists_iterator(artists):
            for artist in force_list(artists):
                artist["id"] = int(artist["id"])
                yield artist

        def _index_iterator(index):
            for index in force_list(index):
                index["artist"] = list(_artists_iterator(index.get("artist")))
                yield index

        response = super(Connection, self).getArtists(*args, **kwargs)
        response["artists"] = response.get("artists", {})
        response["artists"]["index"] = list(
            _index_iterator(response["artists"].get("index")))

        return response

    def getPlaylists(self, *args, **kwargs):
        """
        """

        def _playlists_iterator(playlists):
            for playlist in force_list(playlists):
                playlist["id"] = int(playlist["id"])
                yield playlist

        response = super(Connection, self).getPlaylists(*args, **kwargs)
        response["playlists"]["playlist"] = list(
            _playlists_iterator(response["playlists"].get("playlist")))

        return response

    def getPlaylist(self, *args, **kwargs):
        """
        """

        def _entries_iterator(entries):
            for entry in force_list(entries):
                entry["id"] = int(entry["id"])
                yield entry

        response = super(Connection, self).getPlaylist(*args, **kwargs)
        response["playlist"]["entry"] = list(
            _entries_iterator(response["playlist"].get("entry")))

        return response

    def getArtist(self, *args, **kwargs):
        """
        """

        def _albums_iterator(albums):
            for album in force_list(albums):
                album["id"] = int(album["id"])
                yield album

        response = super(Connection, self).getArtist(*args, **kwargs)
        response["artist"]["album"] = list(
            _albums_iterator(response["artist"].get("album")))

        return response

    def getAlbum(self, *args, **kwargs):
        ""
        ""

        def _songs_iterator(songs):
            for song in force_list(songs):
                song["id"] = int(song["id"])
                yield song

        response = super(Connection, self).getAlbum(*args, **kwargs)
        response["album"]["song"] = list(
            _songs_iterator(response["album"].get("song")))

        return response

    def getAlbumList2(self, *args, **kwargs):
        ""
        ""

        def _album_iterator(albums):
            for album in force_list(albums):
                album["id"] = int(album["id"])
                yield album

        response = super(Connection, self).getAlbumList2(*args, **kwargs)
        response["albumList2"]["album"] = list(
            _album_iterator(response["albumList2"].get("album")))

        return response

    def getMusicDirectory(self, *args, **kwargs):
        """
        """

        def _children_iterator(children):
            for child in force_list(children):
                child["id"] = int(child["id"])

                if "parent" in child:
                    child["parent"] = int(child["parent"])
                if "coverArt" in child:
                    child["coverArt"] = int(child["coverArt"])
                if "artistId" in child:
                    child["artistId"] = int(child["artistId"])
                if "albumId" in child:
                    child["albumId"] = int(child["albumId"])

                yield child

        response = super(Connection, self).getMusicDirectory(*args, **kwargs)
        response["directory"]["child"] = list(
            _children_iterator(response["directory"].get("child")))

        return response

    def getCoverArtUrl(self, *args, **kwargs):
        """
        Return an URL to the cover art.
        """

        self._intercept_url = True
        url = self.getCoverArt(*args, **kwargs)
        self._intercept_url = False

        return url

    def streamUrl(self, *args, **kwargs):
        """
        Return an URL to the file to stream.
        """

        self._intercept_url = True
        url = self.stream(*args, **kwargs)
        self._intercept_url = False

        return url

    def _doBinReq(self, *args, **kwargs):
        """
        Intercept request URL.
        """

        if self._intercept_url:
            parts = list(urlparse.urlparse(
                args[0].get_full_url() + "?" + args[0].data))
            parts[4] = dict(urlparse.parse_qsl(parts[4]))
            parts[4].update({"u": self.username, "p": self.password})
            parts[4] = urllib.urlencode(parts[4])

            return urlparse.urlunparse(parts)
        else:
            return super(Connection, self)._doBinReq(*args, **kwargs)
