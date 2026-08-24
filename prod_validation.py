import requests, uuid, json
base='http://127.0.0.1:8000'

def register(name, email, password='Pass1234!'):
    payload = {
        'full_name': name,
        'email': email,
        'mobile': '+91 9000000001',
        'college': 'Test Campus',
        'degree': 'B.Tech',
        'branch': 'CSE',
        'year': 2026,
        'password': password,
        'domain_id': 1,
    }
    r = requests.post(f'{base}/api/auth/register', json=payload, timeout=10)
    print(name, 'REGISTER', r.status_code, r.text[:150])
    assert r.status_code == 201, r.text
    return r.json()['access_token']

A_name='User A Prod'
A_email=f'user_a_{uuid.uuid4().hex[:8]}@example.com'
B_name='User B Prod'
B_email=f'user_b_{uuid.uuid4().hex[:8]}@example.com'
A_token=register(A_name, A_email)
B_token=register(B_name, B_email)

A_me=requests.get(f'{base}/api/auth/me', headers={'Authorization':'Bearer '+A_token}, timeout=10)
B_me=requests.get(f'{base}/api/auth/me', headers={'Authorization':'Bearer '+B_token}, timeout=10)
print('A_ME', A_me.status_code, A_me.json()['full_name'])
print('B_ME', B_me.status_code, B_me.json()['full_name'])

A_summary=requests.get(f'{base}/api/dashboard/summary', headers={'Authorization':'Bearer '+A_token}, timeout=10)
print('A_SUMMARY', A_summary.status_code, A_summary.text[:300])
# no internship yet, so 404 expected for summary, unless enrolled
assert A_summary.status_code == 404, A_summary.text

# enroll A and B to domains
A_enroll=requests.post(f'{base}/api/internships/apply', headers={'Authorization':'Bearer '+A_token}, json={'domain_id':1}, timeout=10)
B_enroll=requests.post(f'{base}/api/internships/apply', headers={'Authorization':'Bearer '+B_token}, json={'domain_id':2}, timeout=10)
print('A_ENROLL', A_enroll.status_code, A_enroll.text[:200])
print('B_ENROLL', B_enroll.status_code, B_enroll.text[:200])
A_dashboard=requests.get(f'{base}/api/dashboard/summary', headers={'Authorization':'Bearer '+A_token}, timeout=10)
B_dashboard=requests.get(f'{base}/api/dashboard/summary', headers={'Authorization':'Bearer '+B_token}, timeout=10)
print('A_DASHBOARD_NAME', A_dashboard.json()['student']['name'])
print('B_DASHBOARD_NAME', B_dashboard.json()['student']['name'])
assert A_dashboard.json()['student']['name'] == A_name
assert B_dashboard.json()['student']['name'] == B_name

# tasks before approval: prerequisite should be available, module 1 locked
A_tasks=requests.get(f'{base}/api/tasks', headers={'Authorization':'Bearer '+A_token}, timeout=10).json()
print('A_TASKS', [(t['module_number'], t['module_title'], t['module_status']) for t in A_tasks[:5]])
A_before = {item['module_number']: item['module_status'] for item in A_tasks}
assert A_before.get(0) == 'available'
assert A_before.get(1) == 'locked'

# submit prerequisite onboarding task
onboard = next(task for task in A_tasks if task['module_number']==0)
sub = requests.post(f'{base}/api/tasks/{onboard["id"]}/submit', headers={'Authorization':'Bearer '+A_token}, json={'linkedin_url':'https://linkedin.com/posts/user-a'}, timeout=10)
print('A_SUBMIT', sub.status_code, sub.json()['status'])
assert sub.status_code == 200

# admin approves the latest pending submission
admin_login = requests.post(f'{base}/api/auth/login', json={'email':'admin@internxcel.dev','password':'admin123'}, timeout=10)
admin_token = admin_login.json()['access_token']
subs = requests.get(f'{base}/api/admin/submissions', headers={'Authorization':'Bearer '+admin_token}, timeout=10).json()
print('SUBMISSIONS', len(subs), subs[0]['student'] if subs else 'none')
if subs:
    review = requests.patch(f"{base}/api/admin/submissions/{subs[0]['id']}/review", headers={'Authorization':'Bearer '+admin_token,'Content-Type':'application/json'}, json={'status':'approved','admin_comment':'Approved'}, timeout=10)
    print('REVIEW', review.status_code, review.json()['status'])
    assert review.status_code == 200

A_path=requests.get(f'{base}/api/modules/learning-path/{A_enroll.json()["id"]}', headers={'Authorization':'Bearer '+A_token}, timeout=10).json()
print('A_PATH', [(m['module_number'], m['title'], m['status']) for m in A_path[:4]])
assert A_path[0]['status'] == 'completed'
assert A_path[1]['status'] == 'available'
assert A_path[2]['status'] == 'locked'

B_path=requests.get(f'{base}/api/modules/learning-path/{B_enroll.json()["id"]}', headers={'Authorization':'Bearer '+B_token}, timeout=10).json()
print('B_PATH', [(m['module_number'], m['title'], m['status']) for m in B_path[:4]])
assert B_path[0]['status'] == 'available' or B_path[0]['status']=='completed'
print('ALL_ISOLATED_AND_UNLOCK_VALIDATED')
