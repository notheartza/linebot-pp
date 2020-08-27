def getLog(client, firebase_rdb):
    userresults = client.open("linebothistory").get_worksheet(0)
    userssheet = userresults.get_all_records()
    for i in userssheet:
        data = {
            "date": i["date"],
            "userName": i["userName"],
            "pictureProfile": i["pictureProfile"],
            "status": i["สถานะ"],
            "room": i['room'],
            "number": i['number']
        }

        firebase_rdb.child("users").child(i["userId"]).set(data)

    return 'finish'    