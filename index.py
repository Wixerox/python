import requests
import json

# تابع برای ارسال درخواست و دریافت پاسخ
def send_request(url, params):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=params, headers=headers, timeout=60)

    if response.status_code != 200:
        return {'success': False, 'error': response.text}
    else:
        return {'success': True, 'response': response.text}

# تابع برای پردازش داده‌های دریافتی از dmviewer.php و تبدیل به JSON
def process_dm_viewer(response):
    lines = response.split("<br>")
    data = []

    for line in lines:
        fields = line.split(":SBNT:")
        if len(fields) > 1:
            record = {
                "id": fields[0],
                "sender": fields[1],
                "baraye": fields[2],
                "text": fields[3] if len(fields) > 3 else None,
                "riply": fields[4] if len(fields) > 4 else None,
                "time": fields[5] if len(fields) > 5 else None,
                "nemidonam": fields[6] if len(fields) > 6 else None,
                "etelayi_nadaram": fields[7] if len(fields) > 7 else None
            }
            data.append(record)

    json_output = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_output)

    return data

# اولین URL
url_1 = "https://app.sibnote.ir/dmlist.php"
params_1 = {
    "sender": "palermutweet",
    "paaas": "palermutweet",
    "lim": 24
}

data_1 = send_request(url_1, params_1)
if data_1['success']:
    lines_1 = data_1['response'].split("<br>")
    data_1 = []

    for line in lines_1:
        fields = line.split(":SBNT:")
        if len(fields) > 1:
            record = {
                "id": fields[0],
                "user": fields[1],
                "name": fields[2],
                "tick": fields[3] if len(fields) > 3 else None,
                "text": fields[4] if len(fields) > 4 else None,
                "riply": fields[5] if len(fields) > 5 else None,
                "image": fields[6] if len(fields) > 6 else None,
                "time": fields[7] if len(fields) > 7 else None,
                "sender": fields[8] if len(fields) > 8 else None,
                "time_posted": fields[9] if len(fields) > 9 else None
            }
            data_1.append(record)

    json_output_1 = json.dumps(data_1, indent=4, ensure_ascii=False)
    print(json_output_1)

    for record in data_1:
        if record.get('text') and record['text'].startswith('-'):
            sender = record['user']
            break

    # دریافت لیست فالوورها
    url_followers = "https://app.sibnote.ir/myfollowers.php"
    params_followers = {
        "karbar": "algorithm",
        "user": "palermutweet"
    }

    data_followers = send_request(url_followers, params_followers)
    if data_followers['success']:
        lines_followers = data_followers['response'].split("<br>")
        followers_data = []

        for line in lines_followers:
            fields = line.split(":SBNT:")
            if len(fields) > 1:
                record = {
                    "id": fields[0],
                    "user": fields[1],
                    "nomidonam": fields[2],
                    "image": fields[3] if len(fields) > 3 else None,
                    "ha": fields[4] if len(fields) > 4 else None,
                    "etelayi_nadaram": fields[5] if len(fields) > 5 else None
                }
                followers_data.append(record)

        list_user = [record['user'] for record in followers_data]

        if sender in list_user:
            # دومین URL
            url_2 = "https://app.sibnote.ir/dmviewer.php"
            params_2 = {
                "sender": "palermutweet",
                "paaas": "palermutweet",
                "deliver": sender,
                "lim": 0
            }

            data_2 = send_request(url_2, params_2)
            if data_2['success']:
                data_2_processed = process_dm_viewer(data_2['response'])

                # دریافت آخرین متنی که با - شروع می‌شود
                tex = ''
                for record in reversed(data_2_processed):
                    if record.get('text') and record['text'].startswith('-'):
                        tex = record['text']
                        break

                # ارسال به API CHAT
                chat_url = "https://api-free.ir/api/chat.php?text=" + requests.utils.quote(tex)
                result_response = requests.get(chat_url)
                result_data = result_response.json()

                pasokh = result_data.get('result', '')

                send_url = "https://app.sibnote.ir/dmsending.php"
                send_params = {
                    "sender": "palermutweet",
                    "paaas": "palermutweet",
                    "deliver": sender,
                    "reply": "non",
                    "text": pasokh
                }

                send_result = send_request(send_url, send_params)
                if send_result['success']:
                    print(send_result['response'])
                else:
                    print("خطا در ارسال پیام:", send_result['error'])
            else:
                print("خطا در درخواست به لینک دوم:", data_2['error'])
        else:
            # ارسال پیام عدم فالو
            send_url = "https://app.sibnote.ir/dmsending.php"
            send_params = {
                "sender": "palermutweet",
                "paaas": "palermutweet",
                "deliver": sender,
                "reply": "non",
                "text": "شما @algorithm را فالو ندارید! برای ادامه این صفحه را فالو کرده و سپس دوباره پیام خود را بفرستید."
            }

            send_result = send_request(send_url, send_params)
            if send_result['success']:
                print(send_result['response'])
            else:
                print("خطا در ارسال پیام:", send_result['error'])
    else:
        print("خطا در درخواست به لینک myfollowers:", data_followers['error'])
else:
    print("خطا در درخواست به لینک dmlist:", data_1['error'])