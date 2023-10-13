import openai

# Define a function to open a file and return its content as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    

#Define a function to save content to a file
def save_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as outfile:
        outfile.write(content)

# Set the OpenAI API keys by reading them from files
openai.api_key = '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'

# with open ("C:/Users/beryl/Desktop/dataset.jsonl", "rb") as file:
#     response = openai.File.create(
#         file=file,
#         purpose='fine-tune'
#     )

# file_id = response['id']
# print(f"File uploaded successfully with ID: {file_id}")

# Fine tuning job
# file_id = "file-hQA5yi6gCgIv4jhaAVQqHxmT"
# model_name = "gpt-3.5-turbo"

# response = openai.FineTuningJob.create(
#     training_file=file_id,
#     model=model_name
# )

# job_id = response['id']
# print(f"Fine-tuning job created successfilly with ID: {job_id}")

# List fine-tune models
mydict = openai.FineTune.list()
print(type(mydict))
print(mydict)
