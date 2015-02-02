import web
import hashlib
import MySQLdb
import json
import smtplib

urls = (
    '/', 'index',
    '/login','login',
    '/register', 'register',
    '/checkregistration', 'checkregistration',
    '/updateuserprofile', 'updateuserprofile',

    '/subscription', 'subscription',
    '/updatesubsciption', 'updatesubsciption',
    '/deletesubscription', 'deletesubscription',

    '/deletecontact', 'deletecontact',

    '/TeleConnectingIncoming,TeleConnectingIncoming',
    '/TeleConnectComplete,TeleConnectComplete',
    '/CreateAlert', 'CreateAlert',
    '/emergency', 'emergency',
)

db = web.database(dbn='mysql', user='root', pw='', db='db_igothelp')


class index:
    #def GET(self):
       # CFObj = Commonfunctions()

       # return CFObj.GetEmrContact(1, "ea8a003b017650c5a58927b60ff32585", 2)
       # return CFObj.GetEmrContact(1, "ea8a003b017650c5a58927b60ff32585", 2)
    def GET(self):
         status = {"status": "Info", "message":"This page is intentionally left blank."}
         return json.dumps(status)


#FOR REUSABLE FUNCTIONS
class Commonfunctions:
    def GetIdFromAuth(self, AuthCode):
        k = "user_authcode='" + AuthCode + "'"
        entries = db.select('tbl_userprofile', what='user_id', where=k)
        rows = entries.list();
        if rows:
            return rows[0]['user_id']
        else:
            status = {"status": "Error", "message": "AuthCode is not associated with any User"}
            return json.dumps(status)
    def GetIdFromPhone(self, Number,Type): #Type= 'USR' for User and 'DOC for Doctor'
        if Type=="USR":
            k = "user_phone='" + Number + "'"
            table="tbl_userprofile"
            What="user_id"
        else:
            k = "doctor_phone='" + Number + "'"
            table="tbl_doctor"
            What="doctor_id"

        entries = db.select(table, what=What, where=k)
        rows = entries.list();
        if rows:
            return rows[0][What]
        else:
            status = {"status": "Error", "message": "Nothing Found"}
            return json.dumps(status)

    def CheckAuth(self, AuthCode):
        k = "user_authcode='" + AuthCode + "'"
        entries = db.select('tbl_userprofile', where=k)
        rows = entries.list();
        JArray = "{"
        if rows:
            for row in rows:
                JArray += "{"
                JArray += "id:" + str(row['user_id'])
                JArray += ",firstname:" + row['user_firstname']
                JArray += ",lastname:" + row['user_lastname']
                JArray += ",phone:" + row['user_phone']
                JArray += ",email:" + row['user_email']
                JArray += ",dob:" + row['user_dob']
                JArray += ",gender:" + row['user_gender']
                JArray += ",bloodgroup:" + row['user_bloodgroup']
                JArray += ",authcode:" + row['user_authcode']
                JArray += ",lat:" + row['user_lat']
                JArray += ",lon:" + row['user_lon']
                JArray += "},"
            JArray += "}"
            return json.dumps(JArray)
        else:
            return 0

    def SendMail(self, To, From, Subject, Body):
        try:
            web.config.smtp_server = 'smtp.gmail.com'
            web.config.smtp_port = 587
            web.config.smtp_username = 'abhilash.c@spurtreetech.com'
            web.config.smtp_password = 'Ab4i7@$h'
            web.config.smtp_starttls = True
            web.sendmail(To, From, Subject, Body)
        except smtplib.SMTPAuthenticationError:
            status = {"status": "Error", "message": "Authentication Error"}
            return json.dumps(status)
        except Exception as e:
            return e
        else:
            status = {"status": "Sucess", "message": "Mail Sent"}
            return json.dumps(status)

    def GetEmrContact(self, Opt, Incoming, Type):
                                                    # Opt will tell the fuction should return number only
                                                    # or the entire data
                                                    # Incoming can be both Authcode or Phone Number
                                                    # Type will determine which one

        if Type == 1:
            k = "user_phone='" + Incoming + "'"
            TypeStr = "Phone Number"
        elif Type == 2:
            k = "user_authcode='" + Incoming + "'"
            TypeStr = "AuthCode"
        else:
            status = {"status": "Syntax Error", "message": "Type should be 1 or 2"}
            return json.dumps(status)

        entries = db.select('tbl_userprofile', what='user_id', where=k)
        rows = entries.list();
        if rows:
            User_Id = rows[0]['user_id']
        else:
            status = {"status": "Error", "message": "No Emergency Contact added for this user/No user with this "+TypeStr}
            return json.dumps(status)

        if Opt == 1:  # RETURN ONLY PHONE NUMBER OF THE CONTACT
            entries2 = db.select('tbl_contact', what='contact_phone', where="user_id=" + str(User_Id))
        elif Opt == 2:  # RETRUN ALL THE DETAILS OF A CONTACT
            entries2 = db.select('tbl_contact', where="user_id=" + str(User_Id))
        else:
            status = {"status": "Syntax Error", "message": "Opt should be 1 or 2"}
            return json.dumps(status)
        rows2 = entries2.list()

        if rows2:
            JArray = "{"
            if Opt == 2:
                for row in rows2:
                    print row.keys()
                    JArray += "{"
                    JArray += "id:" + str(row['contact_id'])
                    JArray += ",name:" + row['contact_name']
                    JArray += ",phone:" + row['contact_phone']
                    JArray += ",email:" + row['contact_email']
                    JArray += "},"
                JArray += "}"
            else:
                Cnt = 0
                for row in rows2:
                    Cnt += 1
                    JArray += str(Cnt) + ":" + row['contact_phone'] + ","
            JArray += "}"
            return json.dumps(JArray)
        else:
            return 0


