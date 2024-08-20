# Test task for 4ops

DevOps Task Evaluation

## Task 1: Quick Setup and Configuration

I used the following command to connect to the server 
```bash
ssh ubuntu@95.216.93.1 -p 50006
```

## Configuration super user 
Create a new user
```bash
sudo adduser devops_user
```
Add the user to the sudo group 
```bash
sudo usermod -aG sudo devops_user
```
log in as a devops_user 
```bash
su - devops_user
```
Then verify that the user can use sudo by running the command 
```bash
sudo whoami
```
To verify that we have a sudo user, we can use command below
```bash
groups devops_user
```


## Task 2: Ansible and Docker Deployment

Install ansible and update && upgrade cache/packages

```bash
sudo apt update
sudo apt upgrade
```

Install ansible from oficial page - https://docs.ansible.com/ansible/latest/installation_guide/installation_distros.html#installing-ansible-on-ubuntu
```bash
$ UBUNTU_CODENAME=jammy
$ wget -O- "https://keyserver.ubuntu.com/pks/lookup?fingerprint=on&op=get&search=0x6125E2A8C77F2818FB7BD15B93C4A3FD7BB9C367" | sudo gpg --dearmour -o /usr/share/keyrings/ansible-archive-keyring.gpg
$ echo "deb [signed-by=/usr/share/keyrings/ansible-archive-keyring.gpg] http://ppa.launchpad.net/ansible/ansible/ubuntu $UBUNTU_CODENAME main" | sudo tee /etc/apt/sources.list.d/ansible.list
$ sudo apt update && sudo apt install ansible
```

Make sure we have successfully installed ansible 
```bash
ansible --version
```

Playbook Creation:

```yaml
---
- name: Install Docker and Docker Compose with the nginx server
  hosts: all
  become: yes
  remote_user: devops_user
  vars:
    arch_mapping:  # Map ansible architecture {{ ansible_architecture }} names to Docker's architecture names
      x86_64: amd64
      aarch64: arm64
    http_port: 80
    https_port: 443

  tasks:
    - name: Update and upgrade all packages to the latest version
      ansible.builtin.apt:
        update_cache: true
        upgrade: dist
        cache_valid_time: 3600

    - name: Install required packages
      ansible.builtin.apt:
        pkg:
          - apt-transport-https
          - ca-certificates
          - curl
          - gnupg
          - software-properties-common

    - name: Create directory for Docker's GPG key
      ansible.builtin.file:
        path: /etc/apt/keyrings
        state: directory
        mode: '0755'

    - name: Add Docker's official GPG key
      ansible.builtin.apt_key:
        url: https://download.docker.com/linux/ubuntu/gpg
        keyring: /etc/apt/keyrings/docker.gpg
        state: present

    - name: Print architecture variables
      ansible.builtin.debug:
        msg: "Architecture: {{ ansible_architecture }}, Codename: {{ ansible_lsb.codename }}"

    - name: Add Docker repository
      ansible.builtin.apt_repository:
        repo: >-
          deb [arch={{ arch_mapping[ansible_architecture] | default(ansible_architecture) }}
          signed-by=/etc/apt/keyrings/docker.gpg]
          https://download.docker.com/linux/ubuntu {{ ansible_lsb.codename }} stable
        filename: docker
        state: present

    - name: Install Docker and related packages
      ansible.builtin.apt:
        name: "{{ item }}"
        state: present
        update_cache: true
      loop:
        - docker-ce
        - docker-ce-cli
        - containerd.io
        - docker-buildx-plugin
        - docker-compose-plugin
    
    - name: Enable and start Docker services
      ansible.builtin.systemd:
        name: "{{ item }}"
        enabled: true
        state: started
      loop:
        - docker.service
        - containerd.service 
    
    - name: Install docker-compose
      ansible.builtin.get_url:
        url: https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64
        dest: /usr/local/bin/docker-compose
        mode: '0755'
        force: yes

    - name: Create Docker Compose directory
      ansible.builtin.file:
        path: /opt/nginx
        state: directory
        mode: '0755'

    - name: Create Docker Compose file
      ansible.builtin.copy:
        dest: /opt/nginx/docker-compose.yml
        content: |
          version: '3.8'
          services:
            nginx:
              image: nginx:latest
              ports:
                - "{{ http_port }}:80"
                - "{{ https_port }}:443"

    - name: Start Nginx container with Docker Compose
      ansible.builtin.command:
        cmd: docker-compose up -d
        chdir: /opt/nginx
      register: docker_compose_result
      ignore_errors: yes

    - name: Install UFW 
      ansible.builtin.apt:
        name: ufw
        state: present

    - name: Allow HTTP and HTTPS ports through the firewall
      ansible.builtin.ufw:
        rule: allow
        port: "{{ item }}"
      loop:
        - "{{ http_port }}"
        - "{{ https_port }}"

    - name: Enable UFW
      ansible.builtin.ufw:
        state: enabled
        policy: allow

    - name: Update apt cache
      ansible.builtin.apt:
        update_cache: yes

    - name: Install pip for python3
      ansible.builtin.apt:
        name: python3-pip
        state: present
        update_cache: yes
        
    - name: Upgrade pip to the latest version
      ansible.builtin.pip:
        name: pip
        state: latest
        executable: /usr/bin/pip3
  
    - name: Upgrade psutil module using pip
      ansible.builtin.command:
        cmd: sudo pip install --upgrade psutil

    - name: Ensure the Python script is executable
      ansible.builtin.file:
        path: script_cpu_usage.py
        mode: '0755'

    - name: Schedule CPU usage logging script
      ansible.builtin.cron:
        name: "Log CPU usage"
        minute: "*/5"
        job: "/usr/bin/python3 /home/devops_user/ansible-playbook/script_cpu_usage.py"
        user: devops_user
      become: yes
```

## Task 3: Basic Monitoring with Python
 
To do this task i used next modules: 
1.psutil
2.datetime

```python
#!/usr/bin/env python3

import psutil
import datetime

cpu_usage = psutil.cpu_percent(interval=1)
ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

with open('/var/log/cpu_usage.log', 'a') as log:
    log.write(f'{ts} - CPU Usage: {cpu_usage}%\n')
```

## 4 Task 

1. To run ansible playbook we can use command below
```bash
ansible-playbook -i hosts.ini playbook.yml
```
2. To verify that nginx is running correctly we can run the following command 

```bash
curl http://localhost
```
and after that we will see following output, which tell us that nginx is working correctly
```html
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

## What is python script does 

#### Scheduling the Python Script

The Python script `script_cpu_usage.py` is scheduled to run every 5 minutes using a cron job. Cron is a time-based job scheduler in Unix-like operating systems that allows tasks to be executed at specified intervals.

The Python script script_cpu_usage.py is responsible for monitoring and logging the CPU usage of the system. It performs the following tasks:

    Collect CPU Usage Data: The script gathers information about the current CPU usage.
    Log Data: It writes the collected data to /var/log/cpu_usage.log, which can be reviewed later to analyze CPU performance trends over time.
    
