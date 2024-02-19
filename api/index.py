from datetime import date
from flask import Flask, request
from flask_cors import CORS
from supabase import create_client

SUPABASE_URL = "https://iduntfcvrolkhmgnfmcm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlkdW50ZmN2cm9sa2htZ25mbWNtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5MTkxODg0MCwiZXhwIjoyMDA3NDk0ODQwfQ.eP1Nu5QAAvXvmFGCKc2CDD1JfyKV-aXKfwtIm_d6YYI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app)

@app.route("/getUsers", methods=["GET"])
def getUsers():
    data = supabase.table("yogaClasses").select("*").execute()
    
    userDetails = dict(data)['data']
    
    for user in userDetails:
            
        prevYear, prevMonth, prevDay = user["feesPaidOn"].split('-')
        currYear, currMonth, currDay = str(date.today()).split("-")
        
        years = int(currYear)-int(prevYear)
        intermediateMonths = years*12        
        diff = ( int(currMonth) + intermediateMonths) - int(prevMonth)
        
        if diff == 1:
            user['toPay'] = 1; user["currMonthTimings"] = user["nextMonthTimings"]
            supabase.table("yogaClasses").update({"toPay":1, 'currMonthTimings':user['currMonthTimings']}).eq('id',user['id']).execute()
        elif diff > 1:
            user['toPay'] = 1; user["currMonthTimings"] = ""; user["nextMonthTimings"] = ""
            supabase.table("yogaClasses").update({"toPay":1, "currMonthTimings":"", "nextMonthTimings":""}).eq('id',user['id']).execute()            

    return userDetails


# ==============================================================

@app.route("/changeBatch", methods=['POST'])
def changeBatch():
    req = request.json
    
    try:
        data = supabase.table("yogaClasses").update({"nextMonthTimings":req["nextMonthTimings"]}).eq("id", req['id']).execute()
        return "Successfully updated timings for next month", 200
    except:
        return "Server Error", 400

@app.route("/enrollUser", methods=["POST"])
def enrollUser():
    req = request.json # name age time
    req.update({'feesPaidOn': str(date.today()), 'toPay':0, 'age':int(req['age'])})
    
    try:
        if req['age'] > 17:
            data = supabase.table("yogaClasses").insert(req).execute()
            # INSERT INTO yogaClasses values('Harshit', 22, '6-7AM', '6-7AM', '2023-12-19', 0)
            return "Successfully enrolled user", 200
        else:
            return "User doesn't meet age requirements!", 200
    except:
        return "Server Error", 400
    
    
@app.route("/deleteUser", methods=['POST'])
def deleteUser():
    req = request.json
    
    try:
        data = supabase.table("yogaClasses").delete().eq('id',req['id']).execute()
        # DELETE FROM yogaClasses WHERE ID=req['id'] 
        return f"User with ID {req['id']} has been removed successfully!", 200
    except:
        return "Server Error", 400
    
@app.route("/editUser", methods=['POST'])
def editUser():
    req = request.json
    
    try:
        data = supabase.table("yogaClasses").update({'name':req['name'], 'age':req['age']}).eq('id', req['id']).execute()
        # UPDATE yogaClasses values("abhijeet mahato", 22) WHERE ID=req['id'] 
        return dict(data)['data'], 200
    except:
        return "Server Error", 400
    
@app.route("/completePayment", methods=['POST'])
def completePayment():
    req = request.json
    
    try:
        data = supabase.table("yogaClasses").update({"feesPaidOn": str(date.today()), "toPay":0} ).eq('id', req["id"]).execute()
        return f"Successfully paid fees for user with ID {req['id']}", 200
    except:
        return "Server Error", 400

if __name__ == "__main__":
    app.run(debug = True)
    