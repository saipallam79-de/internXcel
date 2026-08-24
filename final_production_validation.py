import requests, uuid
base='http://127.0.0.1:8000'
A_name='User A Final'; A_email=f'user_a_{uuid.uuid4().hex[:8]}@example.com'
B_name='User B Final'; B_email=f'user_b_{uuid.uuid4().hex[:8]}@example.com'
A_reg=requests.post(f'{base}/api/auth/register', json={'full_name':A_name,'email':A_email,'mobile':'+91 9000000001','college':'College A','degree':'B.Tech','branch':'CSE','year':2026,'password':'Pass1234!','domain_id':1}, timeout=10)
B_reg=requests.post(f'{base}/api/auth/register', json={'full_name':B_name,'email':B_email,'mobile':'+91 9000000001','college':'College B','degree':'B.Tech','branch':'IT','year':2026,'password':'Pass1234!','domain_id':2}, timeout=10)
print('A_REGISTER', A_reg.status_code, A_reg.json().get('access_token','')[:12])
print('B_REGISTER', B_reg.status_code, B_reg.json().get('access_token','')[:12])
A_tok=A_reg.json()['access_token']; B_tok=B_reg.json()['access_token']
A_me=requests.get(f'{base}/api/auth/me', headers={'Authorization':'Bearer '+A_tok}, timeout=10)
B_me=requests.get(f'{base}/api/auth/me', headers={'Authorization':'Bearer '+B_tok}, timeout=10)
print('A_ME', A_me.status_code, A_me.json()['full_name'])
print('B_ME', B_me.status_code, B_me.json()['full_name'])
assert A_me.json()['full_name']==A_name
assert B_me.json()['full_name']==B_name
A_summary=requests.get(f'{base}/api/dashboard/summary', headers={'Authorization':'Bearer '+A_tok}, timeout=10)
B_summary=requests.get(f'{base}/api/dashboard/summary', headers={'Authorization':'Bearer '+B_tok}, timeout=10)
print('A_SUMMARY', A_summary.status_code, A_summary.json()['student']['name'])
print('B_SUMMARY', B_summary.status_code, B_summary.json()['student']['name'])
assert A_summary.json()['student']['name']==A_name
assert B_summary.json()['student']['name']==B_name
A_tasks=requests.get(f'{base}/api/tasks', headers={'Authorization':'Bearer '+A_tok}, timeout=10).json()
print('A_TASKS', [(t['module_number'], t['module_title'], t['module_status']) for t in A_tasks[:5]])
assert any(t['module_number']==0 and t['module_status']=='available' for t in A_tasks)
assert any(t['module_number']==1 and t['module_status']=='locked' for t in A_tasks)
onboard=next(t for t in A_tasks if t['module_number']==0)
sub=requests.post(f'{base}/api/tasks/{onboard["id"]}/submit', headers={'Authorization':'Bearer '+A_tok}, json={'linkedin_url':'https://linkedin.com/posts/user-a'}, timeout=10)
print('A_SUBMIT', sub.status_code, sub.json()['status'])
admin=requests.post(f'{base}/api/auth/login', json={'email':'admin@internxcel.dev','password':'admin123'}, timeout=10)
admin_tok=admin.json()['access_token']
subs=requests.get(f'{base}/api/admin/submissions', headers={'Authorization':'Bearer '+admin_tok}, timeout=10).json()
review=requests.patch(f"{base}/api/admin/submissions/{subs[0]['id']}/review", headers={'Authorization':'Bearer '+admin_tok,'Content-Type':'application/json'}, json={'status':'approved','admin_comment':'Approved'}, timeout=10)
print('REVIEW', review.status_code, review.json()['status'])
A_path=requests.get(f'{base}/api/modules/learning-path/{A_summary.json()["internship"]["id"]}', headers={'Authorization':'Bearer '+A_tok}, timeout=10).json()
print('A_PATH', [(m['module_number'], m['title'], m['status']) for m in A_path[:4]])
assert A_path[0]['status']=='completed'
assert A_path[1]['status']=='available'
assert A_path[2]['status']=='locked'
print('FINAL_TWO_USER_PRODUCTION_VALIDATION_OK')
