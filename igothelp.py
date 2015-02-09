import hashlib
import json
import smtplib
from datetime import datetime
import urllib
import re
import linecache
import sys
import MySQLdb
import collections
import web
import random
import time
import dicttoxml
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring, Element


urls = (
    '/', 'index',
    '/login', 'login',
    '/register', 'register',
    '/checkregistration', 'checkregistration',
    '/verify', 'verify',
    '/usersubscribe', 'usersubscribe',
    '/updateuserprofile', 'updateuserprofile',

    '/doctor', 'doctor',
    '/category', 'category',

    '/subscription', 'subscription',
    '/updatesubsciption', 'updatesubsciption',
    '/deletesubscription', 'deletesubscription',


    '/emergencycontact', 'emergencycontact',
    '/deletecontact', 'deletecontact',

    '/TeleConnectingIncoming','TeleConnectingIncoming',
    '/getcustomerdetails','getcustomerdetails',
    '/raise_alert_mobile','raise_alert_mobile',
    '/TeleConnectComplete','TeleConnectComplete',
    '/CreateAlert', 'CreateAlert',
    '/emergency', 'emergency',
    '/test', 'test',
)

# Server and Local have the same login credential
db = web.database(dbn='mysql', user='root', pw='igothelp2015', db='igothelp2015')




class index:
    def GET(self):
        status = {"status": "Info", "message": "This page is intentionally left blank.","statusCode":121}
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return  json.dumps(status)


class test:
    def POST(self):
        i = web.input()
        return i.Phone

    def GET(self):
        ComFnObj = Commonfunctions()
        #return ComFnObj.GetAuthFromId(1)
        return ComFnObj.CheckAuth("da1d8bbf3813e86e290f70b8f294bef0")