class checkregistration:
    def GET(self):
         status = {"status": "Info", "message":"This page is intentionally left blank."}
         return json.dumps(status)

    def POST(self):
        user_data = web.input(Phone="")
        k = "user_phone='" + user_data.Phone + "'"
        entries = db.select('tbl_userprofile', what='user_authcode', where=k)
        rows = entries.list();
        if rows:
            return rows[0]['user_authcode']
        else:
            status = {"status": "Error", "message": "Phone number is not associated with any User"}
            return json.dumps(status)

class register:
    def GET(self):
         status = {"status": "Info", "message":"This page is intentionally left blank."}
         return json.dumps(status)

    def POST(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        user_data = web.input()
        flag = 0
        if user_data.firstname == "":
            status = {"status": "Error", "message": "First name is mandatory"}
            flag = 1
        if user_data.lastname == "":
            status = {"status": "Error", "message": "Last name is mandatory"}
            flag = 1
        if user_data.dob == "":
            status = {"status": "Error", "message": "Date of Birth is mandatory"}
            flag = 1
        if user_data.bloodgroup == "":
            status = {"status": "Error", "message": "Blood Group is mandatory"}
            flag = 1
        if user_data.gender == "":
            status = {"status": "Error", "message": "Gender is mandatory"}
            flag = 1
        if user_data.email == "":
            status = {"status": "Error", "message": "Email ID is mandatory"}
            flag = 1
        if user_data.phone == "":
            status = {"status": "Error", "message": "Phone number is mandatory"}
            flag = 1
        if flag == 0:
            Salt = "$343dddSS"
            String = user_data.firstname + user_data.phone + Salt
            m = hashlib.md5()
            m.update(String)
            Authcode = m.hexdigest()
            try:
                entries = db.insert('tbl_userprofile', user_firstname=user_data.firstname, \
                                    user_lastname=user_data.lastname, user_phone=user_data.phone, \
                                    user_email=user_data.email, user_dob=user_data.dob, \
                                    user_gender=user_data.gender, user_bloodgroup=user_data.bloodgroup, \
                                    user_authcode=Authcode \
                    )
                #PUSH OTP
                #PUSH AUTHCODE
                salut = "Mr."
                if (user_data.gender == "female"):
                    salut = "M/s"

                ComFnObj.SendMail(user_data.email, "support@igothelp.com", "Registration Complete", "Hello " + \
                                  salut + " " + user_data.lastname + "\n This is from support<DATA TO BE INSERTED HERE>")
                status = {"status": "Success", "message": "Update Successful"}
            except MySQLdb.IntegrityError, e:
                status = {"status": "Error", "message": "Phone Number already registered"}
            return json.dumps(status)
class login:

    def GET(self):
         status = {"status": "Info", "message":"This page is intentionally left blank."}
         return json.dumps(status)

    def POST(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        user_data = web.input()
        flag = 0
        Id1= ComFnObj.GetIdFromPhone(user_data.Phone,"USR")
        Id2= ComFnObj.GetIdFromAuth(user_data.Authcode)
        if (Id1!=Id2):
            return user_data.Authcode
        else:
           status = {"status": "Sucess", "message": "Login Sucess"}
           return json.dumps(status)

class updateuserprofile:
    def GET(self):
         status = {"status": "Info", "message":"This page is intentionally left blank."}
         return json.dumps(status)

    def POST(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        user_data = web.input()
        flag = 0
        if (ComFnObj.CheckAuth(user_data.AuthCode) == 0):
            status = {"status": "Error", "message": "AuthCode Failed"}
            return json.dumps(status)

        if user_data.firstname == "":
            status = {"status": "Error", "message": "First name is mandatory"}
            flag = 1
        if user_data.lastname == "":
            status = {"status": "Error", "message": "Last name is mandatory"}
            flag = 1
        if user_data.dob == "":
            status = {"status": "Error", "message": "Date of Birth is mandatory"}
            flag = 1
        if user_data.bloodgroup == "":
            status = {"status": "Error", "message": "Blood Group is mandatory"}
            flag = 1
        if user_data.gender == "":
            status = {"status": "Error", "message": "Gender is mandatory"}
            flag = 1
        if user_data.email == "":
            status = {"status": "Error", "message": "Email ID is mandatory"}
            flag = 1
        if user_data.phone == "":
            status = {"status": "Error", "message": "Phone number is mandatory"}
            flag = 1
        if flag == 0:
            try:
                k = user_id = user_data.id
                entries = db.update('tbl_userprofile', user_firstname=user_data.firstname, \
                                    user_lastname=user_data.lastname, user_phone=user_data.phone, \
                                    user_email=user_data.email, user_dob=user_data.dob, \
                                    user_gender=user_data.gender, user_bloodgroup=user_data.bloodgroup \
                                    , where=k)
                #PUSH OTP
                #PUSH AUTHCODE
                status = {"status": "Success", "message": "Update Successful"}
            except MySQLdb.IntegrityError, e:
                status = {"status": "Error", "message": "Phone Number already registered"}
                return json.dumps(status)
            else:
                return json.dumps(status)

class subscription:
    def GET(self):
        entries = db.select('tbl_subscriptionplan')
        rows = entries.list();
        JArray = "{"
        if rows:
            for row in rows:
                JArray += "{"
                JArray += "id:" + str(row['subscription_id'])
                JArray += ",Name:" + row['subscription_name']
                JArray += ",Validity:" + str(row['subscription_validity'])
                JArray += ",Features:" + row['subscription_features']
                JArray += ",Total_TeleMedCalls:" + str(row['subscription_TotTelMedCalls'])
                JArray += ",Total_AlertCalls:" + str(row['subscription_TotAlertCalls'])
                JArray += "},"
            JArray += "}"
            return json.dumps(JArray)

    def POST(self):
        user_data = web.input()
        flag = 0
        if user_data.subscription_name == "":
            status = {"status": "Error", "message": "Name is mandatory"}
            flag = 1
        if user_data.subscription_validity == "":
            status = {"status": "Error", "message": "Validity is mandatory"}
            flag = 1
        if user_data.subscription_features == "":
            status = {"status": "Error", "message": "Features cannot be empty"}
            flag = 1
        if user_data.subscription_TotTelMedCalls == "":
            status = {"status": "Error", "message": "Value to 'Total Tele Medicine Call' is mandatory"}
            flag = 1
        if user_data.subscription_TotAlertCalls == "":
            status = {"status": "Error", "message": "Value to 'Total Alert Calls' is mandatory"}
            flag = 1
        if flag == 0:
            try:
                entries = db.insert('tbl_subscriptionplan',
                                    subscription_id=user_data.subscription_id,
                                    subscription_name=user_data.subscription_name, \
                                    subscription_validity=user_data.subscription_validity, \
                                    subscription_features=user_data.subscription_features, \
                                    subscription_TotTelMedCalls=user_data.subscription_TotTelMedCalls, \
                                    subscription_TotAlertCalls=user_data.subscription_TotAlertCalls \
                    )
            except Exception as e:
                return e
            else:
                status = {"status": "Sucess", "message": "Subscription Plan Added"}
                return json.dumps(status)
        else:
            return json.dumps(status)

class updatesubsciption:

    def GET(self):
         status = {"status": "Info", "message":"This page is intentionally left blank."}
         return json.dumps(status)

    def POST(self):
        user_data = web.input()
        flag = 0
        if user_data.subscription_name == "":
            status = {"status": "Error", "message": "Name is mandatory"}
            flag = 1
        if user_data.subscription_validity == "":
            status = {"status": "Error", "message": "Validity is mandatory"}
            flag = 1
        if user_data.subscription_features == "":
            status = {"status": "Error", "message": "Features cannot be empty"}
            flag = 1
        if user_data.subscription_TotTelMedCalls == "":
            status = {"status": "Error", "message": "Value to 'Total Tele Medicine Call' is mandatory"}
            flag = 1
        if user_data.subscription_TotAlertCalls == "":
            status = {"status": "Error", "message": "Value to 'Total Alert Calls' is mandatory"}
            flag = 1
        if flag == 0:
            try:
                k = subscription_id = user_data.subscription_id
                entries = db.update('tbl_subscriptionplan',
                                    subscription_name=user_data.subscription_name,\
                                    subscription_validity=user_data.subscription_validity, \
                                    subscription_features=user_data.subscription_features, \
                                    subscription_TotTelMedCalls=user_data.subscription_TotTelMedCalls, \
                                    subscription_TotAlertCalls=user_data.subscription_TotAlertCalls \
                                    , where=k)
            except Exception as e:
                return e
            else:
                status = {"status": "Sucess", "message": "Subscription Plan updated"}
                return json.dumps(status)
        else:
            return json.dumps(status)

class deletesubscription:
    def GET(self):
         status = {"status": "Info", "message":"This page is intentionally left blank."}
         return json.dumps(status)

    def POST(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        sub_data = web.input()
        try:
            k = "subscription_id=" + sub_data.id
            db.delete('tbl_subscriptionplan', where=k)
        except Exception as e:
            status = {"status": "Error", "message": e}
            return json.dumps(status)
        else:
            status = {"status": "Sucess", "message": "Subscription deleted"}
            return json.dumps(status)

class emergency:

    def GET(self):
        user_data = web.input()
        k='emergency_type='+user_data.typeid
        entries = db.select('tbl_emergency',where=k)
        rows = entries.list();
        JArray = "{"
        if rows:
            for row in rows:
                JArray += "{"
                JArray += "id:" + str(row['emergency_id'])
                JArray += ",Name:" + row['emergency_name']
                JArray += ",Type:" + str(row['emergency_type'])
                JArray += ",Latitude:" + row['emergency_lat']
                JArray += ",Longitude:" + row['emergency_lon']
                JArray += ",Phone:" + str(row['emergency_phone'])
                JArray += ",Address:" + str(row['emergency_address'])
                JArray += "},"
            JArray += "}"
            return json.dumps(JArray)
    def POST(self):
         ComFnObj = Commonfunctions()
         user_data = web.input()
         try:
            entries = db.insert('tbl_userprofile',\
                                    emergency_name=user_data.name, emergency_type=user_data.type, \
                                    emergency_lat=user_data.lat, emergency_lon=user_data.lon, \
                                   emergency_phone=user_data.phone, emergency_address=user_data.address, \

                    )
             #PUSH OTP
             #PUSH AUTHCODE
            salut = "Mr."
            if (user_data.gender == "female"):
                salut = "M/s"

            ComFnObj.SendMail(user_data.email, "support@igothelp.com", "Registration Complete", "Hello " + \
                                  salut + " " + user_data.lastname + "\n This is from support<DATA TO BE INSERTED HERE>")
            status = {"status": "Success", "message": "Update Successful"}
         except MySQLdb.IntegrityError, e:
            status = {"status": "Error", "message": "Phone Number already registered"}
         return json.dumps(status)

class deletecontact:
    def GET(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        user_data = web.input()
        if (ComFnObj.CheckAuth(user_data.AuthCode) == 0):
            status = {"status": "Error", "message": "AuthCode Failed"}
            return json.dumps(status)
        else:
            try:
                k = "contact_id=" + user_data.id
                print db.delete('tbl_contact', where=k)
            except Exception as e:
                status = {"status": "Error", "message": e}
                return json.dumps(status)
            else:
                status = {"status": "Sucess", "message": "Contact deleted"}
                return json.dumps(status)

class TeleConnectingIncoming:
    def GET(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        user_data = web.input()
        # NEED DATA FROM THE FRONT END TEAM

class TeleConnectComplete:
    #TeleConnectcomplete API call saves the connected number
    # of the doctor and update the Used TeleMed Call.
    def GET(self):
        user_data = web.input()
        ComFnObj = Commonfunctions()
        DoctorId=ComFnObj.GetIdFromPhone(user_data.DocNumber,"DOC")
        UserId=ComFnObj.GetIdFromPhone(user_data.UserNumber,"USR")
        try:
            entries = db.insert('tbl_telmedcall',
                                    user_id=UserId, \
                                    doctor_id=DoctorId, \
                                    call_date=user_data.date, \
                                    call_time=user_data.time, \
                                    status=user_data.status)
        except Exception as e:
            return e
        else:
            status = {"status": "Sucess", "message": "Call data Updates"}
            return json.dumps(status)

class CreateAlert:
    def GET(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        user_data = web.input()
        if (ComFnObj.CheckAuth(user_data.AuthCode) == 0):
            status = {"status": "Error", "message": "AuthCode Failed"}
            return json.dumps(status)
        else:
            EmrPhonenumber=ComFnObj.GetEmrContact(1, user_data.AuthCode, 2)

        Numbers=json.loads(EmrPhonenumber).split(',')
        Data=""
        for i in range(0,len(Numbers)-1):
            Number=Numbers[i].split(":")
            Data+=Number[1]+" sent to Knowlarity for calling\n" # HERE WILL HAVE THE ACTUAL API CALL TO KNOWLARITY
        return Data

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
