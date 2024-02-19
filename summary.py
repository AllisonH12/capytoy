from datetime import datetime
import glob
import os
from openai import OpenAI

def get_conversation_chunks(logs_dir="logs", max_files=500, chunk_size=30000):
    log_files = glob.glob(f"{logs_dir}/conversation_history_*.txt")
    sorted_files = sorted(log_files, key=lambda x: os.path.getmtime(x), reverse=True)
    chunks = []
    current_chunk = ""
    
    for file_path in sorted_files[:max_files]:
        if os.path.getsize(file_path) < 100:
            continue
        
        with open(file_path, 'r') as file:
            file_content = file.read()
            filtered_content = '\n'.join([line for line in file_content.split('\n') if line.strip()])
            
            # Check if adding this content exceeds chunk size
            if len(current_chunk) + len(filtered_content) > chunk_size:
                chunks.append(current_chunk)
                current_chunk = filtered_content + "\n\n"
            else:
                current_chunk += filtered_content + "\n\n"
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.rstrip("\n"))
    
    return chunks



def summarize_conversations(conversations):
    client = OpenAI()
    prompt = (
        "Read the following conversations and summarize key details about the conversation partner, "
        "including their names, interests, speaking style, any mentioned fun facts such as pet names, "
        "family members and friends, their concerns, and their level of understanding:\n\n" + conversations
    )

    response = client.chat.completions.create(
      #model="gpt-4",
      #model="gpt-4-turbo-preview",
      model="gpt-3.5-turbo",
      #model="gpt-3.5-turbo-0125",
      messages=[
        {
          "role": "system",
          "content": "you are a summarizer, trying to understand the user, extract facts that is helpful to understand the user. "
        },
        {
          "role": "user",
          "content": "Read the following conversations and summarize key details about the conversation partner, \"\n        \"including their name, interests, speaking style, commone questions,  any mentioned fun facts such as pet names, \"\n        \"family members, who are the friends, their concerns, and their level of understanding, the most common things they did with this program \\n\\n\" \n    \n"
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

    #print(prompt)
    return  response.choices[0].message.content 

def main():
    logs_dir = "/home/pi/capytoy/logs"
    conversation_chunks = get_conversation_chunks(logs_dir=logs_dir, max_files=500, chunk_size=50000)
    
    all_summaries = ""
    for chunk in conversation_chunks:

        print(".")
        summary = summarize_conversations(chunk)  # Assume summarize_conversations can handle a single chunk
        all_summaries += summary + "\n\n"
    
    print("Summary of Conversations:\n", all_summaries)
    summary_filename = "conversation_sum.txt"
    with open(summary_filename, 'w') as file:
        file.write(all_summaries)
    print(f"Summary saved to {summary_filename}")    


if __name__ == "__main__":
    main()

