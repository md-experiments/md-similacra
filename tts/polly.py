from botocore.exceptions import BotoCoreError, ClientError
import boto3
import sys
import yaml, os

def get_keys(file_key = 'aws_key.yaml'):
    # Looks for credentials in local file
    if os.path.exists(file_key):
        secrets_dict = yaml.load(open(file_key,'r'), Loader=yaml.FullLoader)
        AWS_ACCESS_KEY = secrets_dict['AWS_ACCESS_KEY']
        AWS_SECRET_KEY = secrets_dict['AWS_SECRET_KEY']        
    # Looks for credentials as environment variables (recommended)
    else:
        AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
        AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
    return AWS_ACCESS_KEY, AWS_SECRET_KEY

def create_tts_polly(text, save_to_path, voice = 'Bella', api_key_path ='../aws_key.yaml', output_format = "mp3"):
    ACCESS_KEY, SECRET_KEY = get_keys(file_key = api_key_path)
    polly = boto3.client("polly", region_name = 'us-west-2', 
        aws_access_key_id = ACCESS_KEY,
        aws_secret_access_key = SECRET_KEY)

    try:
        # Request speech synthesis
        response = polly.synthesize_speech(Text=text, OutputFormat=output_format,
                                            VoiceId=voice)
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    from contextlib import closing

    with closing(response["AudioStream"]) as stream:
        with closing(response["AudioStream"]) as stream:
            assert(save_to_path.endswith(output_format))
            try:
                # Open a file for writing the output as a binary stream
                with open(save_to_path, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)
