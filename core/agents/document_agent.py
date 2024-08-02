import logging

logging.basicConfig(filename='../logging/extract-log.txt', level=logging.INFO)
logging.basicConfig(filename='../logging/extract-error-log.txt', level=logging.ERROR)


def planner_agent(prompt_template,output_format):
    import json 
    from openai import OpenAI
    import json

    client = OpenAI(api_key = 'sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b')

    chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type":"json_object"},
            messages=[
                {"role":"system","content":
                """You are a part of a team of language models. 
                   Your role is this team is a leader, meaning you give the other models instructions. 
                   You must Provide your output in valid JSON. 
                   The data schema should in this format: """ +
                 json.dumps(output_format)},

                {"role":"user","content":prompt_template}
                ]
            )
        
    finish_reason = chat_completion.choices[0].finish_reason
    data = chat_completion.choices[0].message.content
    output = json.loads(data)
    return output


class DocumentAgent:
    def __init__(self,config):
        self.config = config
        logging.info("Document Agent Initialised")



    def run():
        pass 



    