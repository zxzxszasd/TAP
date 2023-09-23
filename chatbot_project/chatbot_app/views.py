from dotenv import load_dotenv
load_dotenv()

import os
import openai
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Message,  Persona

openai.api_key = os.environ.get("OPENAI_KEY")

def chat_interface(request):
    # If POST request
    if request.method == 'POST':
        # select persona
        selected_persona = request.POST.get('selected_persona', 'default_persona')
        user_input = request.POST.get('user_input')
        
        # Save user message
        user_message = Message(sender="User", text=user_input)
        user_message.save()
        
        # Generate response using OpenAI
        prompt = f"{selected_persona}: '{user_input}'?"
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