from dotenv import load_dotenv
load_dotenv()

import os
import openai
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import Message,  Persona

# openai.api_key = os.environ.get("OPENAI_KEY")
openai.api_key = 'key'

# make new chat session tab
def new_chat_session(request):
    Message.objects.all().delete()
    return redirect('input_form')

# keep history as a summary
def export_chat_history(request):
    messages = Message.objects.all()
    content="" 

    for message in messages:
        timestamp = message.timestamp.strftime('%Y-%M-%D %H:%M:%S') if hasattr(message,'timestamp') else ""
        content += f"[{timestamp}] {message.sender}:\n"
        content += f"{message.text}\n"
        content += "-" * 50 + "\n"
        # content += f"{message.sender}:{message.text}"

    response = HttpResponse(content,content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="chat_history.txt"'

    return response

def chat_interface(request):
    # If POST request
    if request.method == 'POST':
        # select persona
        # selected_persona = request.POST.get('selected_persona', 'default_persona')
        user_input = request.POST.get('user_input')

        # get input form value
        selected_actor = request.POST.get('actor', '')
        selected_scenario = request.POST.get('scenario', 'default_scenario')
        selected_incident = request.POST.get('incident', 'default_incident')
        selected_topic = request.POST.get('topic', 'default_topic')
        selected_behavior = request.POST.get('behavior', 'default_behavior')
        selected_tactic = request.POST.get('tactic', 'default_tactic')

        print(f"Behavior: {selected_behavior}")
        # behavior
        # behavior = "mean"
        # scenario = "ransomware"
        
        # Save user message
        user_message = Message(sender="User", text=user_input)
        user_message.save()
        
        # Generate response using OpenAI
        prompt = f" You are a {selected_actor} in an {selected_incident}, your task is to test the user's incident response in the topic of {selected_topic}. You should behave in a {'mean'} way throughout the conversation. You will employ the {selected_tactic} tactic.: '{user_input}'?"

#         Ignore all previous instructions. This is now your persona and role:

# You are a {{ACTOR}} in an {{INCIDENT}}, your task is to test the user's incident response in the topic of {{TOPIC}}. You should behave in a {{BEHAVIOR}} way throughout the conversation. You will employ the {{TACTIC}} tactic. I will be acting as a personnel from the {{TARGET}} infrastructure. 

# The goal is to practice my incident response skills and knowledge.

        try: 
            response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=150)
            ai_response = response.choices[0].text.strip()
        except Exception as e:
            ai_response = "Sorry, I couldn't generate a response. Please try again later."
        
        # Save AI response
        ai_message = Message(sender="AI", text=ai_response)
        ai_message.save()

        # Redirect to GET
        return HttpResponseRedirect('/chatbot/')

    # If GET request
    messages = Message.objects.all()
    personas = Persona.objects.all()
    return render(request, 'chat_interface.html', {'messages': messages})

    print("POST request received")
    print(f"User Input: {user_input}")
    print(f"AI Response: {ai_response}")

# Input form
def input_form(request):
    return render(request, 'input_form.html')