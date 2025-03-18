from flask import Flask, request 
import requests
import forBank.bank_base as bank_base


app = Flask(__name__,template_folder='templates') 
@app.route('/', methods=['GET', 'POST']) 
def index(): 
    if request.method == 'POST': 
        print("Hi")
        userId=request.get_json()['sender_id']
        userText=request.get_json()['text']
        resp = bank_base.start(userText,userId)
        print("response that will be sent",resp)
        return {'text':resp}
    # userId=123
    # userText="I want to see my dps maturity date"
    # resp = bank_flask.start(userText,userId)
    # print(resp)
    return ""


  
if __name__ == '__main__':
    print("in")
    app.run(host='0.0.0.0', port=6003, debug=False) 