#FOR REUSABLE FUNCTIONS
class Commonfunctions:


    def LogError(self, message, APICall, LineNo):
        try:
            now = datetime.now()
            date = str(now.year)+"-"+str(now.month)+"-"+str(now.day)+" "
            time = str(now.hour)+":"+str(now.minute)+":"+str(now.second)
            entries = db.insert('errorLog', time=date+time,API=APICall,\
                                        lineNumber=LineNo,details=str(message))
        except:
            pass


    def SMSEmailLog(self,To,From,Type,API,Message):
        #try:
              db.insert('smsEmailLog',recepient=To,frm=From,details=Type,apiCall=API,message=Message)

        #except:
        #    self.PrintException("SMSEMailLog")


    def PrintException(self,API):
        try:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            print exc_obj
            line = linecache.getline(filename, lineno, f.f_globals)
            linepart=line.strip()
            #linePart="".join(linePart)
            msg=str(exc_obj)+"[" + linepart + "...]"
            return self.LogError(msg,API,lineno)#
        except:
            pass

    def SendSMS(self, To, Msg):
        URL = "http://alerts.sinfini.com/api/web2sms.php?workingkey=663040hvmlrbxmd00792&to=" + str(
            To) + "&sender=GOTHLP&message=" + Msg
        response = urllib.urlopen(URL)
        return response

    def GetAuthFromId(self, Id):
        k = "user_id='" + Id + "'"
        entries = db.select('userProfile', what='user_authcode', where=k)
        rows = entries.list();
        if rows:
            return rows[0]['user_authcode']
        else:
            status = {"status": "Error", "message": "ID is not associated with any User","statusCode":500,"success":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

    def GetIdFromAuth(self, AuthCode):
        k = "user_authcode='" + AuthCode + "'"
        entries = db.select('userProfile', what='user_id', where=k)
        rows = entries.list();
        if rows:
            return rows[0]['user_id']
        else:
            status = {"status": "Error", "message": "AuthCode is not associated with any User","statusCode":500,"success":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

    def GetIdFromPhone(self, Number, Type):  #Type= 'USR' for User and 'DOC for Doctor'
        if Type == "USR":
            k = "user_phone='" + Number + "'"
            table = "userProfile"
            What = "user_id"
        else:
            k = "doctor_phone='" + Number + "'"
            table = "Doctor"
            What = "doctor_id"

        entries = db.select(table, what=What, where=k)
        rows = entries.list();
        if rows:
            return rows[0][What]
        else:
            status = {"status": "Info", "message": "Nothing Found","statusCode":121,"success":True}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

    def CheckAuth(self, AuthCode):
        #try:
            print "Authcode Passed",str(AuthCode)
            k = "user_authcode='" + str(AuthCode) + "'"
            entries = db.select('userProfile', where=k)
            rows = entries.list();
            if rows:
                for row in rows:
                    JArray2={"id":str(row['user_id']),\
                         "firstname":row['user_firstname'],\
                         "lastname":row['user_lastname'],\
                         "phone":row['user_phone'],\
                         "email":row['user_email'],\
                         "dob":row['user_dob'],\
                         "gender":row['user_gender'],\
                         "bloodgroup":row['user_bloodgroup'],\
                         "authcode":row['user_authcode'],\
                         "lat":row['user_lat'],\
                         "lon":row['user_lon']}
                return json.dumps(JArray2)
            else:
                return 0
        #except Exception as e:
        #    return e;

    def SendMail(self, To, From, Subject, Body):
        try:
            web.config.smtp_server = 'smtp.gmail.com'
            web.config.smtp_port = 587
            web.config.smtp_username = 'abhilash.c@spurtreetech.com'
            web.config.smtp_password = 'Ab4i7@$h'
            web.config.smtp_starttls = True
            web.sendmail(To, From, Subject, Body)
            status = {"status": "Sucess", "message": "Mail Sent","statusCode":200,"MailSent":True}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)
        except smtplib.SMTPAuthenticationError:
            status = {"status": "Error", "message": "Authentication Error","statusCode":500,"MailSent":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

        except Exception as e:
            self.PrintException("Mail Sent Function")
            status = {"status": "Error", "message": "Error Try Later","statusCode":str(e)}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

    def GetSubPlanDetails(self,SubId):
        try:

            k = "subscription_id=" + SubId + ""
            entries = db.select('subscriptionPlan', where=k)
            rows = entries.list();
            JResponse = collections.OrderedDict()
            if rows:
                for row in rows:
                    JArray2={"id":str(row['subscription_id']),\
                         "Name":row['subscription_name'],\
                         "Validity":row['subscription_validity'],\
                         "Features":row['subscription_features'],\
                         "TAC":row['subscription_TotAlertCalls'],\
                         "TMC":row['subscription_TotTelMedCalls'],\
                         "Price":row['subscription_price']}

                JResponse["SubscriptionData"]=JArray2
                JResponse["status"] = "success"
                JResponse["statuscode"]=777
                JResponse["message"] ="Successfully retrieved results"
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(JResponse)
            else:
                return 0
        except Exception as e:
            return e;

    def GetEmrContact(self, Opt, Incoming, Type):
        # Opt will tell the fuction should return number only
        # or the entire data
        # Incoming can be both Authcode or Phone Number
        # Type will determine which one
        k = "Dummy"
        JResponse = collections.OrderedDict()

        if Type == 1:
            k = "user_phone='" + str(Incoming) + "'"
            TypeStr = "Phone Number"
        elif Type == 2:
            k = "user_authcode='" + str(Incoming) + "'"
            TypeStr = "AuthCode"
        else:
            status = {"status": "Syntax Error", "message": "Type should be 1 or 2","statusCode":101}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)


        entries = db.select('userProfile', what='user_id', where=k)
        rows = entries.list();
        if rows:
            User_Id = rows[0]['user_id']
        else:
            status = {"status": "Info", "message": "No user with this " + TypeStr,"statusCode":121,"success":True}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)



        entries2="Dummy"
        if Opt == 1:  # RETURN ONLY PHONE NUMBER OF THE CONTACT
            entries2 = db.select('emergencyContact', what='contact_phone', where="user_id=" + str(User_Id))
            rows2 = entries2.list()
            Cnt = 0
            JArray=[]
            if rows2:
                for row in rows2:
                    JArray.append(row['contact_phone'])

                JResponse["EmrList"]=JArray
                JResponse["status"] = "success"
                JResponse["statuscode"]=777
                JResponse["message"] ="Successfully retrieved results"
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(JResponse)

            else:
                    status = {"status": "Info", "message": "No Emergency Contact added for this user","statusCode":121,"success":True}
                    web.header('Access-Control-Allow-Origin', '*')
                    web.header('Access-Control-Allow-Methods', '*')
                    web.header('Access-Control-Allow-Headers', '*')
                    web.header('Content-Type', 'application/json')
                    return  json.dumps(status)
        elif Opt == 2:  # RETRUN ALL THE DETAILS OF A CONTACT
            entries2 = db.select('emergencyContact', where="user_id=" + str(User_Id))
            rows2 = entries2.list()
            JArray = []
            if rows2:
                for row in rows2:
                    JArray2 = collections.OrderedDict()
                    JArray2["id"]=str(row['contact_id'])
                    JArray2["name"]=row['contact_name']
                    JArray2["phone"]=row['contact_phone']
                    JArray2["email"]=row['contact_email']
                    JArray.append(JArray2)
                JResponse["EmrList"]=JArray
                JResponse["status"] = "success"
                JResponse["statuscode"]=777
                JResponse["message"] ="Successfully retrieved results"
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(JResponse)
            else:
                status = {"status": "Info", "message": "No Emergency Contact added for this user","statusCode":121,"success":True}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
        else:
            status = {"status": "Syntax Error", "message": "Opt should be 1 or 2","statusCode":101}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)


        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return json.dumps(JArray)


    def GenerateOTP(self,Phone,Count=4):
        m = hashlib.md5()
        now = datetime.now()
        mm = str(now.month)
        ss = str(now.second)
        rd=random.random()*1000
        Gen = str(Phone) + mm + ss+str(rd)
        m.update(Gen)
        Plain = m.hexdigest()
        k = re.findall(r'\d+', Plain)
        return "".join(k)[:Count]


class checkregistration:
    def GET(self):

        status = {"status": "Info", "message": "This page is intentionally left blank.","statusCode":121,"success":True}
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return  json.dumps(status)


    def POST(self):
        ComFnObj = Commonfunctions()
        data = web.input(Phone='')
        print data
        try:
            k = "user_phone='" + data.Phone + "'"
            entries = db.select('userProfile', what='user_authcode', where=k)
            rows = entries.list();
            if rows:
                OTP = ComFnObj.GenerateOTP(data.Phone,4)
                Message = "Please verify your phone number using this OTP " + str(OTP)

                Id = ComFnObj.GetIdFromPhone(data.Phone, "USR")
                Auth=ComFnObj.GetAuthFromId(str(Id))
                user_data=json.loads(ComFnObj.CheckAuth(Auth))
                print user_data
                salut = "Mr."
                if (user_data["gender"] == "female"):
                    salut = "M/s."
                print salut
                ComFnObj.SendSMS(user_data["phone"], Message)
                ComFnObj.SMSEmailLog(user_data["phone"],"IGOTHELP","SMS","checkregistration","Message")
                Body= "Hello "+salut + user_data["lastname"] + "\n This is from support<DATA TO BE INSERTED HERE>\n" \
                                                                         "Your OTP is:"+str(OTP)+"\n Thank you"
                print ComFnObj.SendMail(user_data["email"],"support@igothelp.com", "IgotHelp-Phone Verification",Body)
                ComFnObj.SMSEmailLog(user_data["phone"],"IGOTHELP","MAIL","checkregistration",Message)
                entries = db.insert('userOTP', user_id=int(Id), otp=OTP)
                status = {"status": "Success", "message": "OTP Send","isExistingCustomer":True,"statusCode":777}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)

            else:
                status = {"status": "Success", "message": "User registration required","isExistingCustomer":False,"statusCode":777}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header("Access-Control-Allow-Headers", '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)

        except Exception as e:
            ComFnObj.PrintException("checkregisteration")
            status = {"status": "Error", "message": "Error Try Later","statusCode":str(e)}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)
