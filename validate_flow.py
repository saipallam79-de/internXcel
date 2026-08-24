import requests, uuid
base='http://127.0.0.1:8000'
email=f'user_{uuid.uuid4().hex[:8]}@example.com'
student = requests.post(f'{base}/api/auth/register', json={
    'full_name':'Progress User',
    'email': email,
    'mobile': '+91 9000000001',
    'college': 'Test Campus',
    'degree': 'B.Tech',
    'branch': 'CSE',
    'year': 2026,
    'password': 'Pass1234!',
    'domain_id': 1,
}, timeout=10)
print('REGISTER', student.status_code)
student_token = student.json()['access_token']
all_tasks = requests.get(f'{base}/api/tasks', headers={'Authorization': 'Bearer ' + student_token}, timeout=10)
print('TASKS', len(all_tasks.json()))
for task in all_tasks.json():
    if task['module_number'] == 0:
        sub = requests.post(f"{base}/api/tasks/{task['id']}/submit", headers={'Authorization': 'Bearer ' + student_token}, json={'linkedin_url': 'https://linkedin.com/posts/test-user'}, timeout=10)
        print('SUBMIT', task['id'], sub.status_code, sub.json()['status'])
        break
admin_login = requests.post(f'{base}/api/auth/login', json={'email':'admin@internxcel.dev','password':'admin123'}, timeout=10)
admin_token = admin_login.json()['access_token']
subs = requests.get(f'{base}/api/admin/submissions', headers={'Authorization': 'Bearer ' + admin_token}, timeout=10).json()
review = requests.patch(f"{base}/api/admin/submissions/{subs[0]['id']}/review", headers={'Authorization': 'Bearer ' + admin_token, 'Content-Type': 'application/json'}, json={'status': 'approved', 'admin_comment': 'Approved for onboarding'}, timeout=10)
print('REVIEW', review.status_code, review.json()['status'])
internship = requests.get(f'{base}/api/internships/me', headers={'Authorization': 'Bearer ' + student_token}, timeout=10).json()
path = requests.get(f"{base}/api/modules/learning-path/{internship['id']}", headers={'Authorization': 'Bearer ' + student_token}, timeout=10).json()
print('PATH', [(item['module_number'], item['title'], item['status']) for item in path[:3]])
