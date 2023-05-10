import boto3
import sources.Controllers.config as cfg

# Amazon Rekognition config
COLLECTION_ID = cfg.COLLECTION_ID
ACCESS_KEY_ID = cfg.ACCESS_KEY_ID
SECRET_ACCESS_ID = cfg.SECRET_ACCESS_ID


def create_boto_client(service_name):
    return boto3.client(service_name, aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=SECRET_ACCESS_ID,
                        region_name="ap-southeast-1")


def check_existed_face(image_path):
    client = create_boto_client('rekognition')

    with open(image_path, 'rb') as image_file:
        search_image = image_file.read()

    # Search for the face in the collection
    response = client.search_faces_by_image(
        CollectionId=COLLECTION_ID,
        FaceMatchThreshold=0.95,
        Image={'Bytes': search_image}
    )

    # Check the search results
    if len(response['FaceMatches']) > 0:
        return True
    else:
        return False


def add_face_to_collection(image_path):
    client = create_boto_client('rekognition')

    with open(image_path, 'rb') as image_file:
        search_image = image_file.read()

    # Search for the face in the collection
    response = client.index_faces(
        CollectionId=COLLECTION_ID,
        Image={'Bytes': search_image}
    )
    return response["FaceRecords"][0]["Face"]["FaceId"]