class verify:
    def GET(self):
        status = {"status": "Info", "message": "This page is intentionally left blank.","statusCode":121}
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return  json.dumps(status)
    def POST(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        try:
            print user_data
            Id = ComFnObj.GetIdFromPhone(user_data.Phone, "USR")
            print Id
            k = "userProfile.user_id=userOTP.user_id and userOTP.user_id='" + str(Id) + "' and OTP='" + user_data.OTP + "'"
            entries = db.select('userOTP,userProfile', what='user_authcode,userProfile.user_id', where=k)
            rows = entries.list();
            if rows:
                row=rows[0]
                JArray = {"status": "Success", "message": "Verification Success",\
                              "isVerified":True,"statusCode":777,"Authcode:":row['user_authcode'],\
                            "success":True}
                k = "userOTP.user_id='" + str(Id) + "' and otp='" + user_data.OTP + "'"
                db.delete('userOTP', where=k)

                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return json.dumps(JArray)
    
            else:
                status = {"status": "Failed", "message": "Phone Verification Failed","statusCode":500,"success":False}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
        except Exception as e:
                status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
                ComFnObj.PrintException("Verify")
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)

class register:
    def GET(self):
        ComFnObj = Commonfunctions()
        status = {"status": "Info", "message": "This page is intentionally left blank.","statusCode":121,"success":True}
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return  json.dumps(status)


    def POST(self):
        try:
            ComFnObj = Commonfunctions()
            # user_data = json.loads(json_input)
            user_data = web.input()
            flag = 0
            if user_data.firstname == "":
                status = {"status": "Error", "message": "First name is mandatory","statusCode":500,"success":False}
                flag = 1
            if user_data.lastname == "":
                status = {"status": "Error", "message": "Last name is mandatory","statusCode":500,"success":False}
                flag = 1
            if user_data.dob == "":
                status = {"status": "Error", "message": "Date of Birth is mandatory","statusCode":500,"success":False}
                flag = 1
            if user_data.bloodgroup == "":
                status = {"status": "Error", "message": "Blood Group is mandatory","statusCode":500,"success":False}
                flag = 1
            if user_data.gender == "":
                status = {"status": "Error", "message": "Gender is mandatory","statusCode":500,"success":False}
                flag = 1
            if user_data.email == "":
                status = {"status": "Error", "message": "Email ID is mandatory","statusCode":500,"success":False}
                flag = 1
            if user_data.phone == "":
                status = {"status": "Error", "message": "Phone number is mandatory","statusCode":500,"success":False}
                flag = 1
            if flag == 0:
                Salt = "$343dddSS"
                String = user_data.firstname + user_data.phone + Salt
                m = hashlib.md5()
                m.update(String)
                Authcode = m.hexdigest()
                OTP = ComFnObj.GenerateOTP(user_data.phone,4)
                print OTP


                entries = db.insert('userProfile', user_firstname=user_data.firstname, \
                                    user_lastname=user_data.lastname, user_phone=user_data.phone, \
                                    user_email=user_data.email, user_dob=user_data.dob, \
                                    user_gender=user_data.gender, user_bloodgroup=user_data.bloodgroup, \
                                    user_authcode=Authcode \
                    )
                Id=ComFnObj.GetIdFromPhone(user_data.phone,"USR")
                entries = db.insert('userOTP', user_id=Id, OTP=OTP)
                Message = "Please verify your phone number using this OTP " + OTP
                ComFnObj.SendSMS(user_data.phone, Message)
                salut = "Mr."
                if (user_data.gender == "female"):
                    salut = "M/s"

                ComFnObj.SendMail(user_data.email, "support@igothelp.com", "Registration Complete", "Hello " + \
                                      salut + " " + user_data.lastname + "\n This is from support<DATA TO BE INSERTED HERE>")
                status = {"status": "Success", "message": "Update Successful","statusCode":777,"success":True}
                return  json.dumps(status)
        except MySQLdb.IntegrityError, e:
                found,found2=0,0
                m = re.search('(user_phone.*)', str(e))
                if m:
                    found = 1
                    status = {"status": "Error", "message": "Phone Number already registered","statusCode":500,"success":False}
                else:
                    found = 0

                m = re.search('(user_email.*)', str(e))
                if m:
                    found2 = 1
                    status = {"status": "Error", "message": "Email already registered","statusCode":500,"success":False}
                else:
                    found2=0
                if found==0 and found2==0:
                    status = {"status": "Error", "message": "Some Error Happened","statusCode":600,"success":False}

                ComFnObj.PrintException("Register")
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)

        except Exception as e:
            status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
            ComFnObj.PrintException("Register")
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)
        else:
             web.header('Access-Control-Allow-Origin', '*')
             web.header('Access-Control-Allow-Methods', '*')
             web.header('Access-Control-Allow-Headers', '*')
             web.header('Content-Type', 'application/json')
             return  json.dumps(status)

