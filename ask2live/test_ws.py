from asgiref.sync import async_to_sync
import websockets

def test_url(url, data=""):
    conn = async_to_sync(websockets.connect)(url)
    async_to_sync(conn.send)(data)


test_url("ws://143.248.226.51:8002/rooms/8")