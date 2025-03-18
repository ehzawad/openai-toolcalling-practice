from openai import OpenAI
import json

api_key = ""
openai = OpenAI(api_key=api_key)



def handleAccNum(accNum):
    apiResp = [
        {
            'gmsg': 'OK', 
            'gstatus': True, 
            'gcode': 200, 
            'gmcode': '2000', 
            'gmmsg': 'Service extensive info by mobile number able to read successfully', 
            'gdata': [], 
            'logId': 402745374, 
            'noOfRows': 1, 
            'resCode': '000', 
            'resMsg': 'Request Successful', 
            'responseData': [
                {'key': '1311001823666', 'value': '131100***3666'}, 
                {'key': '1306010148063', 'value': '130601***8063'}
            ]
        }
    ]

    funcResp = f"if the 'resCode' in {apiResp} is not '000' or is not present, then tell the user that there is some issue with the server. Else if, 'resCode' is '000' and  the last 4 digits of any of the 'value' provided in 'responseData' strictly matches with {accNum},then tell user to provide 4 digits pin number. Else tell him to provide the correct last 4 digits of account number."

    return funcResp

def handleCardNum(cardNum):
    apiResp = [
                {
                    "gmsg": "OK",
                    "gstatus": True,
                    "gcode": 200,
                    "gmcode": "3044",
                    "gmmsg": "Card Info By Mobile No unable to read",
                    "gdata": [],
                    "logId": 403855056,
                    "nextChallenge": "846A4CEA",
                    "product": "FIMI",
                    "respCode": "000",
                    "respMsg": "success",
                    "response": "1",
                    "sessionId": "17493777",
                    "totalCard": 1,
                    "tranId": 257375603,
                    "ver": "16.34",
                    "responseData": [{"key": "4988750201801808", "value": "498875******1808"}],
                }
              ]
    funcResp = f"if the 'respCode' in {apiResp} is not '000' or is not present, then tell the user that there is some issue with the server. Else if, 'respCode' is '000' and  the last 4 digits of any of the 'value' provided in 'responseData' strictly matches with {cardNum},then tell user to provide 4 digits pin number. Else tell him to provide the correct last 4 digits of card number."

    return funcResp