class login:
    def GET(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        print user_data.Phone
        status = {"status": "Info", "message": "This page is intentionally left blank.","statusCode":121,"success":True}
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return  json.dumps(status)


    def POST(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        header = web.ctx.environ
        Authcode = header.get('HTTP_AUTHCODE')
        try:
            flag = 0
            Id1 = ComFnObj.GetIdFromPhone(user_data.Phone, "USR")
            Id2 = ComFnObj.GetIdFromAuth(Authcode)
            if (Id1 != Id2):
                status = {"status": "Sucess", "message": "Login Sucess", "Authcode": Authcode,"statusCode":777,"success":True}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
            else:
                status = {"status": "Error", "message": "Login Failed","statusCode":500,"success":True}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
        except:
            ComFnObj.PrintException("Login")
            status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

class usersubscribe:
    def GET(self):
        status = {"status": "Info", "message": "This page is intentionally left blank.","statusCode":121,"success":True}
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return  json.dumps(status)


    def POST(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        header = web.ctx.environ

        authcode = header.get('HTTP_AUTHCODE')
        flag = 0
        if (ComFnObj.CheckAuth(authcode) == 0):
            status = {"status": "Error", "message": "AuthCode Failed","statusCode":500,"success":True}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)
        else:
            try:
                SubData=json.loads(ComFnObj.GetSubPlanDetails(user_data.subid))
                #return SubData["SubscriptionData"]["Validity"]
                StrDt=time.strftime("%d/%m/%Y")
                EndDt=time.strftime("%d/%m/")+str(  int(time.strftime("%Y")) + int(SubData["SubscriptionData"]["Validity"]) )

                #EndDt =datetime(Time, *St.timetuple()[1:-2])
                entries = db.insert('userSubscriptionPlan',user_id=int(ComFnObj.GetIdFromAuth(authcode))\
                                    ,subscription_id=int(user_data.subid),subscription_startdate=str(StrDt)\
                                    ,subscription_enddate=str(EndDt),user_usedTelMedCalls=0\
                                    ,user_usedAlertCalls=0 ,user_pendingTelMedCalls=int(SubData["SubscriptionData"]["TMC"])\
                                    ,user_pending_AlertCalls=int(SubData["SubscriptionData"]["TAC"]) ,userPayment_ID=int(user_data.PayId)\
                                    ,is_active=1
                                    )
                status = {"status": "Success", "message": "Subscribed Successfully","statusCode":777,"success":True}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)

            except Exception as e:
                print e
                status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
                ComFnObj.PrintException("usersubscribe")
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)


