def create_format_instruction(schema):
    line_template = '\t"{name}": {type}  // {description}'


    schema_str = '\n'.join([line_template.format(
            name=s['name'], description=s['description'], type="string"
        ) for s in schema])


    STRUCTURED_FORMAT_INSTRUCTIONS = """The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`":

    ```json
    [
    {{
    {format}
    }},
    ...
    ]
    ```
    \n\n
    The output should be only the markdown code snippet, there should be no additional commentary, notes or explanations."""

    format_instruction = STRUCTURED_FORMAT_INSTRUCTIONS.format(format=schema_str)
    return format_instruction

def qry_openai_and_retry(openai, user_query, model = "gpt-3.5-turbo-0613", nr_attempts = 3):
    attempt = 0
    success = False
    while (attempt<nr_attempts) and (not success):
        try:
            response = openai.ChatCompletion.create(
                    model=model,

                    # This is the chat message from the user
                    messages=[{"role": "user", "content": user_query}],

                )
            success = True

        except Exception as e: 
            print("OpenAI Attempt",attempt)
            print(e)
            success = False
            attempt = attempt + 1
            response = {}
    return response