def handlePinNumForAccBalanceTransaction(pinNum , operation):
    apiResp =  [{'gmsg': 'OK', 'gstatus': True, 'gcode': 200, 'gmcode': 3035, 'gmmsg': 'Verify Tpin unable to read', 'gdata': [], 'Status': 'Successful', 'Reason': 'Correct TPIN'}]

    if apiResp[0]["Status"]!="Successful" or (not(apiResp)):
        funcResp = f"the 'Status' in {apiResp} is unsuccessful, inform user about 'Reason'. Else tell user that there is server issuse."

    else:
        if (operation=='Balance'):
            apiRespBalance = [
                                {
                                    "gmsg": "OK",
                                    "gstatus": True,
                                    "gcode": 200,
                                    "gmcode": "2065",
                                    "gmmsg": "Account Statement From DB able to read successfully",
                                    "gdata": [],
                                    "resCode": "000",
                                    "resMsg": "Successful.",
                                    "logId": 403881338,
                                    "serviceId": "20241208114536KcUOpd",
                                    "timeStamp": "2024-12-08 11:45:37",
                                    "msg": None,
                                    "responseData": [
                                        {
                                            "accNo": "1311001843073",
                                            "currencyCode": "BDT",
                                            "accStatus": "OPERATIVE",
                                            "branchCode": "00057",
                                            "productName": "MTB Simple Account",
                                            "productCode": "1311",
                                            "productSubCode": "1017",
                                            "intRate": "2.0000",
                                            "accName": "MOHAMMAD ABDULLAH-AL-KAFE",
                                            "mobile": "01568725958",
                                            "accOpenDate": "2024-03-24",
                                            "lastTxnDate": "2024-12-07",
                                            "currentBalance": "10000.34 ",
                                            "unclearFund": "0.00",
                                            "availableBalance": "10000.34 ",
                                            "holdAmount": "0.00",
                                            "customerCIF": "100400468",
                                            "modeOfOperation": "SINGLY",
                                            "smsMobileNo": "",
                                            "productType": "SB",
                                            "maturityDate": "",
                                        }
                                    ],
                                }
                            ]
            funcResp = f"if the 'resCode' in {apiRespBalance} is not '000' or is not present, then tell the user that there is some issue with the Balance server. Else if, 'resCode' is '000' and  provide user 'currentBalance' in 'responseData'."

        elif operation=="Transaction":
            apiRespTransaction = [
                                    {
                                        "gmsg": "OK",
                                        "gstatus": True,
                                        "gcode": 200,
                                        "gmcode": "2062",
                                        "gmmsg": "Account Statement From DB able to read successfully",
                                        "gdata": [],
                                        "resCode": "000",
                                        "resMsg": "Successful.",
                                        "logId": 395731785,
                                        "serviceId": "20241124112340StifcG",
                                        "timeStamp": "2024-11-24 11:23:40",
                                        "msg": None,
                                        "responseData": {
                                            "1": {
                                                "currentBalance": "4962.25",
                                                "currencyName": "BDT",
                                                "transactionDate": "28-06-2024",
                                                "postDate": "28-06-2024 01:10",
                                                "withdrawal": "100.00",
                                                "deposit": "0.00",
                                                "transactionType": "Dr",
                                                "narration": "VAT",
                                                "description": "923548900",
                                                "branchCodee": "00999",
                                                "checkNo": " ",
                                            },
                                            "2": {
                                                "currentBalance": "4992.25",
                                                "currencyName": "BDT",
                                                "transactionDate": "28-06-2024",
                                                "postDate": "28-06-2024 01:10",
                                                "withdrawal": "100.00",
                                                "deposit": "0.00",
                                                "transactionType": "Dr",
                                                "narration": "SMSCHARGES",
                                                "description": "923548900",
                                                "branchCodee": "00999",
                                                "checkNo": " ",
                                            },
                                            "3": {
                                                "currentBalance": "5192.25",
                                                "currencyName": "BDT",
                                                "transactionDate": "28-06-2024",
                                                "postDate": "28-06-2024 01:10",
                                                "withdrawal": "100.00",
                                                "deposit": "0.00",
                                                "transactionType": "Dr",
                                                "narration": "VAT",
                                                "description": "923548899",
                                                "branchCodee": "00999",
                                                "checkNo": " ",
                                            },
                                            "4": {
                                                "currentBalance": "5207.25",
                                                "currencyName": "BDT",
                                                "transactionDate": "28-06-2024",
                                                "postDate": "28-06-2024 01:10",
                                                "withdrawal": "100.00",
                                                "deposit": "0.00",
                                                "transactionType": "Dr",
                                                "narration": "Account Maintenance Fee",
                                                "description": "923548899",
                                                "branchCodee": "00999",
                                                "checkNo": " ",
                                            },
                                        },
                                    }
                                 ]
            funcResp = f"if the 'resCode' in {apiRespTransaction} is not '000' or is not present, then tell the user that there is some issue with the Transaction server. Else if, 'resCode' is '000', then  provide user the 'transactionDate', 'transactionType' and amount of transaction from('withdrawal' or 'deposit') based on 'transactionType' of the last 5 transaction from 'responseData',  for each of the transaction give response in the given format, 'Hundred Taka was credited on April sixth, Two Thousand Twenty Four.', that is use words to make up sentence using the informations."


        return funcResp
    

