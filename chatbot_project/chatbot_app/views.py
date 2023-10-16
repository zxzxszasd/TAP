from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Message, Persona
from dotenv import load_dotenv
import os
import openai
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_KEY")

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

        json_file_path = 'chatbot_app/data/background.json'

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
        if selected_actor == 'apt':
            selected_actor = 'APT38, a threat actor, employs various techniques and tools for cyber operations, including using backdoors like QUICKRIDE, collecting browser information, employing brute force attacks, and leveraging malware such as KEYLIME for clipboard data. The group also utilizes PowerShell, Windows Command Shell, and Visual Basic for command execution, and has employed tactics like creating new Windows services for persistence. APT38 is known for data manipulation using tools like DYEPACK and engaging in destructive activities like data encryption with Hermes ransomware.'
        if selected_scenario == 'ransom':
            selected_scenario = 'demand ransom payment'
        if selected_incident == 'ransomware':
            selected_incident = 'HERMES ransomware is a high-risk ransomware infection, utilizing the AES encryption algorithm to encrypt files and appending them with the ".Hermes" extension. It demands a ransom in Bitcoin, with a time-sensitive payment structure. The infection also alters desktop wallpaper, leaves a ransom message, and has similarities with other ransomware strains. Infections like Virus Hermes spread through trojans, fake software, spam emails, and unofficial download sources. Protection involves cautious online behavior, official software sources, and regular data backups.'
        if selected_topic == 'payment':
            selected_topic = 'Negotiating lowering ransom payment amount and extend the ransom payment timeframe.'
        if selected_behavior == 'nice':
            selected_behavior = 'calm and polite but very stern and calculative'
        if selected_behavior == 'mean':
            selected_behavior = 'aggressive manipulative and deceptive'
        if selected_tactic == 'doubleExtortion':
            selected_tactic = 'Double extortion attacks by gaining access to network of the victim, performing network discovery, exfiltrating high-value assets, encrypting data, and demanding a ransom. Attackers use methods such as phishing, malware, exploits, brute-forcing, and stolen credentials. The attack sequence includes initial access, network recon, data exfiltration, ransomware deployment, and a potential DDoS attack.In addition to demanding ransom for decrypting the files of targeted organizations the attacker also threaten to post sensitive information to a leak site if the ransom is not paid.'

        background = matching_backgrounds[0] if matching_backgrounds else "No matching background found"

        user_message = Message(sender="User", text=user_input)
        user_message.save()

        completion = openai.ChatCompletion.create(
            # Fine tuning model 1
            # model="ft:gpt-3.5-turbo-0613:personal::88geb1nm",

            # Fine tuning model 2
            model="ft:gpt-3.5-turbo-0613:personal::8A6f7P2W",

            # General model
            # model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"From now on, you are going to act as the mastermind attacker behind a sophisticated cyberattack operation as the {selected_actor}. You have execute a {selected_incident}. The tactic you used is {selected_tactic}. Your attack has disrupted the target's operation, your goal is to {selected_scenario}. The target of your attack is the user, who operates in the {selected_target} industry. You will speak in a {selected_behavior} manner. The user will try to {selected_topic}. {background}\nBegin the conversation by stating the data you possess in your possession, the ransom demand you expecting which is $500,000 in Bitcoin and the timeframe is within 72 hours. Tell the target what is at stake if they don't respond accordingly. \nYou need to dynamically engage with the target, challenging their defenses and ensuring the success of your mission. If the target does not express concern or show cooperative intentions, escalate your aggression and respond with increasingly threatening actions"
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ],
            max_tokens=150,
        )

        # print(completion.choices[0].message.content)
        ai_response = completion.choices[0].message.content
        
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