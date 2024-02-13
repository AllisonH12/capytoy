from datetime import datetime
import glob
import os
from openai import OpenAI

def get_recent_conversations(logs_dir="logs", max_files=500):
    log_files = glob.glob(f"{logs_dir}/conversation_history_*.txt")
    sorted_files = sorted(log_files, key=lambda x: os.path.getmtime(x), reverse=True)
    conversations = ""
    for file_path in sorted_files[:max_files]:
        with open(file_path, 'r') as file:
            conversations += file.read() + "\n\n"
    return conversations

def summarize_conversations(conversations):
    client = OpenAI()
    prompt = (
        "Read the following conversations and summarize key details about the conversation partner, "
        "including their name, interests, speaking style, any mentioned fun facts such as pet names, "
        "family members, their concerns, and their level of understanding:\n\n" + conversations
    )

    response = client.chat.completions.create(
      model="gpt-4",
      #model="gpt-3.5-turbo",
      messages=[
        {
          "role": "system",
          "content": "you are a summarizer, trying to understand the user, extract facts that is helpful to understand the user. "
        },
        {
          "role": "user",
          "content": "Read the following conversations and summarize key details about the conversation partner, \"\n        \"including their name, interests, speaking style, any mentioned fun facts such as pet names, \"\n        \"family members, their concerns, and their level of understanding:\\n\\n\" \n    \n"
        },
        {
          "role": "assistant",
          "content":conversations 
        }
    
      ],
      temperature=1,
      max_tokens=256,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    return  response.choices[0].message.content 

def main():
    logs_dir = "logs"  # Adjust as necessary
    conversations = get_recent_conversations(logs_dir=logs_dir, max_files=5)
    summary = summarize_conversations(conversations)
    print("Summary of Conversations:\n", summary)
    # Save the summary to a file in the current directory or a specified path
    summary_filename = "conversation_sum.txt" 
    with open(summary_filename, 'w') as file:
        file.write(summary)
    print(f"Summary saved to {summary_filename}")

if __name__ == "__main__":
    main()

