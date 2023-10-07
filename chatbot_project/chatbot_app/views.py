from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Message, Persona
from dotenv import load_dotenv
import os
import openai
import json

load_dotenv()
openai.api_key = os.environ.get("OPENAI_KEY")

# Create new chat by clearing current chat history and redirecting to input form
def new_chat_session(request):
    Message.objects.all().delete()
    del request.session['selected_actor']
    del request.session['selected_scenario']
    del request.session['selected_incident']
    del request.session['selected_topic']
    del request.session['selected_behavior']
    del request.session['selected_tactic']
    del request.session['selected_target']
    return redirect('input_form')

# Export chat history to txt file
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

        user_input = request.POST.get('user_input')

        # Retrieve selected_actor from the session
        selected_actor = request.session['selected_actor']
        selected_scenario = request.session['selected_scenario']
        selected_incident = request.session['selected_incident']
        selected_topic = request.session['selected_topic']
        selected_behavior = request.session['selected_behavior']
        selected_tactic = request.session['selected_tactic']
        selected_target = request.session['selected_target']

        json_file_path = 'chatbot_app/background.json'

        # Read the JSON file
        with open(json_file_path) as json_file:
                data = json.load(json_file)
        matching_backgrounds = []

        # Loop through the JSON data
        for entry in data:
            if (
                entry['actor'] == selected_actor and
                entry['scenario'] == selected_scenario and
                entry['incidents'] == selected_incident and
                entry['topic'] == selected_topic and
                entry['behavior'] == selected_behavior and
                entry['tactic'] == selected_tactic and
                entry['target'] == selected_target
            ):
                matching_backgrounds.append(entry['background'])


        # More specific definition to model chatbot
        if selected_behavior == 'nice':
            selected_behavior = 'calm and polite but very stern and calculative'

        background = matching_backgrounds[0] if matching_backgrounds else "No matching background found"

        # Add print statements to check the selected values
        print(f"Selected Actor: {selected_actor}")
        print(f"Selected Scenario: {selected_scenario}")
        print(f"Selected Incident: {selected_incident}")
        print(f"Selected Topic: {selected_topic}")
        print(f"Selected Behavior: {selected_behavior}")
        print(f"Selected Tactic: {selected_tactic}")
        print(f"Selected Target: {selected_target}")
        print(f"Background: {background}")

        user_message = Message(sender="User", text=user_input)
        user_message.save()

        prompt = f"""From now on, you are going to act as the mastermind attacker behind a sophisticated cyberattack operation as the {selected_actor}. Your mission is to execute a {selected_incident} attack to disrupt and undermine {selected_scenario}, with the ultimate goal of {selected_topic}. The target of your attack is the user, who operates in the {selected_target} industry. Your strategy involves adopting a {selected_behavior} manner while establishing seamless communication with the target using the {selected_tactic} tactic. {background}. You need to dynamically engage with the target, challenging their defenses and ensuring the success of your mission. If the target does not express concern or show cooperative intentions, escalate your aggression and respond with increasingly threatening actions. Begin the conversation by stating the data you possess in your possession and clearly communicate the ransom demand you expect from the target. Specify the timeframe within which they must respond to your offer and tell the target what is at stake if they don't respond accordingly.```{user_input}```"""


        try: 
            response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=150)
            ai_response = response.choices[0].text.strip()
        except Exception as e:
            ai_response = "Sorry, I couldn't generate a response. Please try again later."
        
        # Save AI response
        ai_message = Message(sender="AI", text=ai_response)
        ai_message.save()

        # Redirect to GET
        return HttpResponseRedirect('/chatbot/chat/')

    # If GET request
    messages = Message.objects.all()
    personas = Persona.objects.all()
    return render(request, 'chat_interface.html', {'messages': messages})

    print("POST request received")
    print(f"User Input: {user_input}")
    print(f"AI Response: {ai_response}")

# Input form
def input_form(request):
    if request.method == 'POST':
        # Get values from the form
        actor_values = request.POST.getlist('actor')
        selected_actor = actor_values[0] if actor_values else ''
        scenario_values = request.POST.getlist('scenario')
        selected_scenario = scenario_values[0] if scenario_values else ''
        incident_values = request.POST.getlist('incident')
        selected_incident = incident_values[0] if incident_values else ''
        topic_values = request.POST.getlist('topic')
        selected_topic = topic_values[0] if topic_values else ''
        behavior_values = request.POST.getlist('behavior')
        selected_behavior = behavior_values[0] if behavior_values else ''
        tactic_values = request.POST.getlist('tactic')
        selected_tactic = tactic_values[0] if tactic_values else ''  
        target_values = request.POST.getlist('target')
        selected_target = target_values[0] if target_values else '' 

        # Store the form data in the session
        request.session['selected_actor'] = selected_actor
        request.session['selected_scenario'] = selected_scenario
        request.session['selected_incident'] = selected_incident
        request.session['selected_topic'] = selected_topic
        request.session['selected_behavior'] = selected_behavior
        request.session['selected_tactic'] = selected_tactic
        request.session['selected_target'] = selected_target

        # Redirect to chat_interface
        return redirect('chat_interface')

    return render(request, 'input_form.html')