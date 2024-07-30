from flask import Flask,redirect,url_for,render_template,request
from functions import initialize_conversation,initialize_conversation_reco,get_chat_completions,moderation_check,intent_confirmation_layer,product_map_layer,dictionary_present,compare_laptops_with_user,recoomendation_validation
import openai
import ast
import re
import pandas as pd
import json
openai.api_key=open("OpenAI_API_Key.txt",'r').read().strip()
app=Flask(__name__)
conversation_bot=[]
conversation = initialize_conversation()
introduction = get_chat_completions(conversation)
conversation_bot.append({"bot":introduction})

top_3_laptops = None

@app.route('/')
def default_func():
    global conversation_bot,conversation,top_3_laptops
    # conversation.append({'bot':'please enter your name'})
    return render_template("index_invite.html",name_xyz=conversation_bot)
@app.route("/end_conv",methods=['POST',"GET"])
def end():
    global conversation_bot,conversation,top_3_laptops
    conversation_bot=[]
    conversation = initialize_conversation()
    introduction = get_chat_completions(conversation)
    conversation_bot.append({"bot":introduction})
    top_3_laptops=None
    return redirect(url_for("default_func"))
@app.route("/hi/<name>")
def hello(name):
    return render_template("index_hello.html",name_xyz=name)
@app.route("/bye/<name>")
def bye(name):
    return render_template("index_bye.html",name_xyz=name)
@app.route("/invite",methods=['POST'])
def invite():
    global conversation_bot,conversation,top_3_laptops,conversation_reco
    user_input=request.form['user_input_message']
    prompt="remember your system message that you are an intelligent laptop assistant so you only help in laptop quiries "
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        return redirect(url_for('end'))    

    if top_3_laptops is None:

        conversation.append({"role": "user", "content": user_input + prompt})
        conversation_bot.append({"user": user_input})
        response_assistant = get_chat_completions(conversation)
        moderation = moderation_check(response_assistant)
        if moderation == 'Flagged':
           return redirect(url_for('end'))    
                


        confirmation = intent_confirmation_layer(response_assistant)

        print("Intent Confirmation Yes/No:",confirmation.get('result'))

        if "No" in confirmation.get('result'):
            conversation.append({"role": "assistant", "content": str(response_assistant)})
            conversation_bot.append({"bot":str(response_assistant)})
               
               

        else:
          

           response = dictionary_present(response_assistant)

           print("Thank you for providing all the information. Kindly wait, while I fetch the products: \n")
           conversation_bot.append({"bot":"Thank you for providing all the information. Kindly wait, while I fetch the products: \n"})
           top_3_laptops = compare_laptops_with_user(response)

           print("top 3 laptops are", top_3_laptops)
          
          
           validated_reco = recoomendation_validation(top_3_laptops)
           if len(validated_reco)==0:
              
               conversation_bot.append({"bot":"sorry,we do not have any matches of your requirements END THIS CONVERSATION"})
           conversation_reco = initialize_conversation_reco(validated_reco)
         
           conversation_reco.append({"role": "user", "content": "This is my user profile" + str(response)})
        #   conversation_bot.append({ "user": + str(response)})
          
           recommendation = get_chat_completions(conversation_reco)

           moderation = moderation_check(recommendation)
           if moderation == 'Flagged':
              return redirect(url_for('end'))    

        #   conversation_reco.append({"role": "user", "content": "This is my user profile" + str(response)})
         
           conversation_reco.append({"role": "assistant", "content": str(recommendation)})
           conversation_bot.append({"bot": str(recommendation)})
                
           print(str(recommendation) + '\n')
    else:
        
        conversation_reco.append({"role": "user", "content": user_input})
        conversation_bot.append({"user": user_input})
        
        response_asst_reco = get_chat_completions(conversation_reco)

        moderation = moderation_check(response_asst_reco)
        if moderation == 'Flagged':
            return redirect(url_for('end'))    
                 

        print('\n' + response_asst_reco + '\n')
        conversation.append({"role": "assistant", "content": response_asst_reco})
        conversation_bot.append({"bot": response_asst_reco})
            
    return redirect(url_for("default_func"))
   
if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")