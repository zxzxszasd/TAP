import openai
import streamlit as st

# Set up your OpenAI API key
api_key = "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"
openai.api_key = api_key

# Define the chat_with_bot function
def chat_with_bot(user_input, role):
    # Create the persona-specific prompt
    prompt = f"You are a {role}. User: {user_input}"
    
    # Send the prompt to the ChatGPT model and get a response
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=50,  # Adjust based on response length preference
    )
    
    return response.choices[0].text.strip()

# Streamlit app header
st.title("Role-Based Chatbot")

# User selects their role
role = st.selectbox("Select your role:", ["Police Officer", "Doctor", "Patient"])

# Initialize chat history
chat_history = []

# Initialize a counter for widget keys
widget_counter = 0

# Chat loop
while True:
    user_input = st.text_input(f"{role}:", key=f"{role}_input_{widget_counter}")
    
    if st.button("Send"):
        if user_input.lower() == "exit":
            break

        # Get the chatbot response
        bot_response = chat_with_bot(user_input, role)

        # Append the conversation to the chat history
        chat_history.append((f"{role}:", user_input))
        chat_history.append(("ChatBot:", bot_response))

        # Increment the widget counter
        widget_counter += 1

    # Display chat history with a unique key for the text area
    st.text_area(f"Chat History ({role})", value="\n".join([f"{sender} {message}" for sender, message in chat_history]))

# Notify the user when the conversation ends
st.write("Conversation ended. You can close the browser window.")

# Save the chat history to a file (optional)
with open(f"{role}_conversation.txt", "w") as file:
    file.write("\n".join([f"{sender} {message}" for sender, message in chat_history]))
