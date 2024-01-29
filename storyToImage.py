import json
import boto3
import base64

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime")

modelId="stability.stable-diffusion-xl-v1"
bucketName = "experimental-repo-aviband"
storyKey = "story/images/image{0}.png"


def putObject(image, keyInx):
    s3.put_object(Body=image, Bucket=bucketName, Key=storyKey.format(keyInx))
    

def create_image(text):
    body = {"text_prompts": [{"text": text}]}
    response = bedrock.invoke_model(body=json.dumps(body), modelId=modelId)
    response_body = json.loads(response["body"].read())
    finish_reason = response_body.get("artifacts")[0].get("finishReason")
    if finish_reason in ["ERROR", "CONTENT_FILTERED"]:
        raise Exception(f"Image error: {finish_reason}")
    base64_image = response_body.get("artifacts")[0]["base64"]
    base64_bytes = base64_image.encode("ascii")
    image_bytes = base64.b64decode(base64_bytes)
    return image_bytes

def createImgsFromStory():
    
    storyKeyInx = 1
    fPtr = open("story.txt", "r")
    storyName = fPtr.readline()
    print(storyName)

    imageInBtytes = create_image(storyName)
    putObject(imageInBtytes, storyKeyInx)
    storyKeyInx = storyKeyInx + 1

    story = fPtr.read()

    stmts = story.split(".")
    for stmt in stmts:
        stmt = stmt.strip()
        print(stmt)
        imageInBtytes = create_image(stmt)
        putObject(imageInBtytes, storyKeyInx)
        storyKeyInx = storyKeyInx + 1

    fPtr.close()
    
createImgsFromStory()




