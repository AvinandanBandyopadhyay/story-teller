import json
import boto3
import base64

s3 = boto3.client("s3")
polly = boto3.client("polly")


bucketName = "experimental-repo-aviband"
storyKey = "story/audio/audio{0}"


def create_audio(text, keyInx):
    response = polly.start_speech_synthesis_task(Text=text, OutputFormat="mp3",
                    VoiceId="Joanna", Engine='neural',
                    OutputS3BucketName=bucketName, 
                    OutputS3KeyPrefix=storyKey.format(keyInx))
    taskId = response['SynthesisTask']['TaskId']
    return taskId

def createAudioFromStory():
    storyKeyInx = 1
    taskIds = []
    fPtr = open("story.txt", "r")
    storyName = fPtr.readline()
    print(storyName)
    taskId = create_audio(storyName, storyKeyInx)
    taskIds.append(taskId)
    storyKeyInx = storyKeyInx + 1
    
    story = fPtr.read()

    stmts = story.split(".")
    for stmt in stmts:
        stmt = stmt.strip()
        print(stmt)
        audioStream = create_audio(stmt, storyKeyInx)
        storyKeyInx = storyKeyInx + 1

    fPtr.close()
    
createAudioFromStory()