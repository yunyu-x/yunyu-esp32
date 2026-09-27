import urllib.request
import urllib.parse
import time
import json

DEV_IP = "192.168.110.67"

def main():
    data = urllib.parse.urlencode({'text': '你好，介绍一下杭州西湖。'}).encode('utf-8')
    req = urllib.request.Request(f'http://{DEV_IP}/bailian/send_text', data=data, method='POST')
    print('Sending text query to StickS3...')
    resp = urllib.request.urlopen(req, timeout=4).read().decode('utf-8')
    print('Send result:', resp)

    for i in range(15):
        time.sleep(0.7)
        st = json.loads(urllib.request.urlopen(f'http://{DEV_IP}/bailian/status', timeout=2).read().decode('utf-8'))
        print(f'[{i*0.7:.1f}s] State={st.get("state_code")} ({st.get("state_name")}) | Reply="{st.get("ai_reply")}" | Err="{st.get("error")}"')
        if st.get('state_code') == 3 and len(st.get('ai_reply', '')) > 0:
            print('Voice turn completed successfully!')
            break

if __name__ == '__main__':
    main()
