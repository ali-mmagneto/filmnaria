import pymongo
from database.guncelTarih import guncelTarih
from database.ia_filterdb import Media
from info import DATABASE_URI, DATABASE_NAME
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
from pyrogram.types import Message
myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]



async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    # mycol.create_index([('text', 'text')])

    data = {
        'text': str(text),
        'reply': str(reply_text),
        'btn': str(btn),
        'file': str(file),
        'alert': str(alert)
    }

    try:
        mycol.update_one({'text': str(text)}, {"$set": data}, upsert=True)
    except:
        logger.exception('Some error occured!', exc_info=True)


async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]

    query = mycol.find({"text": name})
    # query = mycol.find( { "$text": {"$search": name}})
    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            try:
                alert = file['alert']
            except:
                alert = None
        return reply_text, btn, alert, fileid
    except:
        return None, None, None, None


async def get_filters(group_id):
    mycol = mydb[str(group_id)]

    texts = []
    query = mycol.find()
    try:
        for file in query:
            text = file['text']
            texts.append(text)
    except:
        pass
    return texts


async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]

    myquery = {'text': text}
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`'  deleted. I'll not respond to that filter anymore.",
            quote=True,
            parse_mode="md"
        )
    else:
        await message.reply_text("Couldn't find that filter!", quote=True)


async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await message.edit_text(f"Nothing to remove in {title}!")
        return

    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await message.edit_text(f"All filters from {title} has been removed")
    except Exception as e:
        await message.edit_text(f"Couldn't remove all filters from group!\n{str(e)}")


async def delete_all_users(message:Message):
    try:
        mydb['users'].drop()
        await message.edit_text(f"Tüm kullanıcılar silindi.\n{guncelTarih()}")
    except Exception as e:
        await message.edit_text(f"Couldn't remove all users!\n{str(e)}")


async def delete_all_groups(message:Message):
    try:
        mydb['groups'].drop()
        await message.edit_text(f"Tüm gruplar silindi.\n{guncelTarih()}")
    except Exception as e:
        await message.edit_text(f"Couldn't remove all groups!\n{str(e)}")


async def delete_all_files(message:Message):
    try:
        await Media.collection.drop()
        await message.edit_text(f"Tüm dosyalar silindi.\n{guncelTarih()}")
    except Exception as e:
        await message.edit_text(f"Couldn't remove all files!\n{str(e)}")


async def count_filters(group_id):
    mycol = mydb[str(group_id)]

    count = mycol.count()
    return False if count == 0 else count


async def filter_stats():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count()
        totalcount += count

    totalcollections = len(collections)

    return totalcollections, totalcount
