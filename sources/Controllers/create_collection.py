from sources.Controllers.rekognition import create_boto_client

client = create_boto_client('rekognition')

response = client.create_collection(
    CollectionId='FaceDBSmartLock')

print(response)
