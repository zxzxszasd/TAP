# openai.api_key = 'sk-BhOI9G9BO3su6DyjKY####GlT3BlbkFJK40vfrgGhB2LGMDUo4Ne'
import openai
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from .models import Message,  Persona

openai.api_key = ''

# make new chat session tab
def new_chat_session(request):
    Message.objects.all().delete()
    return redirect('chat_interface')

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
        return HttpResponseRedirect('/chatbot')

    # If GET request
    messages = Message.objects.all()
    personas = Persona.objects.all()
    return render(request, 'chat_interface.html', {'messages': messages})

    print("POST request received")
    print(f"User Input: {user_input}")
    print(f"AI Response: {ai_response}")




