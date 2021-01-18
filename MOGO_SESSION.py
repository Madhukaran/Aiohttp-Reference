import time
from aiohttp import web
from aiohttp_session import setup, get_session
from aiohttp_session_mongo import MongoStorage
import motor.motor_asyncio as aiomotor
import asyncio
from asyncio import transports


async def handler(request):
    session = await get_session(request)
    print(session)
    last_visit = session['last_visit'] if 'last_visit' in session else None
    session['last_visit'] = time.time()
    session['TESTING'] = "BEAST"
    text = 'Last visited: {}'.format(last_visit)
    peername = request.transport.get_extra_info('peername')
    print(peername)
    """
    A transport used to process request. Read-only property.
    The property can be used, for example, for getting IP address of client’s peer:
    here the Peername will specify the Spceific ip Address of the client where the request is made!
    Simple: We can get the Specific local ip address of the user from the web request.
    library: from asyncio import transports
    Refrence: https://docs.aiohttp.org/en/stable/web_reference.html?highlight=peername#aiohttp.web.Request.transport
    """
    if peername is not None:
        host, port = peername
    return web.Response(text=text)


async def init_mongo(loop):
    url = "mongodb://192.168.1.221:27017"
    conn = aiomotor.AsyncIOMotorClient(
        url, maxPoolSize=2, io_loop=loop)
    db = 'MadhukaranDb'
    return conn[db]


async def setup_mongo(app, loop):
    db = await init_mongo(loop)

    async def close_mongo(app):
        db.client.close()

    app.on_cleanup.append(close_mongo)
    return db


async def make_app():
    app = web.Application()
    loop = asyncio.get_event_loop()

    db = await setup_mongo(app, loop)
    session_collection = db['sessions']

    max_age = 3600 * 24 * 365 # 1 year
    setup(app, MongoStorage(session_collection,max_age=60,cookie_name="CHAT_APP"))

    app.router.add_get('/', handler)
    return app


web.run_app(make_app(),host='192.168.1.18')