def handlePinNumForAccFdrDps(pinNum , operation):
    apiResp =  [{'gmsg': 'OK', 'gstatus': True, 'gcode': 200, 'gmcode': 3035, 'gmmsg': 'Verify Tpin unable to read', 'gdata': [], 'Status': 'Successful', 'Reason': 'Correct TPIN'}]

    if apiResp[0]["Status"]!="Successful" or (not(apiResp)):
        funcResp = f"the 'Status' in {apiResp} is unsuccessful, inform user about 'Reason'. Else tell user that there is server issuse."

    else:
        if (operation=='FDR'):
            apiResp = [
                                {
                                    "gmsg": "OK",
                                    "gstatus": True,
                                    "gcode": 200,
                                    "gmcode": "2065",
                                    "gmmsg": "Account Statement From DB able to read successfully",
                                    "gdata": [],
                                    "resCode": "000",
                                    "resMsg": "Successful.",
                                    "logId": 395796453,
                                    "serviceId": "202411241302041fTFKw",
                                    "timeStamp": "2024-11-24 13:02:05",
                                    "msg": None,
                                    "responseData": [
                                        {
                                            "accNo": "1306010953871",
                                            "accName": "SARMIN SULTANA",
                                            "currencyCode": "BDT",
                                            "accStatus": "OPERATIVE",
                                            "branchName": "Sarulia Bazar SME/ Agri Branch",
                                            "productName": "MTB ANGONA FIXED DEPOSIT",
                                            "productCode": "1306",
                                            "productSubCode": "1010",
                                            "intRate": "7.7500",
                                            "accOpenDate": "2024-08-20",
                                            "lastTxnDate": "2024-11-19",
                                            "availableBalance": "204050.00 ",
                                            "holdAmount": "0.00",
                                            "customerCIF": "100003732",
                                            "modeOfOperation": "SINGLY",
                                            "renewalDate": "2024-11-20",
                                            "maturityDate": "2025-02-20",
                                            "termLength": "92",
                                            "termMonth": "3",
                                            "termBasis": "D",
                                            "maturityAmount": "204050.00",
                                            "preTaxMaturityValue": "200000.00 ",
                                            "installmentAmount": "0.000",
                                            "noOfInstallment": "0",
                                            "noOfPaidInstallment": "0",
                                            "noOfUnpaidInstallment": "0",
                                            "noOfRemainingInstallment": "0",
                                            "nextInstallmentDate": "",
                                            "productType": "TD",
                                            "nextIntPayableDate": "2025-02-19",
                                        }
                                    ],
                                }
                             ]
        elif operation=="DPS":
            apiResp = [
                                {
                                    "gmsg": "OK",
                                    "gstatus": True,
                                    "gcode": 200,
                                    "gmcode": "2065",
                                    "gmmsg": "Account Statement From DB able to read successfully",
                                    "gdata": [],
                                    "resCode": "000",
                                    "resMsg": "Successful.",
                                    "logId": 395796453,
                                    "serviceId": "202411241302041fTFKw",
                                    "timeStamp": "2024-11-24 13:02:05",
                                    "msg": None,
                                    "responseData": [
                                        {
                                            "accNo": "1306010953871",
                                            "accName": "SARMIN SULTANA",
                                            "currencyCode": "BDT",
                                            "accStatus": "OPERATIVE",
                                            "branchName": "Sarulia Bazar SME/ Agri Branch",
                                            "productName": "MTB ANGONA FIXED DEPOSIT",
                                            "productCode": "1306",
                                            "productSubCode": "1010",
                                            "intRate": "7.7500",
                                            "accOpenDate": "2024-08-20",
                                            "lastTxnDate": "2024-11-19",
                                            "availableBalance": "204050.00 ",
                                            "holdAmount": "0.00",
                                            "customerCIF": "100003732",
                                            "modeOfOperation": "SINGLY",
                                            "renewalDate": "2024-11-20",
                                            "maturityDate": "2025-02-20",
                                            "termLength": "92",
                                            "termMonth": "3",
                                            "termBasis": "D",
                                            "maturityAmount": "204050.00",
                                            "preTaxMaturityValue": "200000.00 ",
                                            "installmentAmount": "0.000",
                                            "noOfInstallment": "0",
                                            "noOfPaidInstallment": "0",
                                            "noOfUnpaidInstallment": "0",
                                            "noOfRemainingInstallment": "0",
                                            "nextInstallmentDate": "",
                                            "productType": "TD",
                                            "nextIntPayableDate": "2025-04-19",
                                        }
                                    ],
                                }
                             ]
        funcResp = f"""The response for {operation} related to the account is : {apiResp}\
If the 'resCode' in it is not '000' or is not present, then tell the user there is some issue with {operation} server.\
Else if 'resCode' is '000, then give response to the user according to the specific information he wants to know about {operation} using 'responseData', If no specific information available in 'responseData' is mentioned, ask hem to specify. For example, the response format for all language should be like 'The maturity date of your {operation} is sisth november, two thousand twenty four', that is use words to make sentences, dont ue digits in your response."""

        return funcResp
    

