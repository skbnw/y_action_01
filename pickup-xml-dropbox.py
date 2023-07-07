import dropbox
import os
from datetime import datetime
import time
import requests

# Dropbox APIのアプリキーとアプリシークレットキー
app_key = 'qmfb5lhstinll9m'
app_secret = 'rogbxz9u608bmjk'

# OAuth2フローを開始
auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(app_key, app_secret, token_access_type='offline')
authorize_url = auth_flow.start()

# アクセスコード（認証コード）を変数として扱う
auth_code = 'TmVaZaXVHl4AAAAAAARvQtQm83Y9w_AO2Ot9Nei6VY0'

# アクセスコードを使用してアクセストークンとリフレッシュトークンを取得
oauth_result = auth_flow.finish(auth_code)
access_token = oauth_result.access_token
refresh_token = oauth_result.refresh_token

# Dropboxへの接続
dbx = dropbox.Dropbox(access_token)

# フォルダ名
folder_name = 'xml-files'

# フォルダが存在しない場合は作成
def create_folder_if_not_exists(folder_name):
    try:
        dbx.files_create_folder_v2('/' + folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except dropbox.exceptions.ApiError as e:
        if e.error.is_path() and e.error.get_path().is_conflict():
            print(f"Folder '{folder_name}' already exists.")
        else:
            print(f"Failed to create folder '{folder_name}': {e}")

# フォルダの作成
create_folder_if_not_exists(folder_name)

# XMLファイルをアップロード
def upload_file(file_path, file_name, folder_name):
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        dbx.files_upload(file_data, '/' + folder_name + '/' + file_name)
        print(f"File '{file_name}' uploaded successfully.")
    except dropbox.exceptions.ApiError as e:
        print(f"Failed to upload file '{file_name}': {e}")

# XMLファイルの取得とアップロード
def fetch_and_upload_xml_files():
    current_time = datetime.now().strftime('%Y%m%d_%H%M')
    xml_directory = 'xml-files'
    os.makedirs(xml_directory, exist_ok=True)
    
    rss_feeds = [
        ('top-picks', 'https://news.yahoo.co.jp/rss/topics/top-picks.xml'),
        ('domestic', 'https://news.yahoo.co.jp/rss/topics/domestic.xml'),
        ('world', 'https://news.yahoo.co.jp/rss/topics/world.xml'),
        ('business', 'https://news.yahoo.co.jp/rss/topics/business.xml'),
        ('entertainment', 'https://news.yahoo.co.jp/rss/topics/entertainment.xml'),
        ('sports', 'https://news.yahoo.co.jp/rss/topics/sports.xml'),
        ('it', 'https://news.yahoo.co.jp/rss/topics/it.xml'),
        ('local', 'https://news.yahoo.co.jp/rss/topics/local.xml'),
        ('science', 'https://news.yahoo.co.jp/rss/topics/science.xml')
    ]

    for feed_name, feed_url in rss_feeds:
        xml_file = f'{xml_directory}/{feed_name}_{current_time}.xml'
        response = requests.get(feed_url)
        if response.status_code == 200:
            with open(xml_file, 'wb') as f:
                f.write(response.content)
            if os.path.isfile(xml_file):
                upload_file(xml_file, os.path.basename(xml_file), folder_name)
            else:
                print(f"File '{xml_file}' does not exist.")
        else:
            print(f"Failed to download XML file from {feed_url}")
        time.sleep(3)

# XMLファイルの取得とアップロードを実行
try:
    fetch_and_upload_xml_files()
except dropbox.exceptions.AuthError:
    # アクセストークンのリフレッシュ
    oauth_result = auth_flow.finish(None, refresh_token=refresh_token)
    access_token = oauth_result.access_token
    dbx = dropbox.Dropbox(access_token)
    fetch_and_upload_xml_files()