class updateuserprofile:
    def GET(self):
        status = {"status": "Info", "message": "This page is intentionally left blank.","statusCode":121,"success":True}
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return  json.dumps(status)


    def POST(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        header = web.ctx.environ
        authcode = header.get('HTTP_AUTHCODE')
        flag = 0
        if (ComFnObj.CheckAuth(authcode) == 0):
            status = {"status": "Error", "message": "AuthCode Failed","statusCode":500,"success":True}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)


        if user_data.firstname == "":
            status = {"status": "Error", "message": "First name is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.lastname == "":
            status = {"status": "Error", "message": "Last name is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.dob == "":
            status = {"status": "Error", "message": "Date of Birth is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.bloodgroup == "":
            status = {"status": "Error", "message": "Blood Group is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.gender == "":
            status = {"status": "Error", "message": "Gender is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.email == "":
            status = {"status": "Error", "message": "Email ID is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.phone == "":
            status = {"status": "Error", "message": "Phone number is mandatory","statusCode":500,"success":False}
            flag = 1
        if flag == 0:
            try:
                k = user_id = user_data.id
                entries = db.update('userProfile', user_firstname=user_data.firstname, \
                                    user_lastname=user_data.lastname, user_phone=user_data.phone, \
                                    user_email=user_data.email, user_dob=user_data.dob, \
                                    user_gender=user_data.gender, user_bloodgroup=user_data.bloodgroup \
                                    , where=k)
                #PUSH OTP
                #PUSH AUTHCODE
                status = {"status": "Success", "message": "Update Successful","statusCode":777,"success":True}
            except MySQLdb.IntegrityError, e:
                ComFnObj.PrintException("UpdateProfile")
                status = {"status": "Error", "message": "Phone Number already registered","statusCode":500,"success":False}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
        else:
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

class doctor:
    def GET(self):
        ComFnObj = Commonfunctions()
        JResponse = collections.OrderedDict()
        user_data = web.input(availability=0,category=0,docid=0)
        try:
            user_data.list
            QueryTypes = "SELECT * FROM `doctorcatagory` "
            entriesType = db.query(QueryTypes)
            rowsTypes = entriesType.list();
            if rowsTypes:
                JArrayTypes = []
                for rowType in rowsTypes:
                    JArrayType = collections.OrderedDict()
                    JArrayType["id"]= str(rowType['id'])
                    JArrayType["catagoryname"]= str(rowType['catagoryname'])
                    JArrayTypes.append(JArrayType)
                JResponse["categorytypes"] = JArrayTypes
                JResponse["status"] = "success"
                JResponse["statuscode"]=777
                JResponse["message"] ="Successfully retrieved results"
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(JResponse)
        except:
            pass
        if user_data.availability>0:
            wherepart="doctor_availability=1"
        else:
            wherepart=''

        if user_data.category >0 :
            if(len(wherepart)>0):
                putand=' and '
            else:
                putand=''
            wherepart+=putand+"doctor_specialization="+user_data.category
        else:
           pass

        if user_data.docid>0:
            if(len(wherepart)>0):
                putand=' and '
            else:
                putand=''
            wherepart+=putand+"doctor_id="+user_data.docid
        else:
          pass
        if wherepart=='':
            status = {"status": "Error", "message": "API Call Incorrect","statusCode":101,"success":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)
        try:
            entries = db.select('Doctor',where=wherepart)
            rows = entries.list();
            QueryTypes = "SELECT * FROM `doctorcatagory` "
            entriesType = db.query(QueryTypes)
            rowsTypes = entriesType.list();
            if rowsTypes:
                JArrayTypes = []
                for rowType in rowsTypes:
                    JArrayType = collections.OrderedDict()
                    JArrayType["id"]= str(rowType['id'])
                    JArrayType["catagoryname"]= str(rowType['catagoryname'])
                    JArrayTypes.append(JArrayType)
                    JResponse["categorytypes"] = JArrayTypes

            JArray = []
            if rows:
                for row in rows:
                    JArray2 = collections.OrderedDict()
                    JArray2["id"]=str(row['doctor_id'])
                    JArray2["Firstname"]=row['doctor_firstname']
                    JArray2["Lastname"]=row['doctor_lastname']
                    JArray2["Available"]=str(row['doctor_availability'])
                    JArray2["Catagory"]=str(row['doctor_specialization'])
                    JArray2["Qualification"]=str(row['doctor_qualification'])
                    JArray2["Phone"]=str(row['doctor_phone'])
                    JArray2["Gender"]=str(row['doctor_gender'])
                    JArray2["Email"]=str(row['doctor_email'])
                    JArray2["AttendedCalls"]=str(row['doctor_attendedcall'])
                    JArray.append(JArray2)

                JResponse["DoctorList"] = JArray
                JResponse["status"] = "success"
                JResponse["statuscode"]=777
                JResponse["message"] ="Successfully retrieved results"
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')

                return json.dumps(JResponse)
            else:
                status = {"status": "Sucess", "message": "No record found","statusCode":777,"success":True}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
        except Exception as e:
            print e
            #status = {"status": "Error", "message": "Error Try Later","statusCode":600}
            status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
            ComFnObj.PrintException("Doctor")
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)
    def POST(self):
        ComFnObj = Commonfunctions()
        # doctor_data = json.loads(json_input)
        doctor_data = web.input()
        flag = 0
        if doctor_data.firstname == "":
            status = {"status": "Error", "message": "First name is mandatory","statusCode":500,"success":False}
            flag = 1
        if doctor_data.lastname == "":
            status = {"status": "Error", "message": "Last name is mandatory","statusCode":500,"success":False}
            flag = 1

        if doctor_data.specialisation == "":
            status = {"status": "Error", "message": "specialisation is mandatory","statusCode":500,"success":False}
            flag = 1
        if doctor_data.qualification == "":
            status = {"status": "Error", "message": "Qualification is mandatory","statusCode":500,"success":False}
            flag = 1
        if doctor_data.gender == "":
            status = {"status": "Error", "message": "Gender is mandatory","statusCode":500,"success":False}
            flag = 1
        if doctor_data.email == "":
            status = {"status": "Error", "message": "Email ID is mandatory","statusCode":500,"success":False}
            flag = 1
        if doctor_data.phone == "":
            status = {"status": "Error", "message": "Phone number is mandatory","statusCode":500,"success":False}
            flag = 1
        if flag == 0:
            Salt = "$343dddSS"
            String = doctor_data.firstname + doctor_data.phone + Salt
            m = hashlib.md5()
            m.update(String)
            Authcode = m.hexdigest()
            try:
                entries = db.insert('Doctor', doctor_firstname=doctor_data.firstname, \
                                    doctor_lastname=doctor_data.lastname, doctor_phone=doctor_data.phone, \
                                    doctor_email=doctor_data.email, doctor_specialization=doctor_data.specialisation, \
                                    doctor_availability=0, doctor_qualification=doctor_data.qualification, \
                                    doctor_attendedcall=0, doctor_authcode=Authcode \
                    )
                OTP = ComFnObj.GenerateOTP(doctor_data.Phone)
                Message = "Please verify your phone number using this OTP " + OTP
                ComFnObj.SendSMS(doctor_data.Phone, Message)
                entries = db.insert('doctorOTP', phonenumber=doctor_data.Phone, otp=OTP)
                salut = "Mr."
                if (doctor_data.gender == "female"):
                    salut = "M/s"

                ComFnObj.SendMail(doctor_data.email, "support@igothelp.com", "Registration Complete", "Hello " + \
                                  salut + " " + doctor_data.lastname + "\n This is from support<DATA TO BE INSERTED HERE>")
                status = {"status": "Success", "message": "Update Successful","statusCode":777,"success":True}
            except MySQLdb.IntegrityError, e:
                status = {"status": "Error", "message": "Phone Number already registered","statusCode":500,"success":False}
                ComFnObj.PrintException("Doctor")
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)

            except:
                status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
                ComFnObj.PrintException("Doctor")
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
            else:
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)


class category:
    def GET(self):
        ComFnObj = Commonfunctions()
        entries = db.select('doctorcatagory')
        rows = entries.list();
        JArray = "{"
        if rows:
            JArray = []
            for row in rows:
                JArray2 = collections.OrderedDict()
                JArray2["id"]= str(row['id'])
                JArray2["Name"]= row['catagoryname']
                JArray.append(JArray2)
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return json.dumps(JArray)


    def POST(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        flag = 0
        if user_data._name == "":
            status = {"status": "Error", "message": "Name is mandatory","statusCode":500,"success":False}
            flag = 1
            return  json.dumps(status)
        try:
            entries = db.insert('doctorcatagory',

                                    catagoryname=user_data._name, \

                    )
        except Exception as e:
                ComFnObj.PrintException("DoctorCatagory")
                status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
        else:
                status = {"status": "Sucess", "message": " Category Added","statusCode":777,"success":True}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)




class subscription:
    def GET(self):
        ComFnObj = Commonfunctions()
        entries = db.select('subscriptionPlan')
        rows = entries.list();
        JResponse = collections.OrderedDict()
        JArray = []
        if rows:
            for row in rows:
                JArray2 = collections.OrderedDict()
                JArray2["id"]= str(row['subscription_id'])
                JArray2["Name"]= row['subscription_name']
                JArray2["Validity"]= str(row['subscription_validity'])
                JArray2["Features"]= row['subscription_features']
                JArray2["Total_TeleMedCalls"]= str(row['subscription_TotTelMedCalls'])
                JArray2["Total_AlertCalls"]= str(row['subscription_TotAlertCalls'])
                JArray2["Price"]= str(row['subscription_price'])
                JArray.append(JArray2)
            JResponse["subscriptionPlan"]=JArray
            JResponse["status"] = "success"
            JResponse["statuscode"]=777
            JResponse["message"] ="Successfully retrieved results"

            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return json.dumps(JResponse)
        else:

            JResponse["status"] = "success"
            JResponse["statuscode"]=777
            JResponse["message"] ="No record Found"

            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return json.dumps(JResponse)

    def POST(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        flag = 0
        if user_data.name == "":
            status = {"status": "Error", "message": "Name is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.validity == "":
            status = {"status": "Error", "message": "Validity is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.features == "":
            status = {"status": "Error", "message": "Features cannot be empty","statusCode":500,"success":False}
            flag = 1
        if user_data.TotTelMedCalls == "":
            status = {"status": "Error", "message": "Value to 'Total Tele Medicine Call' is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.TotAlertCalls == "":
            status = {"status": "Error", "message": "Value to 'Total Alert Calls' is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.price == "":
            status = {"status": "Error", "message": "Price is mandatory","statusCode":500,"success":False}
            flag = 1
        if flag == 0:
            try:
                entries = db.insert('subscriptionPlan',

                                    subscription_name=user_data.name, \
                                    subscription_validity=user_data.validity, \
                                    subscription_features=user_data.features, \
                                    subscription_TotTelMedCalls=user_data.TotTelMedCalls, \
                                    subscription_TotAlertCalls=user_data.TotAlertCalls, \
                                    subscription_price=user_data.price \
                    )
            except Exception as e:
                ComFnObj.PrintException("Subscription")
                status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
            else:
                status = {"status": "Sucess", "message": "Subscription Plan Added","statusCode":777,"success":True}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)

        else:
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)


class updatesubsciption:
    def GET(self):
        ComFnObj = Commonfunctions()
        status = {"status": "Info", "message": "This page is intentionally left blank.","statusCode":121,"success":True}
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return  json.dumps(status)


    def POST(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        flag = 0
        if user_data.subscription_name == "":
            status = {"status": "Error", "message": "Name is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.subscription_validity == "":
            status = {"status": "Error", "message": "Validity is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.subscription_features == "":
            status = {"status": "Error", "message": "Features cannot be empty","statusCode":500,"success":False}
            flag = 1
        if user_data.subscription_TotTelMedCalls == "":
            status = {"status": "Error", "message": "Value to 'Total Tele Medicine Call' is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.subscription_TotAlertCalls == "":
            status = {"status": "Error", "message": "Value to 'Total Alert Calls' is mandatory","statusCode":500,"success":False}
            flag = 1
        if user_data.subscription_price == "":
            status = {"status": "Error", "message": "Price is mandatory","statusCode":500,"success":False}
            flag = 1
        if flag == 0:
            try:
                k = subscription_id = user_data.subscription_id
                entries = db.update('subscriptionPlan',
                                    subscription_name=user_data.subscription_name, \
                                    subscription_validity=user_data.subscription_validity, \
                                    subscription_features=user_data.subscription_features, \
                                    subscription_TotTelMedCalls=user_data.subscription_TotTelMedCalls, \
                                    subscription_TotAlertCalls=user_data.subscription_TotAlertCalls, \
                                    subscription_price=user_data.subscription_price \
                                    , where=k)
            except Exception as e:
                ComFnObj.PrintException("UpdateSubscription")
                status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
            else:
                status = {"status": "Sucess", "message": "Subscription Plan updated","statusCode":777,"success":False}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)

        else:
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)


class deletesubscription:
    def GET(self):
        ComFnObj = Commonfunctions()
        status = {"status": "Info", "message": "This page is intentionally left blank.","statusCode":121,"success":False}
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Methods', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Content-Type', 'application/json')
        return  json.dumps(status)


    def POST(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        sub_data = web.input()
        try:
            k = "subscription_id=" + sub_data.id
            db.delete('subscriptionPlan', where=k)
        except Exception as e:
            ComFnObj.PrintException("Delete Subscription")
            status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

        else:
            status = {"status": "Sucess", "message": "Subscription deleted","statusCode":777,"success":True}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)


class emergency:
    def GET(self):
        ComFnObj = Commonfunctions()
        user_data = web.input(rad=5)

        JResponse = collections.OrderedDict()

        #Using Haversine formula
        QueryTypes = "SELECT * FROM `emergencyType` "
        entriesType = db.query(QueryTypes)
        rowsTypes = entriesType.list();
        if rowsTypes:
            JArrayTypes = []
            for rowType in rowsTypes:
                JArrayType = collections.OrderedDict()
                JArrayType["id"]= str(rowType['emergency_type_id'])
                JArrayType["typename"]= str(rowType['emergency_type_name'])
                JArrayTypes.append(JArrayType)
            JResponse["emergencytypes"] = JArrayTypes

        Query="SELECT *,round(2*atan(sqrt(pow(sin(radians(("+user_data.lat+"- emergency_lat)/2)),2)+\
                cos(radians(emergency_lat))*cos(radians("+user_data.lat+"))*\
                pow(sin(radians(("+user_data.lon+"5-emergency_lon ) ) /2 ) , 2 ) ) ,\
                 sqrt( 1 - pow( sin( radians( ( "+user_data.lat+" - emergency_lat ) /2 ) ) , 2 ) + \
                 cos( radians( emergency_lat ) ) * cos( radians( "+user_data.lat+" ) ) *\
                  pow( sin( radians( ( "+user_data.lon+" - emergency_lon ) ) /2 ) , 2 ) ) ) *6371,2)\
            as distance  FROM emergency HAVING \
    distance <= "+str(user_data.rad)+" ORDER BY distance ASC"
        entries = db.query(Query)


        rows = entries.list();
        if rows:
            JArray = []
            for row in rows:
                JArray2 = collections.OrderedDict()
                JArray2["id"]= str(row['emergency_id'])
                JArray2["Name"]= row['emergency_name']
                JArray2["Distance"]= row['distance']
                JArray2["Type"]= str(row['emergency_type'])
                JArray2["Latitude"]= row['emergency_lat']
                JArray2["Longitude"]= row['emergency_lon']
                JArray2["Phone"]= str(row['emergency_phone'])
                JArray2["Address"]= str(row['emergency_address'])
                JArray.append(JArray2)
            JResponse["emergencylist"] = JArray
            JResponse["status"] = "success"
            JResponse["statuscode"]=777
            JResponse["message"] ="Successfully retrieved results"
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return json.dumps(JResponse)


    def POST(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        try:
            entries = db.insert('emergency',\
                                emergency_name=user_data.name, emergency_type=user_data.type, \
                                emergency_lat=user_data.lat, emergency_lon=user_data.lon, \
                                emergency_phone=user_data.phone, emergency_address=user_data.address,)
            status = {"status": "Success", "message": "Update Successful"}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

        except Exception as e:
            ComFnObj.PrintException("Emergency")
            status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

class emergencycontact:
    def GET(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        header = web.ctx.environ
        authcode = header.get('HTTP_AUTHCODE',0)
        if (ComFnObj.CheckAuth(authcode) == 0):
            status = {"status": "Error", "message": "AuthCode Failed","success":False,"statuscode":500}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)
        else:
            return ComFnObj.GetEmrContact(2,authcode,2) # Returns All the data
    def POST(self):
        ComFnObj = Commonfunctions()
        user_data = web.input()
        header = web.ctx.environ
        try:
            authcode = header.get('HTTP_AUTHCODE',0)
            if (ComFnObj.CheckAuth(authcode) == 0):
                status = {"status": "Error", "message": "AuthCode Failed","success":False,"statuscode":500}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
            else:
                flag = 0
                if user_data.name == "":
                    status = {"status": "Error", "message": "Name is mandatory","statusCode":500,"success":False}
                    flag = 1
                if user_data.phone == "":
                    status = {"status": "Error", "message": "Phone number is mandatory","statusCode":500,"success":False}
                    flag = 1
                if user_data.email == "":
                    status = {"status": "Error", "message": "Email cannot be empty","statusCode":500,"success":False}
                    flag = 1
                if flag == 0:
                    Id=ComFnObj.GetIdFromAuth(authcode)
                    entries = db.insert('emergencyContact',
                                       contact_name=user_data.name,
                                   contact_phone=user_data.phone, \
                                   user_id=Id, \
                                    contact_email=user_data.email, \
                                      )
        except Exception as e:
                ComFnObj.PrintException("emergencyContact")
                status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
        else:
                status = {"status": "Sucess", "message": "Emergency contact added","statusCode":777,"success":True}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)


class deletecontact:
    def GET(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        user_data = web.input()
        header = web.ctx.environ
        authcode = header['HTTP_AUTHCODE']
        if (ComFnObj.CheckAuth(authcode) == 0):
            status = {"status": "Error", "message": "AuthCode Failed","success":True}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

        else:
            try:
                k = "contact_id=" + user_data.id
                print db.delete('emergencyContact', where=k)
            except Exception as e:
                ComFnObj.PrintException("Delete Contact")
                status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
            else:
                status = {"status": "Sucess", "message": "Contact deleted","statusCode":777,"success":True}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
#=======================FROM LAST VERSION============================
class raise_alert_mobile:

    def GET(self):
        #try:
            ComFnObj=Commonfunctions()
            data = web.input()
            header = web.ctx.environ
            authcode = header.get('HTTP_AUTHCODE',0)
            #authcode=
            if (ComFnObj.CheckAuth(authcode) == 0):
                status = {"status": "Error", "message": "AuthCode Failed","success":False,"statuscode":500}
                web.header('Access-Control-Allow-Origin', '*')
                web.header('Access-Control-Allow-Methods', '*')
                web.header('Access-Control-Allow-Headers', '*')
                web.header('Content-Type', 'application/json')
                return  json.dumps(status)
            else:
                """
                GOOGLE API FOR REVERSE ADDRESS LOOK UP
                """
                base = "http://maps.googleapis.com/maps/api/geocode/json?"
                params = "latlng={lat},{lon}&sensor={sen}".format(lat=data.lat,lon=data.long,sen='true')
                url = "{base}{params}".format(base=base, params=params)
                response = urllib.urlopen(url)

                RespJ=dict(json.loads(response.read())) # ALL THE ADDRESS IS COMING HERE

                Message="I need help,I am now in "
                if RespJ["status"]!=u'ZERO_RESULTS': # CHECKING FOR NULL RESULT
                   Address=RespJ["results"][0]["formatted_address"] # GETTIN THE FIRST FORMATED ADDRESS
                else:
                   Address="Latitude:"+str(data.lat),"Longitude:"+str(data.long) # ELSE SIMPLY PUSH THE CO-ORDINATES

        #SENDING SMS TO ALL EMR CONTACT
                Message=Message+str(Address)
                EmrContact=json.loads(ComFnObj.GetEmrContact(1,authcode,2))

                for Data in EmrContact["EmrList"]:
                   print "Sending Message to"+str(Data)
                   #print ComFnObj.SendSMS(str(Data),Message)
                   ComFnObj.SMSEmailLog(str(Data),"IGOTHELP","SMS","raise_alert_mobile",Message)
        #CREATE AN ALERT
                Id=ComFnObj.GetIdFromAuth(authcode)
                AlertID=1   # HARD CODED FOR SECURITY PART. MAY BE THERE WILL BE A CHANGE
                            # FOR FUTURE USE I HAVE PUT THAT IN A TABLE CALLED alerttype
                            # 1 is the ID for SECURITY
                Curdate=datetime.strftime("%d-%m-%Y")
                Curtime=datetime.strftime("%h-%i-%s")
                db.insert('alerts',user_id=Id,alert_type=AlertID,alert_lat=data.lat,alert_lon=data.lon, \
                    alert_date=Curdate,alert_time=Curtime,alert_status='Alert Raised',contacts='',connected_number='',call_status='')

        #HIT KOWLARITY WITH THE ALERT TYPE

                return EmrContact["EmrList"]

            #except Exception as e:
            """    ComFnObj.PrintException("raise_alert_mobile")
            status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)"""

class getcustomerdetails:
    def GET(self):
        try:
            ComFnObj=Commonfunctions()
            user_input = web.input(caller_number='Null',cancelled_alert_id='Null')
            phone =  user_input.subscriber_number
            caller_number = user_input.caller_number
            c_id = user_input.cancelled_alert_id

            if c_id != 'Null':
                db.delete('alerts',vars=locals(),where='alert_id=$c_id')

            EmrContact=json.loads(ComFnObj.GetEmrContact(2,caller_number,1))
            User=ComFnObj.GetIdFromPhone(caller_number,"USR") #Extract Name from here
            UserName="Abhilash"
            JArray=[]
            Cnt=0
            for person in EmrContact["EmrList"]:
                Cnt+=1
                print person
                JArray2={}
                JArray2["priority"]=Cnt
                JArray2["relation"]="Emergency Contact"
                JArray2["name"]=str(person["name"])
                JArray2["number"]=str(person["phone"])
                print person["name"]
                AlertID=1   # HARD CODED FOR SECURITY PART. MAY BE THERE WILL BE A CHANGE
                            # FOR FUTURE USE I HAVE PUT THAT IN A TABLE CALLED alerttype
                            # 1 is the ID for SECURITY
                JArray.append(JArray2)
            print JArray
            jreturn = {'registered':'true','alert_types':{},'emergency_count':Cnt,\
                       'recipient_name':UserName,'alert_id': user_input.alertid,\
                       'default_alert_type':AlertID,'emergency_contacts':(JArray)}
            print jreturn
            xml = dicttoxml.dicttoxml(jreturn)
            print xml
            root = ET.fromstring(xml)

            alert_types_node = root.find('alert_types')

            newNode= Element('alert_type', {'id': '1'})
            newNode.text  = "security"

            alert_types_node.append(newNode)
            print ET.tostring(root)
            return ET.tostring(root)


        except Exception as e:
            return e

#====================================================================

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
        DoctorId = ComFnObj.GetIdFromPhone(user_data.DocNumber, "DOC")
        UserId = ComFnObj.GetIdFromPhone(user_data.UserNumber, "USR")
        try:
            entries = db.insert('telmedCallHistory',
                                user_id=UserId, \
                                doctor_id=DoctorId, \
                                call_date=user_data.date, \
                                call_time=user_data.time, \
                                status=user_data.status, \
                                duration=user_data.duration, \
                                isFollowUpAllowed=user_data.followup, )
        except Exception as e:
            ComFnObj.PrintException("TeleConnectComplete")
            status = {"status": "Error", "message": "Error Try Later","statusCode":600,"success":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)

        else:
            status = {"status": "Sucess", "message": "Call data Updates","statusCode":777,"success":True}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)


class CreateAlert:
    def GET(self):
        ComFnObj = Commonfunctions()
        # user_data = json.loads(json_input)
        user_data = web.input()
        header = web.ctx.environ
        authcode = header.get('HTTP_AUTHCODE')
        if (ComFnObj.CheckAuth(authcode) == 0):
            status = {"status": "Error", "message": "AuthCode Failed","statusCode":500,"success":False}
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', '*')
            web.header('Access-Control-Allow-Headers', '*')
            web.header('Content-Type', 'application/json')
            return  json.dumps(status)
        else:
            EmrPhonenumber = ComFnObj.GetEmrContact(1, authcode, 2)
            Numbers = json.loads(EmrPhonenumber).split(',')
            Data = ""
            for i in range(0, len(Numbers) - 1):
                Number = Numbers[i].split(":")
                Data += Number[1] + " sent to Knowlarity for calling\n"  # HERE WILL HAVE THE ACTUAL API CALL TO KNOWLARITY
                return Data

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
else:
    application = web.application(urls, globals()).wsgifunc()