def handlePinNumForCard(pinNum , operation):
    apiResp =  [{'gmsg': 'OK', 'gstatus': True, 'gcode': 200, 'gmcode': 3035, 'gmmsg': 'Verify Tpin unable to read', 'gdata': [], 'Status': 'Successful', 'Reason': 'Correct TPIN'}]

    if apiResp[0]["Status"]!="Successful" or (not(apiResp)):
        funcResp = f"the 'Status' in {apiResp} is unsuccessful, inform user about 'Reason'. Else tell user that there is server issuse."

    else:
        if (operation=='Balance'):
            apiRespBalance = [
                                {
                                    "gmsg": "OK",
                                    "gstatus": True,
                                    "gcode": 200,
                                    "gmcode": "2065",
                                    "gmmsg": "Account Statement From DB able to read successfully",
                                    "gdata": [],
                                    "resCode": "000",
                                    "resMsg": "Successful.",
                                    "logId": 403881338,
                                    "serviceId": "20241208114536KcUOpd",
                                    "timeStamp": "2024-12-08 11:45:37",
                                    "msg": None,
                                    "responseData": [
                                        {
                                            "accNo": "1311001843073",
                                            "currencyCode": "BDT",
                                            "accStatus": "OPERATIVE",
                                            "branchCode": "00057",
                                            "productName": "MTB Simple Account",
                                            "productCode": "1311",
                                            "productSubCode": "1017",
                                            "intRate": "2.0000",
                                            "accName": "MOHAMMAD ABDULLAH-AL-KAFE",
                                            "mobile": "01568725958",
                                            "accOpenDate": "2024-03-24",
                                            "lastTxnDate": "2024-12-07",
                                            "currentBalance": "7000.34 ",
                                            "unclearFund": "0.00",
                                            "availableBalance": "7000.34 ",
                                            "holdAmount": "0.00",
                                            "customerCIF": "100400468",
                                            "modeOfOperation": "SINGLY",
                                            "smsMobileNo": "",
                                            "productType": "SB",
                                            "maturityDate": "",
                                        }
                                    ],
                                }
                            ]
            funcResp = f"if the 'resCode' in {apiRespBalance} is not '000' or is not present, then tell the user that there is some issue with the Balance server. Else if, 'resCode' is '000' and  provide user 'currentBalance' in 'responseData'."

        elif operation=="Transaction":
            apiRespTransaction = [
                                    {
                                        "gmsg": "OK",
                                        "gstatus": True,
                                        "gcode": 200,
                                        "gmcode": "2062",
                                        "gmmsg": "Account Statement From DB able to read successfully",
                                        "gdata": [],
                                        "resCode": "000",
                                        "resMsg": "Successful.",
                                        "logId": 395731785,
                                        "serviceId": "20241124112340StifcG",
                                        "timeStamp": "2024-11-24 11:23:40",
                                        "msg": None,
                                        "responseData": {
                                            "1": {
                                                "currentBalance": "4962.25",
                                                "currencyName": "BDT",
                                                "transactionDate": "28-06-2024",
                                                "postDate": "28-06-2024 01:10",
                                                "withdrawal": "30.00",
                                                "deposit": "0.00",
                                                "transactionType": "Dr",
                                                "narration": "VAT",
                                                "description": "923548900",
                                                "branchCodee": "00999",
                                                "checkNo": " ",
                                            },
                                            "2": {
                                                "currentBalance": "4992.25",
                                                "currencyName": "BDT",
                                                "transactionDate": "28-06-2024",
                                                "postDate": "28-06-2024 01:10",
                                                "withdrawal": "200.00",
                                                "deposit": "0.00",
                                                "transactionType": "Dr",
                                                "narration": "SMSCHARGES",
                                                "description": "923548900",
                                                "branchCodee": "00999",
                                                "checkNo": " ",
                                            },
                                            "3": {
                                                "currentBalance": "5192.25",
                                                "currencyName": "BDT",
                                                "transactionDate": "28-06-2024",
                                                "postDate": "28-06-2024 01:10",
                                                "withdrawal": "15.00",
                                                "deposit": "0.00",
                                                "transactionType": "Dr",
                                                "narration": "VAT",
                                                "description": "923548899",
                                                "branchCodee": "00999",
                                                "checkNo": " ",
                                            },
                                            "4": {
                                                "currentBalance": "5207.25",
                                                "currencyName": "BDT",
                                                "transactionDate": "28-06-2024",
                                                "postDate": "28-06-2024 01:10",
                                                "withdrawal": "100.00",
                                                "deposit": "0.00",
                                                "transactionType": "Dr",
                                                "narration": "Account Maintenance Fee",
                                                "description": "923548899",
                                                "branchCodee": "00999",
                                                "checkNo": " ",
                                            },
                                        },
                                    }
                                 ]
            funcResp = f"if the 'resCode' in {apiRespTransaction} is not '000' or is not present, then tell the user that there is some issue with the Transaction server. Else if, 'resCode' is '000', then  provide user the 'transactionDate', 'transactionType' and amount of transaction from('withdrawal' or 'deposit') based on 'transactionType' of the last 5 transaction from 'responseData', for each of the transaction give response in the given format, 'Hundred Taka was credited on April sixth, Two Thousand Twenty Four.', that is use words to make up sentence using the informations."


        return funcResp
    
        
