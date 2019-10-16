import json
import boto3
import os
 
# 環境変数を読み込む
TAG_KEY = os.environ['TAG_KEY']
TAG_VALUE = os.environ['TAG_VALUE']
 
 
def lambda_handler(event, context):
    # SageMakerが対応してるリージョン一覧を取得
    regions = boto3.Session().get_available_regions('sagemaker')
 
    # リージョンごとに実行
    for region in regions:
        sm = boto3.client('sagemaker', region_name=region)
 
        # 起動中(InService)のインスタンスを取得する
        nb_list = sm.list_notebook_instances(
            StatusEquals='InService'
        )['NotebookInstances']
 
        for nb in nb_list:
            tags = sm.list_tags(ResourceArn=nb['NotebookInstanceArn'])['Tags']
 
            for tag in tags:
                if tag['Key'] == "auto_stop" and tag['Value'] == "false":
                    pass
                else:
                    # すべてのインスタンスは強制停止
                    nb_name = nb['NotebookInstanceName']
                    print('stop', nb_name+'@'+region)
                    stop_notebook_instance(nb_name, sm)
 
    return {
        'statusCode': 200,
        'body': json.dumps('done')
    }
 
 
 
def stop_notebook_instance(nb_name, sm_client):
    # 指定されたノートブックインスタンスを停止する
 
    sm_client.stop_notebook_instance(
        NotebookInstanceName=nb_name
    )