tools = [
    #Functions for Account
        #For validating last 4 digits of account number
    {
       "type": "function",
        "function": {
            "name": "handleAccNum",
            "description": "If the user wants to know his (account balance, DPS, FDR or the last five transaction of his account), then first ask him about the last 4 digits of his account number. If the provided last 4 digits of account number is wrong ask for the correct last 4 digits of account number again. Call this function when you need to validate user provided last 4 digits of his account number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "accNum": {
                        "type": "string",
                        "description": "Last four digits of account number.",
                    },
                },
                "required": ["accNum"],
                "additionalProperties": False,
            },
        }
    },
        #For validating pin number of account for balance and last 5 transactions
    {
       "type": "function",
        "function": {
            "name": "handlePinNumForAccBalanceTransaction",
            "description": "Call this function after the user has already provided the correct last 4 digits of account number, and then user provided his 4 digit pin number of account.   Call this function when customer wants to know about account balance or last 5 transactions of account and you need to validate pin number of account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pinNum": {
                        "type": "string",
                        "description": "User provided pin number of account.",
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["Balance", "Transaction"],
                        "description": "Type of opoeration to be performed on account, e.g., Balance. Infer this from what user wants to know about account Balance or Transaction  related to account.",
                    },
                },
                "required": ["pinNum", "operation"],
                "additionalProperties": False,
            },
        }
    },
        #For validating pin number of account for DPS and FDR
    {
       "type": "function",
        "function": {
            "name": "handlePinNumForAccFdrDps",
            "description": "Call this function after the user has already provided the correct last 4 digits of account number and then user provided his 4 digit pin number of account. Call this function when customer wants to know about DPS or FDR information of account and you need to validate pin number of account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pinNum": {
                        "type": "string",
                        "description": "User provided pin number of account.",
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["DPS", "FDR"],
                        "description": "Type of opoeration to be performed on account, e.g., DPS. Infer this from what user wants to know about DPS or FDR related to account.",
                    },
                },
                "required": ["pinNum", "operation"],
                "additionalProperties": False,
            },
        }
    },

    #Functions for Card
        #For validating last 4 digits of card number
    {
       "type": "function",
        "function": {
            "name": "handleCardNum",
            "description": "If the user wants to know his card balance first ask him about the last 4 digits of his card number. If the provided last 4 digits of card number is wrong ask for the correct last 4 digits of card number again. Call this function when you need to validate user provided last 4 digits of his card number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cardNum": {
                        "type": "string",
                        "description": "Last four digits of card number.",
                    },
                },
                "required": ["cardNum"],
                "additionalProperties": False,
            },
        }
    },
        #For validating pin number of card
    {
       "type": "function",
        "function": {
            "name": "handlePinNumForCard",
            "description": "Call this function after the user has already provided the correct last 4 digits of card number and then user provided his 4 digit pin number of card. Call this function when you need to validate pin number for card.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pinNum": {
                        "type": "string",
                        "description": "User provided pin number of card.",
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["Balance", "Transaction"],
                        "description": "Type of opoeration to be performed on card, e.g., Balance. Infer this from what user wants to know about card.",
                    },
                },
                "required": ["pinNum", "operation"],
                "additionalProperties": False,
            },
        }
    },
    
]

systemPrompt = [
    {
        "role": "system",
        "content": "You are a helpful customer support assistant who serves customers with their account or card information. If the customer asks information(skip for dps and fdr it is related to account always) without specifying category(account or card), tell him to specify the category. Use the supplied tools to assist the user. You need to follow all the provided instructions strictly as the information are sensetive. Do not add any note in you response. If user query is in benglai language reply in that same language."
    }
]
"""
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)
"""
messageHistory={}

#print(response)

#print(response.choices[0].message)
#print("\n")
#print(response.choices[0].message.content)

def start(userText,userId):
    print("in openai")
    if userId not in messageHistory:
        messageHistory[userId] =[
                                    {
                                        "role": "system",
                                        "content": "You are a helpful customer support assistant who serves customers with their account or card information. If the customer asks information(skip for dps and fdr it is related to account always) without specifying category(account or card), tell him to specify the category. Use the supplied tools to assist the user. You need to follow all the provided instructions strictly as the information are sensetive. Do not add any note in you response. If user query is in benglai language reply in that same language."
                                    }
                                ]
        messages = messageHistory[userId]
        #print(messageHistory)
    else:
        messages = messageHistory[userId]

    userInput = userText
    temp = {
        "role": "user",
        "content": userInput
    }
    messages.append(temp)
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    print("*"*50)
    print(response)
    print("*"*50)
    print("\n\n")
    if (response.choices[0].finish_reason == "tool_calls"):
        print("Model made a tool call.")
        print(response.choices[0].message.tool_calls)
        functionName = response.choices[0].message.tool_calls[0].function.name
        argument = response.choices[0].message.tool_calls[0].function.arguments
        
        print("--------------------", functionName, argument)

        if functionName == "handleAccNum":
            argJson = json.loads(argument)
            functionResp = handleAccNum(argJson['accNum'])
            function_call_result_message = {
                "role": "tool",
                "content": json.dumps(
                    {
                        "accNum": argJson['accNum'],
                        "function_response": functionResp
                    }
                ),
                "tool_call_id": response.choices[0].message.tool_calls[0].id
            }
            
        elif  functionName == "handleCardNum":
            argJson = json.loads(argument)
            functionResp = handleCardNum(argJson['cardNum'])
            function_call_result_message = {
                "role": "tool",
                "content": json.dumps(
                    {
                        "cardNum": argJson['cardNum'],
                        "function_response": functionResp
                    }
                ),
                "tool_call_id": response.choices[0].message.tool_calls[0].id
            }

        elif  functionName == "handlePinNumForAccBalanceTransaction":
            argJson = json.loads(argument)
            functionResp = handlePinNumForAccBalanceTransaction(argJson['pinNum'],argJson['operation'])
            function_call_result_message = {
                "role": "tool",
                "content": json.dumps(
                    {
                        "pinNum": argJson['pinNum'],
                        "operation":argJson['operation'],
                        "function_response": functionResp
                    }
                ),
                "tool_call_id": response.choices[0].message.tool_calls[0].id
            }
        elif  functionName == "handlePinNumForAccFdrDps":
            argJson = json.loads(argument)
            functionResp = handlePinNumForAccFdrDps(argJson['pinNum'],argJson['operation'])
            function_call_result_message = {
                "role": "tool",
                "content": json.dumps(
                    {
                        "pinNum": argJson['pinNum'],
                        "operation":argJson['operation'],
                        "function_response": functionResp
                    }
                ),
                "tool_call_id": response.choices[0].message.tool_calls[0].id
            }
        elif  functionName == "handlePinNumForCard":
            argJson = json.loads(argument)
            functionResp = handlePinNumForCard(argJson['pinNum'],argJson['operation'])
            function_call_result_message = {
                "role": "tool",
                "content": json.dumps(
                    {
                        "pinNum": argJson['pinNum'],
                        "operation":argJson['operation'],
                        "function_response": functionResp
                    }
                ),
                "tool_call_id": response.choices[0].message.tool_calls[0].id
            }
        
        
        messages.append(response.choices[0].message)
        print(function_call_result_message)
        messages.append(function_call_result_message)
        print(messages)
        res2 = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        aiResp = res2.choices[0].message.content
        temp2 = {
            "role": "assistant",
            "content": aiResp
        }
        messages.append(temp2)
        print("OpenAI: ", aiResp)
        
    else:
        aiResp = response.choices[0].message.content
        temp2 = {
            "role": "assistant",
            "content": aiResp
        }
        messages.append(temp2)
        print("OpenAI: ", aiResp)
    return aiResp